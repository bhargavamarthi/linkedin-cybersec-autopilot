"""
gen_image.py
------------
Reads the image_prompt from today's post.json
Calls Pollinations.ai (free, no API key) to generate the image via FLUX
Saves result to posts/YYYY-MM-DD/image.png
Falls back gracefully to text-only if image generation fails.
"""

import json
import datetime
import requests
import urllib.parse
from pathlib import Path

DATE = datetime.date.today().isoformat()
POST_PATH = f"posts/{DATE}/post.json"
IMAGE_PATH = f"posts/{DATE}/image.jpg"

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width=1280&height=720&model=flux&nologo=true"

FALLBACK_PROMPT = (
    "Professional cybersecurity infographic, dark blue and teal color palette, "
    "shield and lock icons, circuit board patterns, clean modern design, 16:9, "
    "no text, no words, suitable for LinkedIn"
)


def generate_image():
    if Path(POST_PATH).exists():
        with open(POST_PATH) as f:
            post_data = json.load(f)
        prompt = post_data.get("image_prompt", FALLBACK_PROMPT)
        print(f"[gen_image] Using prompt: {prompt[:80]}...")
    else:
        prompt = FALLBACK_PROMPT
        print("[gen_image] post.json not found, using fallback prompt")

    url = POLLINATIONS_URL.format(prompt=urllib.parse.quote(prompt))

    try:
        print("[gen_image] Requesting image from Pollinations.ai (FLUX)...")
        r = requests.get(url, timeout=120)
        r.raise_for_status()

        with open(IMAGE_PATH, "wb") as f:
            f.write(r.content)
        print(f"[gen_image] Saved → {IMAGE_PATH} ({len(r.content)//1024}KB)")
    except Exception as e:
        print(f"[gen_image] WARNING: Image generation failed ({e})")
        print("[gen_image] Post will go text-only")


if __name__ == "__main__":
    generate_image()
