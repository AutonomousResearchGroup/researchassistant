from collections import Counter

import fuzzysearch


def validate_claim(claim, document):
    claim_source = claim["source"]
    if claim_source is None or claim_source == "":
        print("Claim is empty")
        return False

    matches = fuzzysearch.find_near_matches(
        claim_source,
        document,
        max_l_dist=8,
        max_substitutions=10,
        max_insertions=10,
        max_deletions=10,
    )

    if len(matches) == 0:
        print("Claim source not found in document")
        sentences = document.split(".")
        for sentence in sentences:
            sentence = sentence.lower()
            claim_source_lower = claim_source.lower()
            # regex replace all non alphanumeric characters in claim_source_lower
            claim_source_lower = "".join(
                [c for c in claim_source_lower if c.isalnum() or c == " "]
            )
            # same for sentences
            sentence = "".join([c for c in sentence if c.isalnum() or c == " "])
            
            similarity_ratio = fuzzysearch.token_set_ratio(claim_source_lower, sentence)
            if similarity_ratio >= 90:
                print("Claim source found in document with 90% similarity")
                claim_words = Counter(claim_source_lower.split())
                sentence_words = Counter(sentence.split())
                common_words = sum((claim_words & sentence_words).values())
                total_words = sum(claim_words.values())
                word_ratio = common_words / total_words * 100

                if word_ratio >= 90:
                    print("Document found in claim source with 90% similarity")
                    return True
                else:
                    print("Document NOT found in claim source")
                    return False

        return False
    else:
        print("Claim source found in document")

    return True
