from wtpsplit import WtP

wtp = WtP("wtp-canine-s-12l")


def split_file(file_path):
    with open(file_path, "r") as f:
        text = f.read()
    sentences = split_document(text)
    with open(file_path, "w") as f:
        for sentence in sentences:
            f.write(sentence + "\n")


def split_document(text):
    sentences = wtp.split(text, lang_code="en")
    return sentences
