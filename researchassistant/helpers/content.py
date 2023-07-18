import sys

import PyPDF2
from dotenv import load_dotenv
load_dotenv()

from agentbrowser import navigate_to, get_body_text, create_page


def get_content_from_url(url):
    page = create_page()

    navigate_to(url, page)

    body_text = get_body_text(page)

    return body_text


def get_content_from_pdf(input_file):
    with open(input_file, "rb") as f:
        try:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for i in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[i].extract_text()
            return text
        except PyPDF2.utils.PdfReadError:
            print("Failed to read PDF file.")
            # sys.exit()


def get_content_from_txt(input_file):
    with open(input_file, "r") as f:
        text = f.read()
        return text


def get_content_from_file(input_file):
    if input_file.startswith("http"):
        text = get_content_from_url(input_file)
        return text
    else:
        if input_file.endswith(".pdf"):
            return get_content_from_pdf(input_file)
        elif input_file.endswith(".txt"):
            return get_content_from_txt(input_file)
        else:
            print("Invalid input file format. Please provide a URL or a PDF file.")
            # sys.exit()