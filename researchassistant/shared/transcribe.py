import asyncio
from yt_dlp import YoutubeDL
import whisper
import os
from agentbrowser import ensure_event_loop

model = whisper.load_model("base")

ydl_opts = {
    'extract_audio': True,
    'outtmpl': 'scrape/%(title)s.%(ext)s'  # Save downloaded content to 'scrape' folder
}

async def get_best_format(url):
    loop = ensure_event_loop()
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        if 'bestaudio' in info_dict['formats']:
            return 'bestaudio', info_dict['ext']
        elif 'bestvideo+bestaudio' in info_dict['formats']:
            return 'bestvideo+bestaudio', info_dict['ext']
        else:
            return 'best', info_dict['ext']
            

async def download_content(url, format):
    ydl_opts['format'] = format
    loop = ensure_event_loop()
    with YoutubeDL(ydl_opts) as ydl:
        download = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
        print(download)
        if 'requested_downloads' in download:
            return download["requested_downloads"][0]["filepath"]
        return download['filepath']
    
async def transcribe(url):
    best_format, _ = await get_best_format(url)
    downloaded_filepath = await download_content(url, best_format)
    transcribed = await asyncio.get_event_loop().run_in_executor(None, lambda: model.transcribe(downloaded_filepath))
    os.remove(downloaded_filepath)

    # Save transcription to 'scrape' folder
    with open(f'scrape/{os.path.basename(url)}.txt', 'w') as f:
        f.write(transcribed["text"].strip())

    return transcribed["text"].strip()

if __name__ == "__main__":
    instagram_url = "https://www.facebook.com/MojIndia/videos/1140950119725892/"
    result = asyncio.run(transcribe(instagram_url))
    print(result)
