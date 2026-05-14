"""
AlphaSignal — Daily Stock Picks Generator
Runs via GitHub Actions every weekday at 9:15 AM ET.
Writes picks.json which the dashboard reads.
Optionally sends a Pushover push notification to your phone.
"""

import anthropic
import json
import datetime
import os
import requests

# ── Config ────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
PUSHOVER_TOKEN    = os.environ.get("PUSHOVER_TOKEN", "")   # optional
PUSHOVER_USER     = os.environ.get("PUSHOVER_USER", "")    # optional
DASHBOARD_URL     = "https://sspottabathula.github.io/alphasignal"
OUTPUT_FILE       = "picks.json"

# ── Prompt ────────────────────────────────────────────────────────────────────
today = datetime.date.today().strftime("%A, %B %d, %Y")
now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

PROMPT = f"""Today is {today}. You are an elite quantitative analyst with deep knowledge of US equity markets.

Analyze the current market environment and identify the TOP 3 high-risk/high-return US stock picks for TODAY based on:
- Upcoming or recent earnings catalysts
- FDA approvals / clinical trial readouts
- Macro events (Fed decisions, CPI, jobs data)
- Short squeeze candidates (high short interest + momentum)
- Sector rotation opportunities
- Breaking news / analyst upgrades

IMPORTANT: Respond ONLY with valid JSON. No markdown, no explanation, no code fences. Pure JSON only.

Use this exact structure:
{{
  "date": "{today}",
  "generated_at": "{now_utc}",
  "market_summary": "One sentence macro backdrop under 25 words.",
  "market_sentiment": "bullish|neutral|bearish",
  "picks": [
    {{
      "rank": 1,
      "ticker": "NVDA",
      "name": "NVIDIA Corporation",
      "sector": "Technology",
      "thesis": "Specific catalyst in under 20 words.",
      "entry_price": "$875.00",
      "entry_time": "Market open 9:30 AM ET",
      "entry_note": "One sentence on when/how to enter.",
      "exit_target": "$920.00",
      "stop_loss": "$855.00",
      "upside_pct": "+5.1%",
      "downside_risk": "-2.3%",
      "risk_reward": "2.2:1",
      "risk_level": "High",
      "timeframe": "1-3 days",
      "confidence": "74%",
      "catalyst": "Earnings / FDA / Short squeeze / Sector rotation",
      "exit_signals": "Exit if breaks below $855 or hits $920 target."
    }},
    {{
      "rank": 2,
      "ticker": "TSLA",
      "name": "Tesla Inc.",
      "sector": "Consumer Discretionary",
      "thesis": "Specific catalyst in under 20 words.",
      "entry_price": "$245.00",
      "entry_time": "After 10:00 AM ET on confirmation",
      "entry_note": "One sentence on when/how to enter.",
      "exit_target": "$265.00",
      "stop_loss": "$235.00",
      "upside_pct": "+8.2%",
      "downside_risk": "-4.1%",
      "risk_reward": "2.0:1",
      "risk_level": "Very High",
      "timeframe": "Same day to 2 days",
      "confidence": "61%",
      "catalyst": "Earnings / FDA / Short squeeze / Sector rotation",
      "exit_signals": "Exit if breaks below $235 or RSI above 80."
    }},
    {{
      "rank": 3,
      "ticker": "MRNA",
      "name": "Moderna Inc.",
      "sector": "Healthcare",
      "thesis": "Specific catalyst in under 20 words.",
      "entry_price": "$98.50",
      "entry_time": "Market open 9:30 AM ET",
      "entry_note": "One sentence on when/how to enter.",
      "exit_target": "$108.00",
      "stop_loss": "$93.00",
      "upside_pct": "+9.6%",
      "downside_risk": "-5.6%",
      "risk_reward": "1.7:1",
      "risk_level": "Very High",
      "timeframe": "1-5 days",
      "confidence": "58%",
      "catalyst": "Earnings / FDA / Short squeeze / Sector rotation",
      "exit_signals": "Exit on catalyst resolution or stop loss hit."
    }}
  ],
  "news_signals": [
    {{"headline": "Short headline under 12 words", "impact": "bullish", "ticker": "NVDA"}},
    {{"headline": "Short headline under 12 words", "impact": "bearish", "ticker": "SPY"}},
    {{"headline": "Short headline under 12 words", "impact": "bullish", "ticker": "TSLA"}}
  ],
  "risk_warning": "High-risk picks — never invest more than you can afford to lose."
}}"""


# ── Generate picks ─────────────────────────────────────────────────────────────
def generate_picks() -> dict:
    print(f"Generating picks for {today}...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": PROMPT}]
    )

    raw = response.content[0].text.strip()
    # Strip any accidental markdown fences
    raw = raw.replace("```json", "").replace("```", "").strip()

    data = json.loads(raw)
    print(f"✓ Generated {len(data.get('picks', []))} picks")
    return data


# ── Save to file ───────────────────────────────────────────────────────────────
def save_picks(data: dict):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved to {OUTPUT_FILE}")


# ── Phone notification (Pushover) ──────────────────────────────────────────────
def send_pushover(data: dict):
    if not PUSHOVER_TOKEN or not PUSHOVER_USER:
        print("  Skipping Pushover (no credentials set)")
        return

    picks = data.get("picks", [])
    if not picks:
        return

    top = picks[0]
    lines = [f"📈 {data.get('market_summary', '')}"]
    for p in picks:
        lines.append(
            f"\n#{p['rank']} {p['ticker']} — {p['upside_pct']} target\n"
            f"  Entry: {p['entry_price']} | Stop: {p['stop_loss']}\n"
            f"  {p['thesis']}"
        )

    payload = {
        "token":     PUSHOVER_TOKEN,
        "user":      PUSHOVER_USER,
        "title":     f"AlphaSignal Picks — {today}",
        "message":   "\n".join(lines),
        "url":       DASHBOARD_URL,
        "url_title": "View dashboard",
        "priority":  0,
        "sound":     "cashregister",
    }

    r = requests.post("https://api.pushover.net/1/messages.json", data=payload, timeout=10)
    if r.status_code == 200:
        print("✓ Pushover notification sent")
    else:
        print(f"  Pushover failed: {r.status_code} {r.text}")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    data = generate_picks()
    save_picks(data)
    send_pushover(data)
    print("Done.")
