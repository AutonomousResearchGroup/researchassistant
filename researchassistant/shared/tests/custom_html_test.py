from researchassistant.shared.custom_html import extract_page_title, extract_links


def test_extract_page_title_valid_title():
    html_data = """
    <html>
    <head>
        <title>Test title</title>
    </head>
        <body>
            <h1>Test</h1>
        </body>
    </html>
    """

    extraction_result = extract_page_title(html_data)
    expected_result = "Test title"
    assert extraction_result == expected_result


def test_extract_page_title_no_title():
    html_data = """
    <html>
        <body>
            <h1>Test</h1>
        </body>
    </html>
    """

    extraction_result = extract_page_title(html_data)
    assert extraction_result is None


def test_extract_links_no_links():
    # Content with no links
    html_data = """
    <html>
        <body>
            <h1>Test</h1>
        </body>
    </html>
    """

    extraction_result = extract_links(html_data)
    assert len(extraction_result) == 0


def test_extract_links_blank_link():
    # Content with blank link
    html_data = """
    <html>
        <body>
            <a href="">blank link</a>
            <a href="https://www.example.com">Example</a>
        </body>
    </html>
    """

    extraction_result = extract_links(html_data)
    expected_result = [
        {
            "name": "Example",
            "url": "https://www.example.com"
        }
    ]
    assert len(extraction_result) == 1
    assert extraction_result == expected_result


def test_extract_links_valid_links():
    html_data = """
    <html>
        <body>
            <a href="https://www.example.com">Example</a>
            <a href="https://www.github.com">GitHub</a>
        </body>
    </html>
    """

    extraction_result = extract_links(html_data)
    expected_result = [
        {
            "name": "Example",
            "url": "https://www.example.com"
        },
        {
            "name": "GitHub",
            "url": "https://www.github.com"
        }
    ]
    assert len(extraction_result) == 2
    assert extraction_result == expected_result
