import sys

import PyPDF2
from dotenv import load_dotenv

load_dotenv()

from agentbrowser import async_create_page, async_get_body_text, async_navigate_to

async def get_content_from_url(url):
    page = await async_create_page()

    page = await async_navigate_to(url, page)

    body_text = await async_get_body_text(page)

    return body_text


def get_content_from_pdf(input_file):
    with open(input_file, "rb") as f:
        try:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for i in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[i].extract_text()
            return text
        except PyPDF2.errors.PdfReadError:
            error_msg = "Failed to read PDF file."
            print(error_msg)
            return error_msg
            # sys.exit()


def get_content_from_txt(input_file):
    with open(input_file, "r") as f:
        text = f.read()
        return text


async def get_content_from_file(input_file):
    if input_file.startswith("http"):
        text = await get_content_from_url(input_file)
        return text
    else:
        if input_file.endswith(".pdf"):
            return get_content_from_pdf(input_file)
        elif input_file.endswith(".txt"):
            return get_content_from_txt(input_file)
        else:
            error_msg = "Invalid input file format. Please provide a URL or a PDF file."
            print(error_msg)
            return error_msg
            # sys.exit()
