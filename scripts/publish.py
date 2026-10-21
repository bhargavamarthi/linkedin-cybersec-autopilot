"""
publish.py
----------
Reads today's post.json
Posts directly to LinkedIn via the UGC Posts API
"""

import os
import json
import datetime
import requests
from pathlib import Path

DATE = datetime.date.today().isoformat()
POST_PATH = f"posts/{DATE}/post.json"

LINKEDIN_API = "https://api.linkedin.com/v2"
TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
PERSON_URN = os.environ["LINKEDIN_PERSON_URN"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
}


def build_post_body(post_text: str, hashtags: list) -> dict:
    full_text = post_text + "\n\n" + " ".join(hashtags)

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

    body = build_post_body(post_text, hashtags)

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
    }
    with open(f"posts/{DATE}/receipt.json", "w") as f:
        json.dump(receipt, f, indent=2)


if __name__ == "__main__":
    publish()
