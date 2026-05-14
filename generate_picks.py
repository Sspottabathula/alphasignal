"""
AlphaSignal v3 — Disciplined Stock Investor Daily Picks
NO OPTIONS. NO FUTURES. NO MARGIN. NO SHORTS.
BUY SHARES → HOLD → SELL SHARES. That is all.

Strategy: Only picks with >50% probability of hitting target.
Uses: momentum + earnings revision + sector rotation + support/resistance.
Timeframe: 5-21 days. Real prices. Real dates. Conservative targets.
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

today      = datetime.date.today()
today_str  = today.strftime("%A, %B %d, %Y")
now_utc    = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# Compute target dates (skip weekends)
def next_trading_day(d, n):
    """Return date n trading days from d."""
    cur = d
    count = 0
    while count < n:
        cur += datetime.timedelta(days=1)
        if cur.weekday() < 5:
            count += 1
    return cur

t5  = next_trading_day(today, 5).strftime("%B %d, %Y")   # ~1 week
t10 = next_trading_day(today, 10).strftime("%B %d, %Y")  # ~2 weeks
t15 = next_trading_day(today, 15).strftime("%B %d, %Y")  # ~3 weeks

PROMPT = f"""Today is {today_str}.

You are a disciplined professional stock investor with 30 years of experience.
You manage real money and are accountable for every recommendation.

=== ABSOLUTE RULES — NEVER VIOLATE ===
1. STOCKS ONLY. Recommend buying and selling SHARES of stock. 
   NEVER mention: calls, puts, options, contracts, strike price, expiry, 
   derivatives, futures, margin, leverage, short selling, or any derivative instrument.
   If you feel tempted to mention options — DON'T. Replace with the stock itself.
2. All prices must be REALISTIC current market prices as of {today_str}.
   Do NOT invent prices. Use your knowledge of recent stock prices.
   NVDA trades around $900-1100, AAPL around $170-200, TSLA around $170-280,
   AMZN around $180-210, META around $480-580, MSFT around $410-450, etc.
3. Every pick must have >50% probability of hitting the buy target within 3 days
   and >50% probability of hitting the sell target within the hold period.
   Be CONSERVATIVE. A 3-5% gain that is likely beats a 15% gain that is unlikely.
4. BUY PRICE: Set at or slightly below current price (0-2% below) so it is actionable.
5. SELL PRICE: Set conservatively at 3-8% above buy price for most picks.
   Only very high conviction picks get 8-15% targets.
6. STOP LOSS: Set at 2-5% below buy price. Tight stops = capital preservation.
7. Include a specific calendar date for: when to buy by, target sell date, stop date.
8. Number of picks: Generate between 5 and 15 picks.
   Only include a pick if you genuinely believe >50% probability of success.
   Do NOT pad with weak ideas. Quality over quantity.

=== YOUR ANALYSIS FRAMEWORK ===
For each stock, evaluate:
- PRICE MOMENTUM: Is the stock in an uptrend? Above 20-day and 50-day MA?
- EARNINGS REVISION: Have analysts raised estimates recently? Earnings beat last quarter?
- RELATIVE STRENGTH: Is this stock outperforming its sector and the S&P 500?
- VOLUME: Is there institutional accumulation? Rising volume on up days?
- CATALYST: Is there a specific upcoming event (earnings date, product launch, analyst day)?
- VALUATION: Is it reasonably valued or at least not dangerously overvalued?
- RISK: What specific event could cause it to drop? Is that risk likely?

=== CONSERVATIVE TARGET LOGIC ===
- Use resistance levels and recent highs as targets, not wishful thinking
- If a stock recently broke out of a range, target the measured move (range height added to breakout)
- Targets should be levels the stock has previously traded at or just above
- Stop losses should be at key support (recent swing low, MA, round number)

=== DATE GUIDANCE ===
- ~5 trading days from today = {t5}
- ~10 trading days from today = {t10}  
- ~15 trading days from today = {t15}
Use these dates in your recommendations.

RESPOND WITH ONLY VALID JSON. NO markdown. NO code fences. NO explanation. PURE JSON.

{{
  "date": "{today_str}",
  "generated_at": "{now_utc}",
  "analyst_note": "3-4 sentence honest market assessment. What is the S&P 500 doing? Which sectors are strong? What is the macro risk? Be specific and actionable, not generic.",
  "market_sentiment": "bullish|cautious_bullish|neutral|cautious_bearish|bearish",
  "market_summary": "One precise sentence: e.g. 'S&P 500 holding above 5,200 with tech leading; Fed pause narrative supporting risk assets but CPI data Thursday is a wildcard.'",
  "macro_backdrop": {{
    "fed_stance": "hawkish|neutral|dovish",
    "market_trend": "uptrend|downtrend|sideways",
    "volatility": "low|moderate|elevated|extreme",
    "key_risk": "The single most important risk to watch this week.",
    "sector_leaders": ["Technology", "Energy"],
    "sector_laggards": ["Utilities", "Real Estate"]
  }},
  "total_picks": 7,
  "picks": [
    {{
      "rank": 1,
      "conviction": "high",
      "ticker": "NVDA",
      "name": "NVIDIA Corporation",
      "sector": "Technology",
      "industry": "Semiconductors",
      "trade_type": "Swing Trade",
      "current_price": "$1,087.00",
      "thesis": "Two specific sentences: what is happening with this company RIGHT NOW and why the stock will go up. Reference actual recent news or earnings data.",
      "fundamental_view": "One sentence on earnings growth rate, revenue trajectory, or valuation metric that supports buying now.",
      "technical_setup": "One sentence: e.g. 'Holding above 50-day MA at $1,040; broke out of 3-week consolidation on above-average volume Tuesday.'",
      "catalyst": "Specific upcoming catalyst with actual date if known, e.g. 'Earnings report expected June 5; consensus EPS $5.82, whisper number higher.'",
      "buy_price": "$1,082.00",
      "buy_by_date": "{t5}",
      "buy_note": "Specific instruction: e.g. 'Set a limit buy order at $1,082. If stock opens above $1,090, wait for a pullback to $1,082 before entering.'",
      "sell_price": "$1,145.00",
      "sell_by_date": "{t10}",
      "sell_note": "Specific exit instruction: e.g. 'Place a limit sell order at $1,145. If stock hits $1,120 and stalls, consider taking partial profits.'",
      "stop_loss": "$1,048.00",
      "stop_date": "{t5}",
      "stop_note": "e.g. 'If stock closes below $1,048 (below 50-day MA), exit immediately regardless of news.'",
      "upside_pct": "+5.8%",
      "downside_risk": "-3.1%",
      "risk_reward": "1.9:1",
      "hold_days": "7-10 days",
      "confidence": "68%",
      "probability_of_target": "65%",
      "position_size_pct": "3% of portfolio",
      "dollar_examples": "$1,000 → 0 shares ($1,082 each) | $5,000 → 4 shares | $10,000 → 9 shares",
      "exit_plan": "Sell 50% at $1,145. Move stop up to $1,100 on remainder. Sell balance at $1,180 or stop.",
      "risk_factors": "Specific risk: e.g. 'Broader semiconductor sector selloff if SMCI earnings disappoint. Also watch for any China export restriction news.'",
      "robinhood_steps": "1. Search NVDA 2. Tap Buy 3. Select Shares 4. Change to Limit Order 5. Set price $1,082 6. Enter quantity 7. Set as Good Till Cancelled 8. Review and Submit"
    }}
  ],
  "stocks_considered_but_skipped": [
    {{"ticker": "TSLA", "reason": "Below 50-day MA, negative earnings revision trend. Risk/reward unfavorable."}}
  ],
  "market_watch": [
    {{
      "ticker": "SPY",
      "current_level": "$523",
      "key_level": "$518",
      "note": "Key support at $518 (50-day MA). Hold = bullish. Break = reduce exposure."
    }}
  ],
  "news_signals": [
    {{
      "headline": "Specific real headline under 12 words",
      "impact": "bullish",
      "ticker": "NVDA",
      "why": "One sentence on direct price impact and magnitude."
    }}
  ],
  "daily_wisdom": "A specific, actionable investing lesson relevant to today's market — not generic advice.",
  "risk_warning": "These are stock picks for informational purposes only. Not financial advice. Buy shares only — no options, no margin."
}}

def generate_picks() -> dict:
    print(f"Running disciplined stock analysis for {today_str}...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8000,
        system="""You are a disciplined professional stock investor.
You ONLY recommend buying and selling shares of stock.
You NEVER mention options, calls, puts, contracts, strike prices, expiry dates, derivatives, futures, or margin.
Every price you quote must be a realistic current market price.
Every recommendation must have >50% probability of success.
You respond ONLY with valid JSON.""",
        messages=[{"role": "user", "content": PROMPT}]
    )

    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    # Find JSON object
    start = raw.find('{')
    end   = raw.rfind('}') + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    data = json.loads(raw)
    picks = data.get("picks", [])
    print(f"Generated {len(picks)} stock picks:")
    for p in picks:
        print(f"  #{p['rank']} {p['ticker']:6s} | Buy {p['buy_price']:>10} → Sell {p['sell_price']:>10} | Stop {p['stop_loss']:>10} | {p['upside_pct']} | {p['probability_of_target']} prob | {p['hold_days']}")
    skipped = data.get("stocks_considered_but_skipped", [])
    if skipped:
        print(f"  Skipped {len(skipped)} stocks: {', '.join(s['ticker'] for s in skipped)}")
    return data


def save_picks(data: dict):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved → {OUTPUT_FILE}")


def send_pushover(data: dict):
    if not PUSHOVER_TOKEN or not PUSHOVER_USER:
        print("Pushover not configured — skipping")
        return
    picks = data.get("picks", [])
    if not picks:
        return

    hi = [p for p in picks if p.get("conviction") == "high"]
    lines = [
        f"Market: {data.get('market_summary', '')}",
        f"{len(picks)} picks | {len(hi)} high conviction\n"
    ]
    for p in picks[:6]:
        icon = {"high":"🟢","medium":"🔵","speculative":"🟣"}.get(p.get("conviction",""), "⚪")
        lines.append(
            f"{icon} {p['ticker']} — Buy {p['buy_price']} → Sell {p['sell_price']}\n"
            f"   Stop: {p['stop_loss']} | {p['upside_pct']} | ~{p['hold_days']} | {p.get('probability_of_target','?')} prob"
        )
    if len(picks) > 6:
        lines.append(f"\n...+{len(picks)-6} more on dashboard")
    lines.append(f'\n"{data.get("daily_wisdom","")}"')

    r = requests.post("https://api.pushover.net/1/messages.json", data={
        "token": PUSHOVER_TOKEN, "user": PUSHOVER_USER,
        "title": f"AlphaSignal — {len(picks)} Picks | {today_str}",
        "message": "\n".join(lines),
        "url": DASHBOARD_URL, "url_title": "Full dashboard",
        "priority": 0, "sound": "cashregister",
    }, timeout=10)
    print("Pushover sent" if r.status_code == 200 else f"Pushover failed: {r.status_code}")


if __name__ == "__main__":
    data = generate_picks()
    save_picks(data)
    send_pushover(data)
    print("Done.")
