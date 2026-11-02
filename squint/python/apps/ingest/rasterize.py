"""Renders a PDF page into the image every later step uses, and measures what they need to know
about it. Embedding and extraction rescale this image rather than render the PDF again."""

import io
from math import ceil, floor

import numpy as np
import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c
from jdeskew.estimator import get_angle
from jdeskew.utility import rotate
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps
from pydantic import BaseModel, ConfigDict

# Removing a page's margins typically leaves 80% of its long side, which keeps the 2048 px NeoMME
# takes without upscaling
MAX_LONG_SIDE = 2560
POINTS_PER_INCH = 72
# Stops small pages from being blown up past the text sizes the models work well with
MAX_DPI = 300

SCAN_IMAGE_COVERAGE = 0.9
COVERAGE_GRID_SIZE = 100

# Below this, resampling softens the text more than the skew hurts it
MIN_SKEW_DEGREES = 0.25
# Above this, the estimate is more likely a diagonal design than a crooked scan
MAX_SKEW_DEGREES = 10

PROBE_LONG_SIDE = 512
# Anti-aliased edges fade to just under the background
INK_MARGIN = 5
# Paper texture and show-through vary more than anti-aliasing does
SCAN_INK_MARGIN = 40
SPECKLE_FILTER_SIZE = 3

PAGE_QUALITY = 95
KEEP_ALL_CHROMA = 0
THUMBNAIL_LONG_SIDE = 320


class RasterizedPage(BaseModel):
    model_config = ConfigDict(frozen=True)

    image: bytes
    thumbnail: bytes
    width: int
    height: int
    is_scan: bool
    skew_degrees: float | None
    content_box: list[int] | None


def render_page(page: pdfium.PdfPage) -> Image.Image:
    scale = min(MAX_LONG_SIDE / max(page.get_size()), MAX_DPI / POINTS_PER_INCH)
    return page.render(scale=scale, rev_byteorder=True).to_pil().convert("RGB")


def bounds_on_page(page_object: pdfium.PdfObject) -> tuple[float, float, float, float]:
    """Left, bottom, right and top in page coordinates. PDFium reports an object inside a form in
    the form's own coordinates."""
    bounds = page_object.get_bounds()
    container = page_object.container
    while container is not None:
        bounds = container.get_matrix().on_rect(*bounds)
        container = container.container
    return bounds


def image_coverage(page: pdfium.PdfPage) -> float:
    """The fraction of the page under images. Scanners often split a page into strips and layers,
    so the images are painted onto a mask rather than added up."""
    page_left, page_bottom, page_right, page_top = page.get_bbox()
    x_scale = COVERAGE_GRID_SIZE / (page_right - page_left)
    y_scale = COVERAGE_GRID_SIZE / (page_top - page_bottom)
    mask = Image.new("L", (COVERAGE_GRID_SIZE, COVERAGE_GRID_SIZE))
    draw = ImageDraw.Draw(mask)
    for image in page.get_objects(filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE]):
        left, bottom, right, top = bounds_on_page(image)
        first_column = round((left - page_left) * x_scale)
        first_row = round((page_top - top) * y_scale)
        end_column = round((right - page_left) * x_scale)
        end_row = round((page_top - bottom) * y_scale)
        # Rules and bullets are often tiny images that don't fill a single cell
        if end_column > first_column and end_row > first_row:
            draw.rectangle(
                (first_column, first_row, end_column - 1, end_row - 1), fill=1
            )
    _, covered = mask.histogram()[:2]
    return covered / COVERAGE_GRID_SIZE**2


def detected_angle(image: Image.Image) -> float:
    return get_angle(np.asarray(image.convert("L")))


def measure_skew(image: Image.Image) -> float | None:
    """The rotation that would straighten the page, if it's worth applying."""
    angle = detected_angle(image)
    return angle if MIN_SKEW_DEGREES <= abs(angle) <= MAX_SKEW_DEGREES else None


def grayscale_probe(image: Image.Image) -> Image.Image:
    return ImageOps.contain(
        image.convert("L"),
        (PROBE_LONG_SIDE, PROBE_LONG_SIDE),
        Image.Resampling.BOX,
    )


def most_common_level(grayscale: Image.Image) -> int:
    histogram = grayscale.histogram()
    return histogram.index(max(histogram))


def page_background(image: Image.Image) -> int:
    return most_common_level(grayscale_probe(image))


def straighten(image: Image.Image, angle: float) -> Image.Image:
    """Keeps the page's size, so the image still matches the PDF page."""
    background = page_background(image)
    rotated = rotate(
        np.asarray(image),
        angle,
        resize=False,
        border_value=(background, background, background),
    )
    return Image.fromarray(rotated)


def find_content_box(image: Image.Image, is_scan: bool) -> list[int] | None:
    """[left, top, right, bottom] around whatever stands out from the page's background, or None
    if nothing does. Works on a page of any color, since slides are often dark."""
    probe = grayscale_probe(image)
    if is_scan:
        probe = probe.filter(ImageFilter.MedianFilter(SPECKLE_FILTER_SIZE))
    margin = SCAN_INK_MARGIN if is_scan else INK_MARGIN
    background = Image.new("L", probe.size, most_common_level(probe))
    ink = ImageChops.difference(probe, background).point(
        lambda difference: 255 if difference > margin else 0
    )
    bounds = ink.getbbox()
    if bounds is None:
        return None

    # A probe pixel of padding, so faint edges aren't clipped
    left, top, right, bottom = bounds
    x_scale = image.width / probe.width
    y_scale = image.height / probe.height
    return [
        max(0, floor((left - 1) * x_scale)),
        max(0, floor((top - 1) * y_scale)),
        min(image.width, ceil((right + 1) * x_scale)),
        min(image.height, ceil((bottom + 1) * y_scale)),
    ]


def to_webp(image: Image.Image, **options) -> bytes:
    output = io.BytesIO()
    image.save(output, format="WEBP", **options)
    return output.getvalue()


def encode_page(image: Image.Image) -> bytes:
    """JPEG takes a seventh of the CPU time of WebP at this quality, which is worth its larger
    files. Keeping the chroma resolution keeps colored text sharp."""
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=PAGE_QUALITY, subsampling=KEEP_ALL_CHROMA)
    return output.getvalue()


def encode_thumbnail(image: Image.Image) -> bytes:
    thumbnail = ImageOps.contain(
        image,
        (THUMBNAIL_LONG_SIDE, THUMBNAIL_LONG_SIDE),
        Image.Resampling.LANCZOS,
    )
    return to_webp(thumbnail, quality=75, method=4)


def rasterize_page(page: pdfium.PdfPage) -> RasterizedPage:
    image = render_page(page)
    is_scan = image_coverage(page) >= SCAN_IMAGE_COVERAGE
    skew_degrees = measure_skew(image) if is_scan else None
    if skew_degrees is not None:
        image = straighten(image, skew_degrees)
    return RasterizedPage(
        image=encode_page(image),
        thumbnail=encode_thumbnail(image),
        width=image.width,
        height=image.height,
        is_scan=is_scan,
        skew_degrees=skew_degrees,
        content_box=find_content_box(image, is_scan),
    )
