"""
gen_image.py
------------
Reads the image_prompt from today's post.json
Calls Gemini Imagen to generate the image
Saves result to posts/YYYY-MM-DD/image.png
Falls back gracefully to text-only if image generation fails.
"""

import os
import json
import datetime
import base64
from google import genai
from pathlib import Path

DATE = datetime.date.today().isoformat()
POST_PATH = f"posts/{DATE}/post.json"
IMAGE_PATH = f"posts/{DATE}/image.png"

FALLBACK_PROMPT = (
    "Professional cybersecurity infographic, dark blue and teal color palette, "
    "shield and lock icons, circuit board patterns, clean modern design, 16:9, "
    "no text, no words, suitable for LinkedIn"
)


def generate_image():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[gen_image] No GEMINI_API_KEY set, skipping image generation")
        return
    client = genai.Client(api_key=api_key)

    if Path(POST_PATH).exists():
        with open(POST_PATH) as f:
            post_data = json.load(f)
        prompt = post_data.get("image_prompt", FALLBACK_PROMPT)
        print(f"[gen_image] Using prompt: {prompt[:80]}...")
    else:
        prompt = FALLBACK_PROMPT
        print("[gen_image] post.json not found, using fallback prompt")

    try:
        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=genai.types.GenerateImagesConfig(number_of_images=1),
        )
        image_bytes = response.generated_images[0].image.image_bytes
        with open(IMAGE_PATH, "wb") as f:
            f.write(image_bytes)
        print(f"[gen_image] Saved → {IMAGE_PATH} ({len(image_bytes)//1024}KB)")
    except Exception as e:
        print(f"[gen_image] WARNING: Image generation failed ({e})")
        print("[gen_image] Post will go text-only")


if __name__ == "__main__":
    generate_image()
