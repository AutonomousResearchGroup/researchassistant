from transcribe import transcribe

def test(transcription, substring):
    assert transcription.find(substring) >= 0, "expected substring \"" + substring + "\" not found in transcription"

expected_substring_1 = "It's not just science fiction, powerful machines and algorithms are already capable of diagnosing illnesses, performing surgery and driving autonomous cars."
expected_substring_2 = "For instance, could the development of new AI applications be a threat to human rights?"
expected_substring_3 = "For example, ethics frameworks, regulatory oversight and legal safeguards could help us to avoid the misuse of artificial intelligence."

transcription = transcribe("https://youtu.be/5pM6NFb4tqU")

test(transcription, expected_substring_1)
test(transcription, expected_substring_2)
test(transcription, expected_substring_3)
