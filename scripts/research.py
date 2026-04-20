"""
research.py
-----------
Calls Claude API to:
1. Research the hottest cybersecurity topic of the week
2. Write a LinkedIn post (~1200 chars) with hook + insight + CTA
3. Produce an image prompt for Gemini image generation

Saves output to posts/YYYY-MM-DD/post.json
"""

import os
import json
import datetime
import anthropic

TOPIC_ROTATION = {
    0: "threat_of_week",    # Monday
    2: "concept_explainer", # Wednesday
    4: "career_tip",        # Friday
}

SYSTEM_PROMPT = """You are a cybersecurity content strategist with 20+ years of experience.
You create LinkedIn posts that attract recruiters and demonstrate deep technical knowledge.
Your posts are authoritative, human, and always end with a clear call to action.
You understand what goes viral on LinkedIn in the cybersecurity space in 2025."""


def get_post_type():
    weekday = datetime.date.today().weekday()
    return TOPIC_ROTATION.get(weekday, "concept_explainer")


def build_prompt(post_type: str) -> str:
    today = datetime.date.today().strftime("%B %d, %Y")

    if post_type == "threat_of_week":
        task = (
            "Identify the single most talked-about cybersecurity threat, breach, CVE, "
            "or ransomware incident from the past 7 days. Write a LinkedIn post that: "
            "• Hooks with a shocking or counterintuitive opening line "
            "• Explains what happened and why it matters in plain English "
            "• Names 2-3 concrete takeaways for defenders "
            "• Ends with 'What's your take? Comment below.' "
        )
    elif post_type == "career_tip":
        task = (
            "Write a LinkedIn post from the perspective of someone actively breaking "
            "into cybersecurity. Share one authentic career insight, study tip, or "
            "certification lesson. Make it personal, relatable, and useful. "
            "End with a question that invites other job-seekers to reply. "
        )
    else:
        task = (
            "Pick one foundational or emerging cybersecurity concept that is widely "
            "misunderstood or underappreciated (e.g. Zero Trust, SIEM, EDR, threat hunting, "
            "MITRE ATT&CK, cloud misconfigs). Write a LinkedIn post that explains it "
            "clearly using a real-world analogy. End with '♻️ Repost if this helped someone.' "
        )

    return f"""Today is {today}. Post type: {post_type}

{task}

STRICT FORMAT — respond with valid JSON only, no markdown fences:
{{
  "topic": "<one-line topic summary>",
  "post_text": "<full LinkedIn post, 900-1300 characters, use line breaks and emojis sparingly>",
  "hashtags": ["#CyberSecurity", "<4 more relevant hashtags>"],
  "image_prompt": "<detailed image prompt: professional, infographic-style, no text in image, 16:9, cybersecurity theme>"
}}"""


def research_and_write() -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    post_type = get_post_type()
    print(f"[research] Post type today: {post_type}")

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(post_type)}],
    )

    raw = message.content[0].text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    data = json.loads(raw)
    data["post_type"] = post_type
    data["date"] = datetime.date.today().isoformat()
    return data


if __name__ == "__main__":
    result = research_and_write()

    out_dir = f"posts/{result['date']}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/post.json"

    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"[research] Saved → {out_path}")
    print(f"[research] Topic: {result['topic']}")
    print(f"[research] Post length: {len(result['post_text'])} chars")
