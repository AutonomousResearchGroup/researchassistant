from researchassistant.shared.urls import add_url_entry, get_url_entries

from agentmemory import (
    get_memories,
    create_memory,
    wipe_all_memories
)


def test_add_url_entry():
    wipe_all_memories()
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
    # Assert that the memory was created correctly
    assert result["crawled_urls"][0]["text"] == expected_crawled_data["text"]
    assert result["crawled_urls"][0]["url"] == expected_crawled_data["url"]
    assert result["crawled_urls"][0]["type"] == expected_crawled_data["type"]
    assert result["crawled_urls"][0]["project_name"] == expected_crawled_data["project_name"]
    assert result["crawled_urls"][0]["valid"] == expected_crawled_data["valid"]
    assert result["crawled_urls"][0]["crawled"] == expected_crawled_data["crawled"]


def test_get_url_entries_missing_entry():
    wipe_all_memories()
    context_data = {
        "project_name": "sample_project"
    }
    create_memory(
        "sample_project_crawled_urls",
        "document",
        {
            "text": "Test Url",
            "url": "https://www.example.com",
            "type": "url",
            "project_name": "sample_project",
            "valid": 'True',
            "crawled": 'True',
        },
    )

    valid = True
    result = get_url_entries(context=context_data, valid=valid)
    assert len(result) == 1, "Should return 1 result"

    expected_result = get_memories("sample_project_crawled_urls")
    assert result == expected_result, "Should return the same result"


def test_get_url_entries_valid_entries():
    wipe_all_memories()
    context_data = {
        "project_name": "test_project"
    }
    test_data = {
        "text": "Test Url",
        "url": "https://www.example.com",
        "type": "url",
        "project_name": "test_project",
        "valid": 'True',
        "crawled": 'True',
    }
    create_memory(
        "test_project_crawled_urls",
        "document 1",
        test_data,
    )
    create_memory(
        "test_project_crawled_urls",
        "document 2",
        test_data,
    )
    valid = True
    crawled = True
    result = get_url_entries(context=context_data, valid=valid, crawled=crawled)
    assert len(result) == 2, "Should return 2 results"
    expected_result = get_memories("test_project_crawled_urls")
    assert result == expected_result, "Should return the same result"
