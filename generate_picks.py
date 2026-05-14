"""
AlphaSignal — Expert Investor Daily Stock Analysis
Modeled on 30 years of professional investing experience.
Combines: macro analysis, fundamental screening, technical setup,
sector rotation, risk/reward discipline, and position sizing.

Runs via GitHub Actions every weekday at 9:15 AM ET.
Generates 3-20 picks depending on market opportunity quality.
"""

import anthropic
import json
import datetime
import os
import requests

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
PUSHOVER_TOKEN    = os.environ.get("PUSHOVER_TOKEN", "")
PUSHOVER_USER     = os.environ.get("PUSHOVER_USER", "")
DASHBOARD_URL     = "https://sspottabathula.github.io/alphasignal"
OUTPUT_FILE       = "picks.json"

today   = datetime.date.today().strftime("%A, %B %d, %Y")
now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

PROMPT = f"""Today is {today}.

You are a seasoned professional investor with 30 years of active market experience across bull markets, bear markets, the dot-com crash, 2008 financial crisis, COVID crash, and multiple Fed cycles. You have managed portfolios worth hundreds of millions of dollars.

Your daily process combines:
1. TOP-DOWN MACRO: Fed policy, rates, inflation, dollar, global flows
2. SECTOR ROTATION: Which sectors are seeing institutional accumulation vs distribution
3. FUNDAMENTAL SCREENING: Earnings revisions, revenue growth, margin expansion, free cash flow
4. TECHNICAL SETUP: Price action, volume, moving averages, support/resistance, momentum
5. CATALYST IDENTIFICATION: Earnings, FDA events, analyst days, product launches, regulatory decisions
6. RISK/REWARD DISCIPLINE: Never recommend a trade without clear entry, stop, and target
7. CONVICTION SIZING: High-conviction ideas get more capital; speculative ideas get less

Today, scan the full US equity market and identify ALL stocks with a compelling setup for the next 3-21 days. Be selective but not artificially limited — generate between 3 and 20 picks depending on genuine market opportunity. In a strong trending market you may find 15-20 setups; in choppy conditions maybe only 3-5.

For EACH pick, apply this professional framework:
- Is the risk/reward at least 2:1? (target gain must be 2x the stop-loss distance)
- Is there a specific catalyst or technical trigger?
- What does the chart say? (trend, volume, key levels)
- What is the fundamental backdrop? (earnings growth, sector health)
- How much capital should a retail investor allocate? (position sizing)
- What exactly invalidates the thesis? (stop loss reasoning)

INVESTMENT TYPES to consider:
- Swing trades (3-7 days): momentum plays, earnings catalysts, technical breakouts
- Position trades (2-4 weeks): fundamental re-ratings, sector rotations, post-earnings drifts
- Special situations: FDA readouts, M&A rumors, activist involvement, short squeezes
- Defensive plays: if market is bearish, include some safer large-cap ideas with lower risk

BUY SHARES ONLY. No options, no margin, no shorts. Retail-friendly.

IMPORTANT: Respond ONLY with valid JSON. No markdown, no explanation, no code fences. Pure JSON only.

{{
  "date": "{today}",
  "generated_at": "{now_utc}",
  "analyst_note": "2-3 sentence professional market read. What is the market doing today and why. What is your overall posture.",
  "macro_backdrop": {{
    "fed_stance": "hawkish|neutral|dovish",
    "market_trend": "uptrend|downtrend|sideways",
    "volatility": "low|moderate|elevated|extreme",
    "sector_leaders": ["Sector1", "Sector2"],
    "sector_laggards": ["Sector1", "Sector2"],
    "key_risk": "The single biggest market risk right now in one sentence."
  }},
  "market_sentiment": "bullish|cautious_bullish|neutral|cautious_bearish|bearish",
  "market_summary": "One crisp sentence on today's market environment.",
  "total_picks": 5,
  "picks": [
    {{
      "rank": 1,
      "conviction": "high|medium|speculative",
      "ticker": "NVDA",
      "name": "NVIDIA Corporation",
      "sector": "Technology",
      "industry": "Semiconductors",
      "trade_type": "Swing Trade|Position Trade|Special Situation|Defensive",
      "thesis": "Precise 2-sentence investment thesis. What is the catalyst and why will this stock go up.",
      "fundamental_view": "One sentence on earnings, revenue growth, or valuation that supports the thesis.",
      "technical_setup": "One sentence on the chart — trend, key level, volume signal.",
      "catalyst": "Specific upcoming catalyst with approximate timing.",
      "entry_price": "$875.00",
      "entry_strategy": "Buy at market open / Limit order at $875 / Buy on pullback to $860 support",
      "position_size": "2-3% of portfolio (high conviction) / 1-2% of portfolio (medium) / 0.5-1% (speculative)",
      "dollar_example": "$500 account: X shares | $1,000 account: X shares | $5,000 account: X shares",
      "exit_target_1": "$920.00",
      "exit_target_2": "$950.00",
      "stop_loss": "$855.00",
      "stop_reasoning": "One sentence explaining why this level invalidates the thesis.",
      "upside_pct": "+5.1%",
      "upside_pct_t2": "+8.6%",
      "downside_risk": "-2.3%",
      "risk_reward": "2.2:1",
      "hold_days": "5-7 days",
      "confidence": "74%",
      "exit_plan": "Sell 50% at target 1, let rest run to target 2. Exit all if stop is hit.",
      "risk_factors": "One sentence on what could go wrong.",
      "robinhood_action": "Exact step-by-step: Search NVDA → Buy → Shares → Qty X → Limit $875 → Day order → Review → Submit"
    }}
  ],
  "market_watch": [
    {{
      "ticker": "SPY",
      "note": "Watch this level — key support/resistance that matters today.",
      "level": "$520"
    }}
  ],
  "news_signals": [
    {{"headline": "Concise headline under 12 words", "impact": "bullish", "ticker": "NVDA", "why": "One sentence on why this matters"}},
    {{"headline": "Concise headline under 12 words", "impact": "bearish", "ticker": "SPY", "why": "One sentence on why this matters"}},
    {{"headline": "Concise headline under 12 words", "impact": "bullish", "ticker": "TSLA", "why": "One sentence on why this matters"}}
  ],
  "daily_wisdom": "One sentence of hard-won investing wisdom relevant to today's market conditions.",
  "risk_warning": "These are high-risk stock picks for informational purposes only. Not financial advice. Only invest money you can afford to lose."
}}"""


def generate_picks() -> dict:
    print(f"Running expert analysis for {today}...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8000,
        messages=[{"role": "user", "content": PROMPT}]
    )

    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    data = json.loads(raw)
    n = len(data.get("picks", []))
    print(f"Generated {n} picks (conviction breakdown follows)")
    for p in data.get("picks", []):
        print(f"  #{p['rank']} {p['ticker']} — {p['conviction']} conviction — {p['upside_pct']} target — {p['hold_days']}")
    return data


def save_picks(data: dict):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {OUTPUT_FILE}")


def send_pushover(data: dict):
    if not PUSHOVER_TOKEN or not PUSHOVER_USER:
        print("Skipping Pushover (no credentials set)")
        return

    picks = data.get("picks", [])
    if not picks:
        return

    high   = [p for p in picks if p.get("conviction") == "high"]
    medium = [p for p in picks if p.get("conviction") == "medium"]
    spec   = [p for p in picks if p.get("conviction") == "speculative"]

    lines = [
        f"Market: {data.get('market_summary', '')}",
        f"{len(picks)} picks today ({len(high)} high / {len(medium)} medium / {len(spec)} speculative)\n"
    ]

    for p in picks[:5]:
        icon = "🟢" if p.get("conviction") == "high" else "🟡" if p.get("conviction") == "medium" else "🔵"
        lines.append(
            f"{icon} {p['ticker']} {p['upside_pct']} ({p['hold_days']})\n"
            f"   Buy: {p['entry_price']} | Target: {p['exit_target_1']} | Stop: {p['stop_loss']}"
        )

    if len(picks) > 5:
        lines.append(f"\n...and {len(picks)-5} more picks on dashboard")

    lines.append(f"\n\"{data.get('daily_wisdom', '')}\"")

    payload = {
        "token":     PUSHOVER_TOKEN,
        "user":      PUSHOVER_USER,
        "title":     f"AlphaSignal — {len(picks)} Picks Ready ({today})",
        "message":   "\n".join(lines),
        "url":       DASHBOARD_URL,
        "url_title": "View full analysis",
        "priority":  0,
        "sound":     "cashregister",
    }

    r = requests.post("https://api.pushover.net/1/messages.json", data=payload, timeout=10)
    if r.status_code == 200:
        print("Pushover sent")
    else:
        print(f"Pushover failed: {r.status_code} {r.text}")


if __name__ == "__main__":
    data = generate_picks()
    save_picks(data)
    send_pushover(data)
    print("Done.")
