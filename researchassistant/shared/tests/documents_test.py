from researchassistant.shared.documents import split_document


def test_split_document():
    text = "This is a test. This is another test"
    split_result = split_document(text)
    assert len(split_result) == 2, "The split result should have 2 sentences."

    expected_result = ["This is a test. ", "This is another test"]
    assert split_result == expected_result, "The split result should be the same as the expected result."
