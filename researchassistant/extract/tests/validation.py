from researchassistant.extract.validation import validate_claim

def test_validate_claim_empty_source():
    claim_empty_source = {"source": "", "claim": "claim1", "relevant": "relevant1"}
    document = "This is a test document."

    assert validate_claim(claim_empty_source, document) is False

def test_validate_exact_words():
    claim_empty_source = {"source": "abcey there x exists x a x certain x distinctive x force x in x the x universe xabcey", "claim": "there exists a certain distinctive force in the universe", "relevant": "relevant1"}
    document = "abcey there x exists x a x certain x distinctive x force x in x the x universe xabcey"

    assert validate_claim(claim_empty_source, document) is True

def test_validate_similar_words():
    claim_empty_source = {"source": "there exists a certain distinctive force in the universe", "claim": "there exists a certain distinctive force in the universe", "relevant": "relevant1"}
    document = "abcey there x exists x a x certain x distinctive x force x in x the x universe xabcey"

    assert validate_claim(claim_empty_source, document) is True

def test_validate_similar_words_false():
    claim_empty_source = {"source": "there are distinctive forces in the world", "claim": "there are distinctive forces in the world", "relevant": "relevant1"}
    document = "abcey there x exists x a x certain x distinctive x force x in x the x universe xabcey"

    assert validate_claim(claim_empty_source, document) is False

def test_validate_similar_words_missing():
    claim_empty_source = {"source": "there exists a certain distinctive force in the universe", "claim": "there exists a certain distinctive force in the universe", "relevant": "relevant1"}
    document = "there is a force in the universe"

    assert validate_claim(claim_empty_source, document) is False

def test_validate_claim_source_not_found():
    claim_source_not_found = {"source": "missing_source", "claim": "claim1", "relevant": "relevant1"}
    document = "This is a test document."

    assert validate_claim(claim_source_not_found, document) is False

def test_validate_claim_source_found():
    claim_source_found = {"source": "test", "claim": "claim1", "relevant": "relevant1"}
    document = "This is a test document."

    assert validate_claim(claim_source_found, document) is True

def test_validate_claim_source_found_with_similarity():
    claim_source_similarity = {"source": "tes", "claim": "claim1", "relevant": "relevant1"}
    document = "This is a test document."

    assert validate_claim(claim_source_similarity, document) is True