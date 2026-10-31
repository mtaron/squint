import io
import random
from pathlib import Path

import pypdfium2 as pdfium
import pytest
from PIL import Image, ImageDraw
from PIL.JpegImagePlugin import JpegImageFile, get_sampling

import rasterize

LETTER = (612, 792)
SUBSAMPLING_444 = 0


def reopen(pdf: pdfium.PdfDocument, path: Path) -> pdfium.PdfDocument:
    """Parses the PDF from disk, the way an uploaded document is read."""
    pdf.save(path)
    pdf.close()
    return pdfium.PdfDocument(path)


def pdf_with_images(
    tiles: list[tuple[float, float, float, float]], size: tuple[int, int] = LETTER
) -> pdfium.PdfDocument:
    """A page holding an image at each (left, bottom, width, height)."""
    pdf = pdfium.PdfDocument.new()
    page = pdf.new_page(*size)
    for left, bottom, width, height in tiles:
        image = pdfium.PdfImage.new(pdf)
        image.set_bitmap(
            pdfium.PdfBitmap.from_pil(Image.new("RGB", (8, 8), "gray")),
        )
        image.set_matrix(
            pdfium.PdfMatrix().scale(width, height).translate(left, bottom)
        )
        page.insert_obj(image)
    page.gen_content()
    return pdf


def text_page(size: tuple[int, int] = (1275, 1650)) -> Image.Image:
    """Lines of word-sized dark bars on white, inside 150 px margins."""
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    words = random.Random(0)
    width, height = size
    for top in range(150, height - 170, 40):
        left = 150
        while left < width - 250:
            word = words.randrange(40, 130)
            draw.rectangle((left, top, left + word, top + 18), fill=(20, 20, 20))
            left += word + 16
    return image


def scanned_pdf(image: Image.Image, path: Path) -> pdfium.PdfDocument:
    image.save(path, "PDF", resolution=150)
    return pdfium.PdfDocument(path)


def test_renders_the_long_side_at_the_cap():
    pdf = pdf_with_images([], LETTER)

    image = rasterize.render_page(pdf[0])

    assert max(image.size) == 2560
    assert image.mode == "RGB"


def test_renders_small_pages_at_no_more_than_300_dpi():
    pdf = pdf_with_images([], (216, 360))

    image = rasterize.render_page(pdf[0])

    assert image.width == pytest.approx(900, abs=1)
    assert image.height == pytest.approx(1500, abs=1)


def test_coverage_is_zero_without_images():
    pdf = pdf_with_images([])

    assert rasterize.image_coverage(pdf[0]) == 0


def test_coverage_counts_overlapping_images_once():
    pdf = pdf_with_images([(0, 0, 612, 396), (0, 0, 612, 396), (0, 0, 306, 792)])

    assert rasterize.image_coverage(pdf[0]) == pytest.approx(0.75, abs=0.02)


def test_coverage_of_scanners_tiled_strips_is_nearly_full():
    pdf = pdf_with_images([(0, top, 612, 80) for top in range(0, 792, 79)])

    assert rasterize.image_coverage(pdf[0]) > 0.98


@pytest.mark.parametrize(
    "image",
    [(100, 400, 300, 0.5), (100, 100, 0.5, 300), (100, 100, 1, 1), (0, 0, 612, 1)],
    ids=["horizontal rule", "vertical rule", "bullet", "sliver at the edge"],
)
def test_images_too_small_to_fill_a_grid_cell_cover_nothing(
    image: tuple[float, float, float, float],
):
    pdf = pdf_with_images([image])

    assert rasterize.image_coverage(pdf[0]) == 0


def test_coverage_is_measured_on_the_page_for_an_image_inside_a_form(tmp_path: Path):
    source = pdf_with_images([(0, 0, 612, 792)])
    target = pdfium.PdfDocument.new()
    page = target.new_page(*LETTER)
    form = source.page_as_xobject(0, target).as_pageobject()
    form.set_matrix(pdfium.PdfMatrix().scale(0.5, 0.5).translate(306, 396))
    page.insert_obj(form)
    page.gen_content()
    page.close()

    reopened = reopen(target, tmp_path / "form.pdf")

    assert rasterize.image_coverage(reopened[0]) == pytest.approx(0.25, abs=0.02)


@pytest.mark.parametrize("skew", [-3.0, 1.2, 6.0])
def test_straightening_undoes_a_known_skew(skew: float):
    skewed = text_page().rotate(skew, Image.Resampling.BICUBIC, fillcolor="white")

    angle = rasterize.measure_skew(skewed)

    assert angle is not None
    straightened = rasterize.straighten(skewed, angle)
    remaining = rasterize.detected_angle(straightened)
    assert abs(remaining) < 0.2


def test_ignores_skew_too_small_to_be_worth_resampling():
    skewed = text_page().rotate(0.1, Image.Resampling.BICUBIC, fillcolor="white")

    assert rasterize.measure_skew(skewed) is None


def test_ignores_implausibly_large_skew():
    skewed = text_page().rotate(13, Image.Resampling.BICUBIC, fillcolor="white")

    assert rasterize.measure_skew(skewed) is None


def test_straightening_keeps_the_size_and_fills_corners_with_the_background():
    paper = (240, 238, 232)
    image = text_page()
    image.paste(paper, (0, 0, image.width, 140))
    image.paste(paper, (0, image.height - 140, image.width, image.height))
    image.paste(paper, (0, 0, 140, image.height))
    image.paste(paper, (image.width - 140, 0, image.width, image.height))

    straightened = rasterize.straighten(image, 5)

    assert straightened.size == image.size
    corner = straightened.convert("L").getpixel((1, 1))
    assert corner == pytest.approx(rasterize.page_background(image), abs=2)


def test_content_box_surrounds_the_ink():
    image = Image.new("RGB", (1000, 2000), "white")
    ImageDraw.Draw(image).rectangle((200, 400, 799, 1599), fill="black")

    box = rasterize.find_content_box(image, is_scan=False)

    assert box is not None
    left, top, right, bottom = box
    assert left == pytest.approx(200, abs=8)
    assert top == pytest.approx(400, abs=8)
    assert right == pytest.approx(800, abs=8)
    assert bottom == pytest.approx(1600, abs=8)
    assert left <= 200 and top <= 400 and right >= 800 and bottom >= 1600


def test_content_box_stays_inside_the_image():
    image = Image.new("RGB", (500, 500), "black")
    ImageDraw.Draw(image).rectangle((0, 0, 499, 250), fill="white")

    assert rasterize.find_content_box(image, is_scan=False) == [0, 250, 500, 500]


def test_a_white_page_has_no_content_box():
    image = Image.new("RGB", (1000, 2000), "white")

    assert rasterize.find_content_box(image, is_scan=False) is None


def test_a_page_of_blank_paper_has_no_content_box():
    noise = Image.effect_noise((1000, 1300), 6).convert("RGB")
    paper = Image.blend(Image.new("RGB", (1000, 1300), (236, 234, 230)), noise, 0.15)

    assert rasterize.find_content_box(paper, is_scan=True) is None


def test_finds_ink_on_scanned_paper():
    image = Image.new("RGB", (1000, 1300), (236, 234, 230))
    ImageDraw.Draw(image).rectangle((300, 300, 700, 900), fill=(40, 40, 40))

    box = rasterize.find_content_box(image, is_scan=True)

    assert box is not None
    assert box[0] == pytest.approx(300, abs=12)
    assert box[3] == pytest.approx(900, abs=12)


def test_finds_light_content_on_a_dark_page():
    image = Image.new("RGB", (1000, 1000), (20, 20, 40))
    ImageDraw.Draw(image).rectangle((400, 400, 600, 600), fill="white")

    box = rasterize.find_content_box(image, is_scan=False)

    assert box is not None
    assert box[0] == pytest.approx(400, abs=8)


def decode(encoded: bytes) -> Image.Image:
    return Image.open(io.BytesIO(encoded))


def test_pages_are_jpegs_of_the_same_size():
    image = text_page()

    jpeg = decode(rasterize.encode_page(image))

    assert jpeg.format == "JPEG"
    assert jpeg.size == image.size


def test_pages_keep_full_color_resolution():
    jpeg = decode(rasterize.encode_page(text_page()))

    assert isinstance(jpeg, JpegImageFile)
    assert get_sampling(jpeg) == SUBSAMPLING_444


def test_thumbnails_fit_the_long_side():
    thumbnail = decode(rasterize.encode_thumbnail(text_page()))

    assert thumbnail.format == "WEBP"
    assert thumbnail.size == (247, 320)


def test_rasterizes_a_skewed_scan_end_to_end(tmp_path: Path):
    scan = text_page().rotate(2.5, Image.Resampling.BICUBIC, fillcolor="white")
    pdf = scanned_pdf(scan, tmp_path / "scan.pdf")

    page = rasterize.rasterize_page(pdf[0])

    assert page.is_scan
    assert page.skew_degrees is not None
    assert abs(page.skew_degrees) == pytest.approx(2.5, abs=0.2)
    assert decode(page.image).size == (page.width, page.height)
    assert page.content_box is not None


def test_rasterizes_a_born_digital_page_without_skew_measurement(tmp_path: Path):
    pdf = pdf_with_images([(100, 100, 100, 100)])

    page = rasterize.rasterize_page(pdf[0])

    assert not page.is_scan
    assert page.skew_degrees is None
    assert page.content_box is not None
    assert max(page.width, page.height) == 2560
