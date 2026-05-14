"""
AlphaSignal v3 - Disciplined Stock Investor Daily Picks
NO OPTIONS. NO FUTURES. NO MARGIN. NO SHORTS.
BUY SHARES -> HOLD -> SELL SHARES. That is all.

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

today     = datetime.date.today()
today_str = today.strftime("%A, %B %d, %Y")
now_utc   = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def next_trading_day(d, n):
    """Return date n trading days from d, skipping weekends."""
    cur = d
    count = 0
    while count < n:
        cur += datetime.timedelta(days=1)
        if cur.weekday() < 5:
            count += 1
    return cur


t5  = next_trading_day(today,  5).strftime("%B %d, %Y")
t10 = next_trading_day(today, 10).strftime("%B %d, %Y")
t15 = next_trading_day(today, 15).strftime("%B %d, %Y")


SYSTEM_PROMPT = (
    "You are a disciplined professional stock investor with 30 years of experience. "
    "You ONLY recommend buying and selling shares of stock. "
    "You NEVER mention: options, calls, puts, contracts, strike prices, expiry dates, "
    "derivatives, futures, margin, leverage, short selling, or any derivative instrument. "
    "Every price you quote must be a realistic current market price as of today. "
    "Every recommendation must have greater than 50 percent probability of success. "
    "You respond ONLY with valid JSON and nothing else."
)


def build_prompt():
    """Build the analysis prompt with today's dates baked in."""

    json_example = (
        '{\n'
        '  "date": "' + today_str + '",\n'
        '  "generated_at": "' + now_utc + '",\n'
        '  "analyst_note": "3-4 sentences. What is the S&P 500 doing today? Which sectors lead? Key macro risk? Be specific with index levels.",\n'
        '  "market_sentiment": "bullish|cautious_bullish|neutral|cautious_bearish|bearish",\n'
        '  "market_summary": "One precise sentence with specific index levels and what is driving the market today.",\n'
        '  "macro_backdrop": {\n'
        '    "fed_stance": "hawkish|neutral|dovish",\n'
        '    "market_trend": "uptrend|downtrend|sideways",\n'
        '    "volatility": "low|moderate|elevated|extreme",\n'
        '    "key_risk": "The single most important risk to watch this week.",\n'
        '    "sector_leaders": ["Technology", "Energy"],\n'
        '    "sector_laggards": ["Utilities", "Real Estate"]\n'
        '  },\n'
        '  "total_picks": 7,\n'
        '  "picks": [\n'
        '    {\n'
        '      "rank": 1,\n'
        '      "conviction": "high",\n'
        '      "ticker": "NVDA",\n'
        '      "name": "NVIDIA Corporation",\n'
        '      "sector": "Technology",\n'
        '      "industry": "Semiconductors",\n'
        '      "trade_type": "Swing Trade",\n'
        '      "current_price": "$1087.00",\n'
        '      "thesis": "Two specific sentences about what is happening with this company RIGHT NOW and why the stock will go up. Reference actual recent news or earnings data.",\n'
        '      "fundamental_view": "One sentence on earnings growth rate, revenue trajectory, or valuation metric supporting buying now.",\n'
        '      "technical_setup": "One sentence: trend direction, key moving average level, volume signal.",\n'
        '      "catalyst": "Specific upcoming catalyst with approximate date if known.",\n'
        '      "buy_price": "$1082.00",\n'
        '      "buy_by_date": "' + t5 + '",\n'
        '      "buy_note": "Specific instruction: e.g. Set a limit buy order at $1082. If stock opens above $1090, wait for a pullback before entering.",\n'
        '      "sell_price": "$1145.00",\n'
        '      "sell_by_date": "' + t10 + '",\n'
        '      "sell_note": "Specific exit instruction including whether to take partial profits.",\n'
        '      "stop_loss": "$1048.00",\n'
        '      "stop_date": "' + t5 + '",\n'
        '      "stop_note": "If stock closes below $1048 (below 50-day MA), exit immediately. This level invalidates the thesis.",\n'
        '      "upside_pct": "+5.8%",\n'
        '      "downside_risk": "-3.1%",\n'
        '      "risk_reward": "1.9:1",\n'
        '      "hold_days": "7-10 days",\n'
        '      "confidence": "68%",\n'
        '      "probability_of_target": "65%",\n'
        '      "position_size_pct": "3% of portfolio",\n'
        '      "dollar_examples": "$1000 account: 0 shares | $5000 account: 4 shares | $10000 account: 9 shares",\n'
        '      "exit_plan": "Sell 50% at sell target. Move stop to breakeven on remainder. Sell balance at target 2 or stop.",\n'
        '      "risk_factors": "Specific risk that could cause this trade to fail.",\n'
        '      "robinhood_steps": "1. Search NVDA  2. Tap Buy  3. Select Shares  4. Change to Limit Order  5. Set price $1082  6. Enter quantity  7. Set Good Till Cancelled  8. Submit"\n'
        '    }\n'
        '  ],\n'
        '  "stocks_considered_but_skipped": [\n'
        '    {"ticker": "TSLA", "reason": "Below 50-day MA with negative earnings revision trend. Risk/reward unfavorable."}\n'
        '  ],\n'
        '  "market_watch": [\n'
        '    {\n'
        '      "ticker": "SPY",\n'
        '      "current_level": "$523",\n'
        '      "key_level": "$518",\n'
        '      "note": "Key support at $518 (50-day MA). Hold = bullish. Break = reduce all exposure."\n'
        '    }\n'
        '  ],\n'
        '  "news_signals": [\n'
        '    {"headline": "Specific real headline under 12 words", "impact": "bullish", "ticker": "NVDA", "why": "One sentence on direct price impact."}\n'
        '  ],\n'
        '  "daily_wisdom": "A specific actionable investing lesson relevant to today\'s market conditions.",\n'
        '  "risk_warning": "These are stock picks for informational purposes only. Not financial advice. Buy shares only."\n'
        '}'
    )

    prompt = (
        "Today is " + today_str + ".\n\n"
        "You are a seasoned professional investor with 30 years of active market experience.\n\n"
        "=== ABSOLUTE RULES - NEVER VIOLATE ===\n"
        "1. STOCKS ONLY. Recommend buying and selling SHARES of stock.\n"
        "   FORBIDDEN WORDS: calls, puts, options, contracts, strike price, expiry,\n"
        "   derivatives, futures, margin, leverage, short selling.\n"
        "   If you feel like mentioning any of those words - DO NOT. Recommend the stock instead.\n\n"
        "2. REALISTIC PRICES. Use your knowledge of current stock prices as of today.\n"
        "   Reference price ranges: NVDA ~$900-1100, AAPL ~$170-200, TSLA ~$170-280,\n"
        "   AMZN ~$180-210, META ~$480-580, MSFT ~$410-450, GOOGL ~$160-180,\n"
        "   AMD ~$150-180, PLTR ~$80-120, SPY ~$510-540.\n"
        "   Do NOT invent prices far outside these ranges.\n\n"
        "3. GREATER THAN 50 PERCENT PROBABILITY. Only include picks you genuinely believe\n"
        "   have more than 50% chance of hitting the target. Be conservative.\n"
        "   A 4% gain that is likely beats a 20% gain that is unlikely.\n\n"
        "4. CONSERVATIVE TARGETS. Set sell prices at 3-8% above buy for most picks.\n"
        "   Only exceptional setups get 10-15% targets.\n"
        "   Targets must be at prior resistance or recent highs - not random numbers.\n\n"
        "5. TIGHT STOPS. Stop loss at 2-5% below buy price.\n"
        "   Stop must be at a key technical level (support, moving average, round number).\n\n"
        "6. SPECIFIC DATES for every pick:\n"
        "   ~5 trading days from today = " + t5 + "\n"
        "   ~10 trading days from today = " + t10 + "\n"
        "   ~15 trading days from today = " + t15 + "\n\n"
        "7. PICK COUNT. Generate 5 to 15 picks based on genuine opportunity.\n"
        "   Do NOT pad with weak ideas. Quality beats quantity.\n\n"
        "=== ANALYSIS FRAMEWORK ===\n"
        "For each stock evaluate: price momentum, earnings revisions, relative strength,\n"
        "institutional volume, upcoming catalyst, and risk/reward (minimum 1.5:1).\n\n"
        "RESPOND WITH ONLY VALID JSON. No markdown. No explanation. No code fences.\n\n"
        + json_example
    )

    return prompt


def generate_picks() -> dict:
    print(f"Running disciplined stock analysis for {today_str}...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt()}]
    )

    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    # Extract JSON object robustly
    start = raw.find('{')
    end   = raw.rfind('}') + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    data = json.loads(raw)
    picks = data.get("picks", [])

    print(f"Generated {len(picks)} picks:")
    for p in picks:
        ticker = str(p.get('ticker', '?')).ljust(6)
        buy    = str(p.get('buy_price',  '?')).rjust(12)
        sell   = str(p.get('sell_price', '?')).rjust(12)
        stop   = str(p.get('stop_loss',  '?')).rjust(12)
        up     = str(p.get('upside_pct', '?')).rjust(7)
        prob   = str(p.get('probability_of_target', '?')).rjust(5)
        days   = str(p.get('hold_days',  '?'))
        print(f"  #{p.get('rank','?')} {ticker} | Buy {buy} -> Sell {sell} | Stop {stop} | {up} | {prob} prob | {days}")

    skipped = data.get("stocks_considered_but_skipped", [])
    if skipped:
        print(f"  Skipped: {', '.join(s.get('ticker', '?') for s in skipped)}")

    return data


def save_picks(data: dict):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {OUTPUT_FILE}")


def send_pushover(data: dict):
    if not PUSHOVER_TOKEN or not PUSHOVER_USER:
        print("Pushover not configured - skipping")
        return

    picks = data.get("picks", [])
    if not picks:
        return

    hi = [p for p in picks if p.get("conviction") == "high"]
    me = [p for p in picks if p.get("conviction") == "medium"]
    sp = [p for p in picks if p.get("conviction") == "speculative"]

    lines = [
        data.get("market_summary", ""),
        f"{len(picks)} picks: {len(hi)} high / {len(me)} medium / {len(sp)} speculative\n"
    ]

    for p in picks[:6]:
        icon = {"high": "[HIGH]", "medium": "[MED]", "speculative": "[SPEC]"}.get(
            p.get("conviction", ""), "")
        bd = str(p.get('buy_by_date',  '?'))[:6]
        sd = str(p.get('sell_by_date', '?'))[:6]
        lines.append(
            f"{icon} {p.get('ticker')} | "
            f"Buy {p.get('buy_price')} by {bd} | "
            f"Sell {p.get('sell_price')} by {sd} | "
            f"Stop {p.get('stop_loss')} | "
            f"{p.get('upside_pct')} | {p.get('probability_of_target', '?')} prob"
        )

    if len(picks) > 6:
        lines.append(f"...and {len(picks) - 6} more on dashboard")

    wisdom = data.get("daily_wisdom", "")
    if wisdom:
        lines.append(f'\n"{wisdom}"')

    r = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token":     PUSHOVER_TOKEN,
            "user":      PUSHOVER_USER,
            "title":     f"AlphaSignal - {len(picks)} Picks | {today_str}",
            "message":   "\n".join(lines),
            "url":       DASHBOARD_URL,
            "url_title": "View full dashboard",
            "priority":  0,
            "sound":     "cashregister",
        },
        timeout=10
    )

    if r.status_code == 200:
        print("Pushover notification sent")
    else:
        print(f"Pushover failed: {r.status_code} - {r.text}")


if __name__ == "__main__":
    data = generate_picks()
    save_picks(data)
    send_pushover(data)
    print("Done.")
