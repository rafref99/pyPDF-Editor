from __future__ import annotations

import fitz

from pdf_operations import (
    add_page_numbers,
    add_text_watermark,
    compress_pdf,
    convert_html_to_pdf,
    convert_markdown_to_pdf,
    export_pdf_pages_to_images,
    extract_pdf_images,
    images_to_pdf,
    merge_pdfs,
    move_page,
    protect_pdf,
    split_pages,
    unlock_pdf,
    update_metadata,
)


def _sample_document(page_count: int = 2) -> fitz.Document:
    document = fitz.open()
    for page_index in range(page_count):
        page = document.new_page()
        page.insert_text((72, 72), f"Page {page_index + 1}")
    return document


def test_move_page_changes_page_order() -> None:
    document = _sample_document(3)

    new_index = move_page(document, 0, 1)

    assert new_index == 1
    assert "Page 2" in document[0].get_text()
    assert "Page 1" in document[1].get_text()


def test_merge_pdfs_appends_pages(tmp_path) -> None:
    base_document = _sample_document(1)
    source_document = _sample_document(2)
    source_path = tmp_path / "source.pdf"
    source_document.save(source_path)
    source_document.close()

    merge_pdfs(base_document, [source_path])

    assert base_document.page_count == 3


def test_split_pages_writes_individual_pdfs(tmp_path) -> None:
    document = _sample_document(2)

    written_paths = split_pages(document, tmp_path, "sample")

    assert len(written_paths) == 2
    assert all(path.exists() for path in written_paths)


def test_update_metadata_sets_selected_fields() -> None:
    document = _sample_document(1)

    update_metadata(document, {"title": "Example", "author": "PDF Editor"})

    assert document.metadata["title"] == "Example"
    assert document.metadata["author"] == "PDF Editor"


def test_convert_markdown_to_pdf_writes_searchable_pdf(tmp_path) -> None:
    markdown_path = tmp_path / "notes.md"
    markdown_path.write_text(
        "# Project Notes\n\n"
        "This is a **Markdown** file with a [link](https://example.com).\n\n"
        "- First item\n"
        "- Second item\n\n"
        "```python\n"
        "print('hello')\n"
        "```\n",
        encoding="utf-8",
    )
    output_path = tmp_path / "notes.pdf"

    written_path = convert_markdown_to_pdf(markdown_path, output_path)

    assert written_path == output_path
    assert written_path.exists()

    with fitz.open(written_path) as document:
        text = "\n".join(page.get_text() for page in document)

    assert "Project Notes" in text
    assert "Markdown file with a link" in text
    assert "- First item" in text
    assert "print('hello')" in text


def test_convert_html_to_pdf_writes_searchable_pdf(tmp_path) -> None:
    html_path = tmp_path / "page.html"
    html_path.write_text(
        "<!doctype html>"
        "<html><body>"
        "<h1>HTML Export</h1>"
        "<p>This paragraph came from HTML content.</p>"
        "<ul><li>First HTML item</li><li>Second HTML item</li></ul>"
        "</body></html>",
        encoding="utf-8",
    )
    output_path = tmp_path / "page.pdf"

    written_path = convert_html_to_pdf(html_path, output_path)

    assert written_path == output_path
    assert written_path.exists()

    with fitz.open(written_path) as document:
        text = "\n".join(page.get_text() for page in document)

    assert "HTML Export" in text
    assert "This paragraph came from HTML content." in text
    assert "First HTML item" in text


def test_export_pdf_pages_to_images_writes_png_files(tmp_path) -> None:
    document = _sample_document(2)

    written_paths = export_pdf_pages_to_images(document, tmp_path, "sample", zoom=0.5)

    assert len(written_paths) == 2
    assert all(path.exists() for path in written_paths)
    assert all(path.suffix == ".png" for path in written_paths)


def test_images_to_pdf_creates_one_page_per_image(tmp_path) -> None:
    source_document = _sample_document(2)
    image_paths = export_pdf_pages_to_images(source_document, tmp_path, "source", zoom=0.5)
    output_path = tmp_path / "images.pdf"

    written_path = images_to_pdf(image_paths, output_path)

    with fitz.open(written_path) as document:
        assert document.page_count == 2


def test_extract_pdf_images_writes_embedded_images(tmp_path) -> None:
    source_document = _sample_document(1)
    image_path = export_pdf_pages_to_images(source_document, tmp_path, "image_source", zoom=0.5)[0]
    document = fitz.open()
    page = document.new_page()
    page.insert_image(fitz.Rect(72, 72, 172, 172), filename=image_path)

    written_paths = extract_pdf_images(document, tmp_path / "extracted", "sample")

    assert len(written_paths) == 1
    assert written_paths[0].exists()


def test_compress_pdf_writes_pdf(tmp_path) -> None:
    document = _sample_document(1)
    output_path = tmp_path / "compressed.pdf"

    written_path = compress_pdf(document, output_path)

    assert written_path.exists()
    with fitz.open(written_path) as compressed:
        assert compressed.page_count == 1


def test_protect_and_unlock_pdf(tmp_path) -> None:
    document = _sample_document(1)
    protected_path = protect_pdf(document, tmp_path / "protected.pdf", "secret")

    with fitz.open(protected_path) as protected:
        assert protected.needs_pass

    unlocked_path = unlock_pdf(protected_path, tmp_path / "unlocked.pdf", "secret")

    with fitz.open(unlocked_path) as unlocked:
        assert not unlocked.needs_pass
        assert unlocked.page_count == 1


def test_add_watermark_and_page_numbers_add_searchable_text() -> None:
    document = _sample_document(1)

    add_text_watermark(document, "DRAFT")
    add_page_numbers(document, 7)

    text = document[0].get_text()
    assert "DRAFT" in text
    assert "7" in text
