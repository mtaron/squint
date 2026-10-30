import json
from uuid import UUID

from temporalio.contrib.pydantic import pydantic_data_converter

from squint_core.models import CamelModel


class Example(CamelModel):
    document_id: UUID
    page_count: int | None = None


DOCUMENT_ID = UUID("0f8fad5b-d9cb-469f-a165-70867728950e")


def test_serializes_camel_case_through_the_temporal_converter():
    converter = pydantic_data_converter.payload_converter
    [payload] = converter.to_payloads([Example(document_id=DOCUMENT_ID, page_count=3)])

    assert json.loads(payload.data) == {"documentId": str(DOCUMENT_ID), "pageCount": 3}


def test_validates_camel_case_from_typescript():
    converter = pydantic_data_converter.payload_converter
    [payload] = converter.to_payloads([{"documentId": str(DOCUMENT_ID)}])

    [example] = converter.from_payloads([payload], [Example])

    assert example == Example(document_id=DOCUMENT_ID)
