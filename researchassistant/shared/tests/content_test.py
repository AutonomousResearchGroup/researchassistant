import asyncio
import os
import PyPDF2
from tempfile import NamedTemporaryFile

from researchassistant.shared.content import get_content_from_pdf, get_content_from_txt, get_content_from_file


def test_get_content_from_pdf_invalid_pdf_content():
    pdf_content = "Invalid content."
    # Create a temporary file with .pdf extension
    with NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_file.write(pdf_content.encode())
        temp_file_path = temp_file.name

    content_result = get_content_from_pdf(temp_file_path)
    expected_result = "Failed to read PDF file."
    assert content_result == expected_result

    # Remove temporary file
    os.remove(temp_file_path)


def test_get_content_from_pdf_success():
    with NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        pdf_writer = PyPDF2.PdfWriter()
        # Create a blank page
        page = PyPDF2.PageObject.create_blank_page(width=200, height=200)

        pdf_writer.add_page(page)
        pdf_writer.write(temp_file)
        temp_file_path = temp_file.name

    content_result = get_content_from_pdf(temp_file_path)
    expected_result = ""
    assert content_result == expected_result

    os.remove(temp_file_path)


def test_get_content_from_txt_success():
    txt_content: str = "This is a test content."
    with NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        temp_file.write(txt_content.encode())
        temp_file_path = temp_file.name

    content_result = get_content_from_txt(temp_file_path)
    expected_result = "This is a test content."
    assert content_result == expected_result

    os.remove(temp_file_path)


def test_get_content_from_file_http():
    content_result = asyncio.get_event_loop().run_until_complete(
        get_content_from_file("http://www.example.com/"))

    assert type(content_result) == str


def test_get_content_from_file_invalid_file_format():
    invalid_format = ".invalid_format"
    # Create a temporary file with invalid format
    test_content = "This is a test content."
    with NamedTemporaryFile(suffix=invalid_format, delete=False) as temp_file:
        temp_file.write(test_content.encode())
        temp_file_path = temp_file.name

    content_result = asyncio.get_event_loop().run_until_complete(
        get_content_from_file(temp_file_path))

    expected_result = "Invalid input file format. Please provide a URL or a PDF file."
    assert content_result == expected_result

    os.remove(temp_file_path)
