import asyncio
import io

import asyncpg
from capo_s3 import AsyncS3Client
from capo_s3.errors import NoSuchBucket, NoSuchKey
from PIL import Image
from pymilvus import AsyncMilvusClient
from squint_core import documents
from squint_core.documents import document_deleted
from squint_core.embedding import (
    DELETE_DOCUMENT_VECTORS_ACTIVITY,
    DELETE_USER_VECTORS_ACTIVITY,
    EMBED_PAGES_ACTIVITY,
    ENCODE_QUERY_ACTIVITY,
    EmbedPagesInput,
    EncodedQuery,
)
from squint_vector import pages
from squint_vector.pages import PageVectors
from temporalio import activity

from encoder import Encoder


def decode_page(image: bytes, content_box: list[int] | None) -> Image.Image:
    """The page without its margins, which leaves more of NeoMME's resolution for the content.
    A blank page has no content box."""
    page = Image.open(io.BytesIO(image)).convert("RGB")
    if content_box is None:
        return page
    left, top, right, bottom = content_box
    return page.crop((left, top, right, bottom))


class EmbedActivities:
    def __init__(
        self,
        db: asyncpg.Pool,
        s3: AsyncS3Client,
        milvus: AsyncMilvusClient,
        encoder: Encoder,
    ) -> None:
        self.db = db
        self.s3 = s3
        self.milvus = milvus
        self.encoder = encoder

    async def read_page(
        self, input: EmbedPagesInput, page_number: int, content_box: list[int] | None
    ) -> Image.Image:
        key = documents.page_image_key(input.document_id, page_number)
        try:
            async with self.s3.get_object(input.bucket, key) as response:
                image = b"".join([chunk async for chunk in response["body"]])
        except (NoSuchKey, NoSuchBucket) as error:
            raise document_deleted() from error
        return await asyncio.to_thread(decode_page, image, content_box)

    @activity.defn(name=EMBED_PAGES_ACTIVITY)
    async def embed_pages(self, input: EmbedPagesInput) -> None:
        """Pages are recorded before they get here, so a missing row means a deleted document. The
        upsert is idempotent, so a retry after any step is safe."""
        content_boxes = await documents.content_boxes(
            self.db, input.document_id, input.page_numbers
        )
        if not content_boxes:
            raise document_deleted()

        page_numbers = sorted(content_boxes)
        images = await asyncio.gather(
            *(
                self.read_page(input, page_number, content_boxes[page_number])
                for page_number in page_numbers
            )
        )
        encoded = await self.encoder.encode_pages(list(images))
        await pages.upsert_pages(
            self.milvus,
            [
                PageVectors(
                    document_id=input.document_id,
                    user_id=str(input.user_id),
                    page_number=page_number,
                    dense=page.dense,
                    tokens=page.tokens,
                )
                for page_number, page in zip(page_numbers, encoded, strict=True)
            ],
        )

        marked = await documents.mark_pages_embedded(
            self.db, input.document_id, page_numbers
        )
        if not marked:
            raise document_deleted()

    @activity.defn(name=ENCODE_QUERY_ACTIVITY)
    async def encode_query(self, query: str) -> EncodedQuery:
        [encoded] = await asyncio.to_thread(self.encoder.encode_queries, [query])
        return EncodedQuery(
            dense=encoded.dense.tolist(), tokens=encoded.tokens.tolist()
        )

    @activity.defn(name=DELETE_DOCUMENT_VECTORS_ACTIVITY)
    async def delete_document_vectors(self, document_ids: list[str]) -> None:
        await pages.delete_documents(self.milvus, document_ids)

    @activity.defn(name=DELETE_USER_VECTORS_ACTIVITY)
    async def delete_user_vectors(self, user_id: str) -> None:
        await pages.delete_user(self.milvus, user_id)
