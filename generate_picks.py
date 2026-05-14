"""
AlphaSignal — Daily Stock Picks Generator
Runs via GitHub Actions every weekday at 9:15 AM ET.
Writes picks.json which the dashboard reads.
Optionally sends a Pushover push notification to your phone.

Focus: STOCK INVESTING only (buy shares, no options, no futures, no margin).
Timeframe: 3-14 days swing trades or multi-week position trades.
"""

import anthropic
import json
import datetime
import os
import requests

# ── Config ────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
PUSHOVER_TOKEN    = os.environ.get("PUSHOVER_TOKEN", "")
PUSHOVER_USER     = os.environ.get("PUSHOVER_USER", "")
DASHBOARD_URL     = "https://sspottabathula.github.io/alphasignal"
OUTPUT_FILE       = "picks.json"

# ── Prompt ────────────────────────────────────────────────────────────────────
today   = datetime.date.today().strftime("%A, %B %d, %Y")
now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

PROMPT = f"""Today is {today}. You are an expert stock market analyst specializing in swing trading and short-term stock investing.

Your job is to identify the TOP 3 US stocks to BUY (shares only - NO options, NO futures, NO margin) for the next 3-14 days.

Focus exclusively on:
- Buying and holding actual shares in a Robinhood account
- Realistic entry prices a retail investor can act on at market open
- Clear price targets and stop-loss levels in dollar terms
- Catalysts that will drive the stock price UP over the next 1-2 weeks

Look for stocks with:
- Upcoming earnings beats or strong guidance revisions
- FDA approvals, drug trial results, or biotech catalysts
- Positive analyst upgrades or price target raises
- Breakouts above key technical resistance levels
- Strong sector momentum (AI, energy, healthcare, etc.)
- Undervalued stocks with near-term re-rating potential

STRICT RULES:
- Only recommend buying shares (long positions) - no options, no puts, no calls, no shorts
- Timeframe must be 3 to 14 days (swing trade or short position trade)
- Entry must be a realistic limit or market-open price for a retail investor
- Risk level: High or Very High (these are aggressive picks for higher returns)
- All prices in USD

IMPORTANT: Respond ONLY with valid JSON. No markdown, no explanation, no code fences. Pure JSON only.

Use this exact structure:
{{
  "date": "{today}",
  "generated_at": "{now_utc}",
  "strategy": "Stock investing only - buy shares, no options",
  "market_summary": "One sentence macro backdrop under 25 words.",
  "market_sentiment": "bullish|neutral|bearish",
  "picks": [
    {{
      "rank": 1,
      "ticker": "NVDA",
      "name": "NVIDIA Corporation",
      "sector": "Technology",
      "thesis": "Specific reason this stock will go up in under 20 words.",
      "how_to_buy": "Buy X shares at market open / set limit order at $XXX",
      "entry_price": "$875.00",
      "entry_type": "Market order at open / Limit order",
      "shares_example": "Example: 10 shares = ~$8,750 investment",
      "exit_target": "$920.00",
      "stop_loss": "$855.00",
      "upside_pct": "+5.1%",
      "downside_risk": "-2.3%",
      "risk_reward": "2.2:1",
      "risk_level": "High",
      "hold_days": "5-7 days",
      "confidence": "74%",
      "catalyst": "Earnings beat / Analyst upgrade / Breakout / Sector momentum",
      "sell_when": "Sell all shares when price hits $920 or drops below $855 stop loss.",
      "robinhood_tip": "In Robinhood: search NVDA, tap Buy, select Shares, enter quantity, choose Market order."
    }},
    {{
      "rank": 2,
      "ticker": "TSLA",
      "name": "Tesla Inc.",
      "sector": "Consumer Discretionary",
      "thesis": "Specific reason this stock will go up in under 20 words.",
      "how_to_buy": "Buy X shares at market open / set limit order at $XXX",
      "entry_price": "$245.00",
      "entry_type": "Limit order",
      "shares_example": "Example: 20 shares = ~$4,900 investment",
      "exit_target": "$265.00",
      "stop_loss": "$235.00",
      "upside_pct": "+8.2%",
      "downside_risk": "-4.1%",
      "risk_reward": "2.0:1",
      "risk_level": "Very High",
      "hold_days": "3-5 days",
      "confidence": "61%",
      "catalyst": "Earnings beat / Analyst upgrade / Breakout / Sector momentum",
      "sell_when": "Sell all shares at $265 target or cut losses at $235.",
      "robinhood_tip": "In Robinhood: search TSLA, tap Buy, select Shares, set Limit order at $245."
    }},
    {{
      "rank": 3,
      "ticker": "MRNA",
      "name": "Moderna Inc.",
      "sector": "Healthcare",
      "thesis": "Specific reason this stock will go up in under 20 words.",
      "how_to_buy": "Buy X shares at market open / set limit order at $XXX",
      "entry_price": "$98.50",
      "entry_type": "Market order at open",
      "shares_example": "Example: 50 shares = ~$4,925 investment",
      "exit_target": "$108.00",
      "stop_loss": "$93.00",
      "upside_pct": "+9.6%",
      "downside_risk": "-5.6%",
      "risk_reward": "1.7:1",
      "risk_level": "Very High",
      "hold_days": "7-14 days",
      "confidence": "58%",
      "catalyst": "Earnings beat / Analyst upgrade / Breakout / Sector momentum",
      "sell_when": "Sell all shares when catalyst resolves or stop loss at $93 is hit.",
      "robinhood_tip": "In Robinhood: search MRNA, tap Buy, select Shares, enter quantity, choose Market order."
    }}
  ],
  "news_signals": [
    {{"headline": "Short headline under 12 words", "impact": "bullish", "ticker": "NVDA"}},
    {{"headline": "Short headline under 12 words", "impact": "bearish", "ticker": "SPY"}},
    {{"headline": "Short headline under 12 words", "impact": "bullish", "ticker": "TSLA"}}
  ],
  "risk_warning": "These are high-risk stock picks. Only invest money you can afford to lose. Buy shares only - no options."
}}"""


# ── Generate picks ─────────────────────────────────────────────────────────────
def generate_picks() -> dict:
    print(f"Generating stock picks for {today}...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": PROMPT}]
    )

    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    data = json.loads(raw)
    print(f"Generated {len(data.get('picks', []))} stock picks")
    return data


# ── Save to file ───────────────────────────────────────────────────────────────
def save_picks(data: dict):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {OUTPUT_FILE}")


# ── Phone notification (Pushover) ──────────────────────────────────────────────
def send_pushover(data: dict):
    if not PUSHOVER_TOKEN or not PUSHOVER_USER:
        print("Skipping Pushover (no credentials set)")
        return

    picks = data.get("picks", [])
    if not picks:
        return

    lines = [f"Today's market: {data.get('market_summary', '')}"]
    for p in picks:
        lines.append(
            f"\n#{p['rank']} {p['ticker']} - {p['upside_pct']} target\n"
            f"  Buy at: {p['entry_price']} | Sell at: {p['exit_target']} | Stop: {p['stop_loss']}\n"
            f"  Hold: {p['hold_days']} | {p['thesis']}"
        )

    payload = {
        "token":     PUSHOVER_TOKEN,
        "user":      PUSHOVER_USER,
        "title":     f"AlphaSignal Stock Picks - {today}",
        "message":   "\n".join(lines),
        "url":       DASHBOARD_URL,
        "url_title": "View full dashboard",
        "priority":  0,
        "sound":     "cashregister",
    }

    r = requests.post("https://api.pushover.net/1/messages.json", data=payload, timeout=10)
    if r.status_code == 200:
        print("Pushover notification sent")
    else:
        print(f"Pushover failed: {r.status_code} {r.text}")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    data = generate_picks()
    save_picks(data)
    send_pushover(data)
    print("Done.")
