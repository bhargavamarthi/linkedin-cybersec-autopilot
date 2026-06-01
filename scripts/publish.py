"""
publish.py
----------
Reads today's post.json + image.png
Posts directly to LinkedIn via the UGC Posts API
"""

import os
import json
import datetime
import requests
from pathlib import Path

DATE = datetime.date.today().isoformat()
POST_PATH = f"posts/{DATE}/post.json"
IMAGE_PATH = next(
    (f"posts/{DATE}/{f}" for f in ("image.jpg", "image.png") if Path(f"posts/{DATE}/{f}").exists()),
    f"posts/{DATE}/image.jpg",
)

LINKEDIN_API = "https://api.linkedin.com/v2"
TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
PERSON_URN = os.environ["LINKEDIN_PERSON_URN"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
}


def upload_image(image_path: str) -> str | None:
    if not Path(image_path).exists():
        print("[publish] No image found, posting text-only")
        return None

    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": PERSON_URN,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent",
                }
            ],
        }
    }

    r = requests.post(
        f"{LINKEDIN_API}/assets?action=registerUpload",
        headers=HEADERS,
        json=register_payload,
    )
    r.raise_for_status()
    upload_data = r.json()

    upload_url = upload_data["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]
    asset_urn = upload_data["value"]["asset"]

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    content_type = "image/jpeg" if image_path.endswith((".jpg", ".jpeg")) else "image/png"
    r = requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": content_type},
        data=image_bytes,
    )
    r.raise_for_status()
    print(f"[publish] Image uploaded → {asset_urn}")
    return asset_urn


def build_post_body(post_text: str, hashtags: list, asset_urn: str | None) -> dict:
    full_text = post_text + "\n\n" + " ".join(hashtags)

    if asset_urn:
        return {
            "author": PERSON_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": full_text},
                    "shareMediaCategory": "IMAGE",
                    "media": [{"status": "READY", "media": asset_urn}],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
    else:
        return {
            "author": PERSON_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": full_text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }


def publish():
    if not Path(POST_PATH).exists():
        print(f"[publish] ERROR: {POST_PATH} not found. Did research.py run?")
        return

    with open(POST_PATH) as f:
        post_data = json.load(f)

    post_text = post_data["post_text"]
    hashtags = post_data.get("hashtags", ["#CyberSecurity"])

    asset_urn = upload_image(IMAGE_PATH)
    body = build_post_body(post_text, hashtags, asset_urn)

    r = requests.post(f"{LINKEDIN_API}/ugcPosts", headers=HEADERS, json=body)
    r.raise_for_status()

    post_id = r.headers.get("x-restli-id", "unknown")
    print(f"[publish] Posted to LinkedIn! ID: {post_id}")
    print(f"[publish] Topic: {post_data.get('topic', 'N/A')}")

    receipt = {
        "published_at": datetime.datetime.utcnow().isoformat(),
        "post_id": post_id,
        "topic": post_data.get("topic"),
        "char_count": len(post_text),
        "had_image": asset_urn is not None,
    }
    with open(f"posts/{DATE}/receipt.json", "w") as f:
        json.dump(receipt, f, indent=2)


if __name__ == "__main__":
    publish()
