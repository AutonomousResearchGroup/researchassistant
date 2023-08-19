from researchassistant.shared.documents import split_document


def test_split_document():
    text = "This is a test. This is another test"
    split_result = split_document(text)
    assert len(split_result) == 2

    expected_result = ["This is a test. ", "This is another test"]
    assert split_result == expected_result
