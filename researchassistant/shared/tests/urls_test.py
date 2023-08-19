from researchassistant.shared.urls import add_url_entry, get_url_entries, url_has_been_crawled
from agentmemory import get_memories


def test_add_url_entry():
    url = "https://www.example.com"
    text = "Example Url"
    context = {
        "project_name": "my_project"
    }
    result = add_url_entry(url, text, context)
    expected_crawled_data = {
        "text": "Example Url",
        "url": "https://www.example.com",
        "type": "url",
        "project_name": "my_project",
        "valid": 'True',
        "crawled": 'True',
    }
    assert result["crawled_urls"][0]["text"] == expected_crawled_data["text"]
    assert result["crawled_urls"][0]["url"] == expected_crawled_data["url"]
    assert result["crawled_urls"][0]["type"] == expected_crawled_data["type"]
    assert result["crawled_urls"][0]["project_name"] == expected_crawled_data["project_name"]
    assert result["crawled_urls"][0]["valid"] == expected_crawled_data["valid"]
    assert result["crawled_urls"][0]["crawled"] == expected_crawled_data["crawled"]


def test_get_url_entries_missing_entry():
    context_data = {
        "project_name": "sample_project"
    }
    valid = True
    result = get_url_entries(context=context_data, valid=valid)

    expected_result = get_memories("sample_project_crawled_urls")
    assert result == expected_result


def test_get_url_entries_valid_entries():
    context_data = {
        "project_name": "test_project"
    }
    valid = True
    crawled = True
    result = get_url_entries(context=context_data, valid=valid, crawled=crawled)
    expected_result = get_memories("test_project_crawled_urls")
    assert result == expected_result
