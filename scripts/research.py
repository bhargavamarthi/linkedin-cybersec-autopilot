"""
research.py
-----------
Calls Claude API to:
1. Research the hottest cybersecurity topic of the week
2. Write a LinkedIn post (~1200 chars) with hook + insight + CTA + open-to-work close

Saves output to posts/YYYY-MM-DD/post.json
"""

import os
import json
import datetime
import anthropic

TOPIC_ROTATION = {
    0: "threat_of_week",    # Monday
    2: "concept_explainer", # Wednesday
    4: "industry_insight",  # Friday
}

# Real, fixed facts about the author — Claude must use these verbatim in substance
# and must never add to, embellish, or fabricate beyond them.
AUTHOR_FACTS = (
    "- Actively job-searching, remote-only, for: SOC Analyst, Vulnerability Assessment & "
    "Penetration Testing (VA/PT) Analyst, or Penetration Tester roles.\n"
    "- Experience: 1 year, from an unpaid remote cybersecurity internship.\n"
    "- Certification: CompTIA Security+ (obtained August 2026).\n"
    "- Open to connecting and open to referrals/opportunities."
)

SYSTEM_PROMPT = f"""You are a cybersecurity professional writing authoritative LinkedIn content.
Your posts are grounded in real, current, verifiable facts — named CVEs, named incidents, published research, actual statistics.
You write in first person to explain, analyze, and opine on facts — never to share personal anecdotes, personal exam experiences, or invented stories.
You never fabricate personal failures, certification attempts, or career struggles on behalf of the author.
You never name private individuals, and you never make claims about identifiable third parties (people or companies) beyond what is already public record.
Virality comes from the quality, relevance, and sharpness of the information — never from clickbait, exaggeration, or misleading framing. Every hook must be a genuine, verifiable fact.

Writing style, optimized to spread on LinkedIn:
- Open with the sharpest, most specific line you have — a hard number, a named CVE/incident, or a genuinely counterintuitive fact. Never a greeting or throat-clearing sentence.
- Short lines and tight paragraphs (2-3 sentences max per block) for mobile skimming.
- Use arrow (→) or bullet takeaways for the concrete, actionable points.
- Close the analysis with one pointed, specific question tied to the topic — never a generic "thoughts?".

The author's real, current background (use naturally in the closing section of every post — do not alter, embellish, or add to these facts, and never invent experience, roles, or certifications beyond them):
{AUTHOR_FACTS}

Every single post must end with a short (2-3 sentence) closing that works this background in naturally and invites connections or referrals. Vary the phrasing, tone, and structure of this closing every time — it must never read as a copy-pasted template. Do not name specific companies, recruiters, or people in this closing."""


def get_post_type():
    weekday = datetime.date.today().weekday()
    return TOPIC_ROTATION.get(weekday, "concept_explainer")


def build_prompt(post_type: str) -> str:
    today = datetime.date.today().strftime("%B %d, %Y")

    if post_type == "threat_of_week":
        task = (
            "Identify the single most talked-about cybersecurity threat, breach, CVE, "
            "or ransomware incident from the past 7 days. Use real, named incidents and "
            "published CVE numbers where possible. Write a LinkedIn post that: "
            "• Opens with a sharp, factual hook (a specific number, a named victim, or a "
            "  counterintuitive finding — never a fabricated personal story) "
            "• Explains what happened and why it matters in plain English "
            "• Names 2-3 concrete, actionable takeaways for defenders (use → bullets) "
            "• Asks one pointed, topic-specific question to drive comments "
            "• Closes with the author's real background and an invitation to connect, per the system prompt "
            "Do not invent personal anecdotes. Ground every claim in real events."
        )
    elif post_type == "industry_insight":
        task = (
            "Pick one significant, contemporary trend, regulatory development, or strategic "
            "shift in cybersecurity (e.g. NIS2 enforcement, AI-assisted attacks, CISA KEV "
            "updates, zero-day commoditization, SEC disclosure rules, supply chain security). "
            "Write a LinkedIn post that: "
            "• Opens with a sharp fact, statistic, or named development that frames why this matters now "
            "• Analyzes the real-world implication for organizations or practitioners (use → bullets for impacts) "
            "• Offers a pointed, expert perspective in first person (opinion and analysis — not personal story) "
            "• Asks one pointed, topic-specific question to drive comments "
            "• Closes with the author's real background and an invitation to connect, per the system prompt "
            "Do not invent personal experiences, exam results, or career anecdotes. "
            "The hook must come from the substance of the issue, not from personal drama."
        )
    else:
        task = (
            "Pick one foundational or emerging cybersecurity concept that is widely "
            "misunderstood or underappreciated (e.g. Zero Trust, SIEM, EDR, threat hunting, "
            "MITRE ATT&CK, cloud misconfigs, memory-safe languages, SBOM). Write a LinkedIn "
            "post that explains it clearly using a concrete real-world analogy or a named "
            "real incident that illustrates the concept (use → bullets for the key points). "
            "Use first-person voice to guide the reader through the explanation — not to "
            "share personal stories. Ask one pointed, topic-specific question to drive comments. "
            "Close with the author's real background and an invitation to connect, per the system prompt. "
            "Do not fabricate personal anecdotes or certification experiences."
        )

    return f"""Today is {today}. Post type: {post_type}

{task}

STRICT FORMAT — respond with valid JSON only, no markdown fences:
{{
  "topic": "<one-line topic summary>",
  "post_text": "<full LinkedIn post, 1000-1500 characters, including the closing background/CTA section, use line breaks and emojis sparingly>",
  "hashtags": ["#CyberSecurity", "<3-4 more topic-relevant hashtags>", "<1-2 career hashtags such as #OpenToWork, #CyberSecurityJobs, #SOCAnalyst, #PenetrationTesting, #InfoSecCommunity — pick ones that fit the topic and the author's target roles>"]
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
