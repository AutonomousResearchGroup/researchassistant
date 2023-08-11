from yt_dlp import YoutubeDL
import whisper
import os

model = whisper.load_model("base")
ydl = YoutubeDL({
    'extract_audio': True,
    'format': 'bestaudio',
    'outtmpl': '/tmp/%(title)s.%(ext)s'
})

def transcribe(url):
    download = ydl.extract_info(url,download=True)
    downloaded_filepath = download["requested_downloads"][0]["filepath"]
    transcribed = model.transcribe(downloaded_filepath)
    os.remove(downloaded_filepath)

    return transcribed["text"].strip()
