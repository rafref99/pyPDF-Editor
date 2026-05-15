from __future__ import annotations

import re
from pathlib import Path

import fitz


PAGE_WIDTH = 595
PAGE_HEIGHT = 842
PAGE_MARGIN = 54
BODY_FONT = "helv"
BOLD_FONT = "hebo"
CODE_FONT = "cour"


def merge_pdfs(base_document: fitz.Document, pdf_paths: list[Path]) -> None:
    for pdf_path in pdf_paths:
        with fitz.open(pdf_path) as source:
            base_document.insert_pdf(source)


def move_page(document: fitz.Document, page_index: int, offset: int) -> int:
    target_index = page_index + offset
    if target_index < 0 or target_index >= document.page_count:
        return page_index

    if offset > 0:
        for _ in range(offset):
            document.move_page(page_index + 1, page_index)
            page_index += 1
    else:
        for _ in range(abs(offset)):
            document.move_page(page_index, page_index - 1)
            page_index -= 1

    return target_index


def split_pages(document: fitz.Document, output_dir: Path, base_name: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written_paths: list[Path] = []

    for page_index in range(document.page_count):
        single_page = fitz.open()
        single_page.insert_pdf(document, from_page=page_index, to_page=page_index)
        output_path = output_dir / f"{base_name}_page_{page_index + 1}.pdf"
        single_page.save(output_path, garbage=4, deflate=True)
        single_page.close()
        written_paths.append(output_path)

    return written_paths


def update_metadata(document: fitz.Document, metadata: dict[str, str]) -> None:
    current_metadata = document.metadata or {}
    updated_metadata = current_metadata.copy()
    updated_metadata.update(metadata)
    document.set_metadata(updated_metadata)


def compress_pdf(document: fitz.Document, output_path: Path) -> Path:
    output_path = output_path.with_suffix(".pdf")
    document.save(output_path, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True)
    return output_path


def protect_pdf(document: fitz.Document, output_path: Path, password: str) -> Path:
    output_path = output_path.with_suffix(".pdf")
    permissions = int(
        fitz.PDF_PERM_PRINT
        | fitz.PDF_PERM_COPY
        | fitz.PDF_PERM_ANNOTATE
        | fitz.PDF_PERM_ACCESSIBILITY
    )
    document.save(
        output_path,
        garbage=4,
        deflate=True,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw=password,
        user_pw=password,
        permissions=permissions,
    )
    return output_path


def unlock_pdf(input_path: Path, output_path: Path, password: str) -> Path:
    output_path = output_path.with_suffix(".pdf")
    document = fitz.open(input_path)
    try:
        if document.needs_pass and not document.authenticate(password):
            raise ValueError("Incorrect password.")

        document.save(output_path, garbage=4, deflate=True, encryption=fitz.PDF_ENCRYPT_NONE)
    finally:
        document.close()

    return output_path


def export_pdf_pages_to_images(
    document: fitz.Document,
    output_dir: Path,
    base_name: str,
    image_format: str = "png",
    zoom: float = 2.0,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    image_format = image_format.lower().lstrip(".")
    written_paths: list[Path] = []

    for page_index in range(document.page_count):
        pixmap = document[page_index].get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        output_path = output_dir / f"{base_name}_page_{page_index + 1}.{image_format}"
        pixmap.save(output_path)
        written_paths.append(output_path)

    return written_paths


def extract_pdf_images(document: fitz.Document, output_dir: Path, base_name: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written_paths: list[Path] = []
    seen_xrefs: set[int] = set()

    for page_index in range(document.page_count):
        for image_index, image_info in enumerate(document[page_index].get_images(full=True), start=1):
            xref = image_info[0]
            if xref in seen_xrefs:
                continue

            seen_xrefs.add(xref)
            extracted = document.extract_image(xref)
            extension = extracted.get("ext", "png")
            output_path = output_dir / f"{base_name}_page_{page_index + 1}_image_{image_index}.{extension}"
            output_path.write_bytes(extracted["image"])
            written_paths.append(output_path)

    return written_paths


def images_to_pdf(image_paths: list[Path], output_path: Path) -> Path:
    if not image_paths:
        raise ValueError("At least one image is required.")

    output_path = output_path.with_suffix(".pdf")
    document = fitz.open()
    try:
        for image_path in image_paths:
            image_document = fitz.open(image_path)
            try:
                pdf_bytes = image_document.convert_to_pdf()
            finally:
                image_document.close()

            image_pdf = fitz.open("pdf", pdf_bytes)
            try:
                document.insert_pdf(image_pdf)
            finally:
                image_pdf.close()

        document.save(output_path, garbage=4, deflate=True)
    finally:
        document.close()

    return output_path


def add_text_watermark(
    document: fitz.Document,
    text: str,
    font_size: int = 48,
    opacity: float = 0.18,
) -> None:
    for page in document:
        rect = page.rect
        watermark_rect = fitz.Rect(36, rect.height / 2 - 60, rect.width - 36, rect.height / 2 + 60)
        page.insert_textbox(
            watermark_rect,
            text,
            fontsize=font_size,
            fontname=BOLD_FONT,
            color=(0.45, 0.45, 0.45),
            align=fitz.TEXT_ALIGN_CENTER,
            fill_opacity=opacity,
            overlay=True,
        )


def add_page_numbers(document: fitz.Document, start_number: int = 1) -> None:
    for page_index, page in enumerate(document):
        number = str(start_number + page_index)
        rect = page.rect
        text_width = fitz.get_text_length(number, fontname=BODY_FONT, fontsize=10)
        x = (rect.width - text_width) / 2
        y = rect.height - 28
        page.insert_text((x, y), number, fontsize=10, fontname=BODY_FONT, fill=(0.2, 0.2, 0.2))


def convert_markdown_to_pdf(markdown_path: Path, output_path: Path) -> Path:
    markdown_text = markdown_path.read_text(encoding="utf-8")
    output_path = output_path.with_suffix(".pdf")

    document = fitz.open()
    page = _new_markdown_page(document)
    y = PAGE_MARGIN
    in_code_block = False

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()

        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            y += 8
            continue

        if in_code_block:
            page, y = _draw_wrapped_text(document, page, line or " ", y, 9, CODE_FONT, 11)
            continue

        stripped = line.strip()
        if not stripped:
            y += 10
            continue

        if re.fullmatch(r"[-*_]{3,}", stripped):
            page, y = _ensure_page_space(document, page, y, 18)
            page.draw_line(
                (PAGE_MARGIN, y),
                (PAGE_WIDTH - PAGE_MARGIN, y),
                color=(0.55, 0.55, 0.55),
                width=0.8,
            )
            y += 18
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading_match:
            level = len(heading_match.group(1))
            text = _clean_inline_markdown(heading_match.group(2))
            font_size = {1: 24, 2: 20, 3: 17, 4: 14, 5: 12, 6: 11}[level]
            y += 8 if level <= 2 else 4
            page, y = _draw_wrapped_text(document, page, text, y, font_size, BOLD_FONT, font_size + 6)
            y += 6
            continue

        quote_match = re.match(r"^>\s?(.*)$", stripped)
        if quote_match:
            text = "| " + _clean_inline_markdown(quote_match.group(1))
            page, y = _draw_wrapped_text(document, page, text, y, 11, BODY_FONT, 15, indent=12)
            y += 3
            continue

        list_match = re.match(r"^([-*+]|\d+\.)\s+(.+)$", stripped)
        if list_match:
            marker = list_match.group(1)
            marker = "-" if marker in {"-", "*", "+"} else marker
            text = f"{marker} {_clean_inline_markdown(list_match.group(2))}"
            page, y = _draw_wrapped_text(document, page, text, y, 11, BODY_FONT, 15, indent=16)
            continue

        page, y = _draw_wrapped_text(
            document,
            page,
            _clean_inline_markdown(stripped),
            y,
            11,
            BODY_FONT,
            15,
        )

    document.set_metadata({"title": markdown_path.stem, "creator": "pyPDF Editor"})
    document.save(output_path, garbage=4, deflate=True)
    document.close()
    return output_path


def convert_html_to_pdf(html_path: Path, output_path: Path) -> Path:
    html_text = html_path.read_text(encoding="utf-8")
    output_path = output_path.with_suffix(".pdf")
    archive = fitz.Archive(str(html_path.parent))
    story = fitz.Story(html_text, archive=archive)
    writer = fitz.DocumentWriter(str(output_path))

    def rectfn(_rect_num, _filled):
        return (
            fitz.Rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT),
            fitz.Rect(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - PAGE_MARGIN, PAGE_HEIGHT - PAGE_MARGIN),
            fitz.Identity,
        )

    try:
        story.write(writer, rectfn)
    finally:
        writer.close()

    with fitz.open(output_path) as document:
        document.set_metadata({"title": html_path.stem, "creator": "pyPDF Editor"})
        document.saveIncr()

    return output_path


def _new_markdown_page(document: fitz.Document) -> fitz.Page:
    return document.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)


def _ensure_page_space(
    document: fitz.Document,
    page: fitz.Page,
    y: float,
    needed_height: float,
) -> tuple[fitz.Page, float]:
    if y + needed_height <= PAGE_HEIGHT - PAGE_MARGIN:
        return page, y

    return _new_markdown_page(document), PAGE_MARGIN


def _draw_wrapped_text(
    document: fitz.Document,
    page: fitz.Page,
    text: str,
    y: float,
    font_size: int,
    font_name: str,
    line_height: int,
    indent: int = 0,
) -> tuple[fitz.Page, float]:
    max_width = PAGE_WIDTH - (PAGE_MARGIN * 2) - indent
    lines = _wrap_text(text, max_width, font_name, font_size)

    for index, wrapped_line in enumerate(lines):
        page, y = _ensure_page_space(document, page, y, line_height)
        x = PAGE_MARGIN + (indent if index > 0 else 0)
        page.insert_text((x, y), wrapped_line, fontsize=font_size, fontname=font_name, fill=(0.08, 0.08, 0.08))
        y += line_height

    return page, y


def _wrap_text(text: str, max_width: float, font_name: str, font_size: int) -> list[str]:
    if not text:
        return [""]

    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current_line = words[0]

    for word in words[1:]:
        candidate = f"{current_line} {word}"
        if fitz.get_text_length(candidate, fontname=font_name, fontsize=font_size) <= max_width:
            current_line = candidate
        else:
            lines.extend(_split_long_word(current_line, max_width, font_name, font_size))
            current_line = word

    lines.extend(_split_long_word(current_line, max_width, font_name, font_size))
    return lines


def _split_long_word(text: str, max_width: float, font_name: str, font_size: int) -> list[str]:
    if fitz.get_text_length(text, fontname=font_name, fontsize=font_size) <= max_width:
        return [text]

    lines: list[str] = []
    current = ""
    for character in text:
        candidate = current + character
        if current and fitz.get_text_length(candidate, fontname=font_name, fontsize=font_size) > max_width:
            lines.append(current)
            current = character
        else:
            current = candidate

    if current:
        lines.append(current)

    return lines


def _clean_inline_markdown(text: str) -> str:
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(`+)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    return text
