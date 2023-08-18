from researchassistant.shared.documents import split_document


def test_split_document():
    text = "This is a test. This is another test"
    result = split_document(text)
    assert len(result) == 2

    expected_result = ["This is a test. ", "This is another test"]
    assert result == expected_result
