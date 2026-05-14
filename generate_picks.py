"""
AlphaSignal v4 - HIGH RISK / HIGH RETURN Aggressive Stock Picks
Target: 10-40% gains in 3-14 days on volatile, catalyst-driven stocks.
Focus: Biotech, small/mid-cap momentum, earnings plays, short squeezes,
       breakouts, sector hot-money rotations, IPO momentum.
NO OPTIONS. BUY SHARES ONLY.
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
    cur, count = d, 0
    while count < n:
        cur += datetime.timedelta(days=1)
        if cur.weekday() < 5:
            count += 1
    return cur


t3  = next_trading_day(today,  3).strftime("%B %d, %Y")
t5  = next_trading_day(today,  5).strftime("%B %d, %Y")
t10 = next_trading_day(today, 10).strftime("%B %d, %Y")
t14 = next_trading_day(today, 14).strftime("%B %d, %Y")


SYSTEM_PROMPT = (
    "You are an aggressive short-term stock trader with 30 years of experience "
    "specializing in high-volatility, high-return opportunities. "
    "You focus on biotech binary events, momentum breakouts, short squeezes, "
    "earnings surprises, and small-cap catalysts that can move 15-50% in days. "
    "You ONLY recommend buying and selling SHARES of stock. "
    "You NEVER mention: options, calls, puts, contracts, strike prices, expiry, "
    "derivatives, futures, margin, leverage, or short selling. "
    "All prices must be realistic current market prices. "
    "You respond ONLY with valid JSON and nothing else."
)


def build_prompt():

    json_example = (
        '{\n'
        '  "date": "' + today_str + '",\n'
        '  "generated_at": "' + now_utc + '",\n'
        '  "strategy": "High Risk / High Return - Aggressive Short-Term Stock Picks",\n'
        '  "analyst_note": "3-4 sentences on which aggressive themes have the hottest momentum today. Name specific sectors, catalysts, and market conditions creating opportunity. Be specific - reference actual recent moves.",\n'
        '  "market_sentiment": "risk-on|cautious-risk-on|neutral|risk-off",\n'
        '  "market_summary": "One sentence on overall risk appetite and which aggressive themes are working today.",\n'
        '  "macro_backdrop": {\n'
        '    "risk_appetite": "high|moderate|low",\n'
        '    "hot_themes": ["AI/Chips", "Biotech FDA", "Short Squeeze"],\n'
        '    "market_trend": "uptrend|downtrend|sideways",\n'
        '    "volatility": "low|moderate|elevated|extreme",\n'
        '    "key_risk": "Biggest risk that could kill momentum this week.",\n'
        '    "sector_leaders": ["Biotech", "Semiconductors"],\n'
        '    "sector_laggards": ["Utilities", "Consumer Staples"]\n'
        '  },\n'
        '  "total_picks": 8,\n'
        '  "picks": [\n'
        '    {\n'
        '      "rank": 1,\n'
        '      "conviction": "high",\n'
        '      "ticker": "MSTR",\n'
        '      "name": "MicroStrategy Inc.",\n'
        '      "sector": "Technology",\n'
        '      "industry": "Bitcoin Proxy / Software",\n'
        '      "trade_type": "Momentum Breakout",\n'
        '      "why_high_risk_high_return": "High beta to BTC, volatile, can move 15-30% in a week on BTC momentum.",\n'
        '      "current_price": "$185.00",\n'
        '      "thesis": "Two sentences: what specific catalyst or momentum setup makes this stock likely to explode higher in the next 3-14 days. Name the actual trigger.",\n'
        '      "technical_setup": "Describe the chart setup: breakout level, volume surge, moving average position, momentum indicator.",\n'
        '      "catalyst": "Exact catalyst: e.g. FDA PDUFA date May 20, earnings May 22, BTC breakout above $70k, short squeeze building with 25% SI.",\n'
        '      "catalyst_date": "' + t5 + '",\n'
        '      "pre_catalyst_buy": true,\n'
        '      "buy_price": "$183.00",\n'
        '      "buy_by_date": "' + t3 + '",\n'
        '      "buy_note": "Exact entry instruction. e.g. Place limit order at $183. Enter before catalyst date. Do not chase above $190.",\n'
        '      "sell_price_conservative": "$205.00",\n'
        '      "sell_price_aggressive": "$225.00",\n'
        '      "sell_by_date": "' + t10 + '",\n'
        '      "sell_note": "Exact exit: e.g. Sell 50% at $205 (conservative). Let rest run to $225 if momentum holds. Exit ALL before catalyst if uncertain.",\n'
        '      "stop_loss": "$170.00",\n'
        '      "stop_date": "' + t3 + '",\n'
        '      "stop_note": "If stock closes below $170 (key support), exit immediately. Do not hold through breakdown.",\n'
        '      "upside_conservative": "+12.0%",\n'
        '      "upside_aggressive": "+22.9%",\n'
        '      "downside_risk": "-7.1%",\n'
        '      "risk_reward_conservative": "1.7:1",\n'
        '      "risk_reward_aggressive": "3.2:1",\n'
        '      "hold_days": "3-7 days",\n'
        '      "confidence": "65%",\n'
        '      "probability_of_target": "60%",\n'
        '      "volatility_profile": "Very High - can move 10%+ in a single day",\n'
        '      "market_cap": "Mid-cap $5B",\n'
        '      "short_interest": "18% of float",\n'
        '      "position_size_pct": "1-2% of portfolio MAX - this is aggressive",\n'
        '      "dollar_examples": "$1000: 5 shares | $5000: 27 shares | $10000: 54 shares",\n'
        '      "exit_plan": "Sell half at conservative target. Trail stop on rest. Never let a winner turn into a loss - move stop to breakeven after 8% gain.",\n'
        '      "risk_factors": "Specific risks: e.g. BTC drops below $60k kills this trade. Broader risk-off would hit hard. Very thin liquidity.",\n'
        '      "warning": "HIGH RISK: This stock can lose 15-20% as fast as it gains. Size position accordingly.",\n'
        '      "robinhood_steps": "1. Search ticker  2. Tap Buy  3. Select Shares  4. Limit Order  5. Set price  6. Enter qty  7. Good Till Cancelled  8. Submit"\n'
        '    }\n'
        '  ],\n'
        '  "top_biotech_watch": [\n'
        '    {"ticker": "XXXX", "catalyst": "FDA PDUFA date", "date": "' + t10 + '", "note": "Binary event - stock could double or halve. Small position only."}\n'
        '  ],\n'
        '  "short_squeeze_radar": [\n'
        '    {"ticker": "XXXX", "short_interest": "35% of float", "days_to_cover": "4.2", "note": "Any positive news could ignite a squeeze."}\n'
        '  ],\n'
        '  "stocks_avoided_today": [\n'
        '    {"ticker": "AAPL", "reason": "Large cap, low volatility, 2% annual mover. Wrong tool for high-return strategy."}\n'
        '  ],\n'
        '  "market_watch": [\n'
        '    {"ticker": "IWM", "current_level": "$210", "key_level": "$205", "note": "Small cap proxy. Above $205 = risk-on for high beta names."}\n'
        '  ],\n'
        '  "news_signals": [\n'
        '    {"headline": "Real headline driving high-beta stocks today", "impact": "bullish", "ticker": "MSTR", "why": "Direct price impact explanation."}\n'
        '  ],\n'
        '  "daily_wisdom": "An aggressive trader wisdom quote relevant to today - about cutting losses fast, riding momentum, or position sizing.",\n'
        '  "risk_warning": "EXTREME RISK: These are highly speculative stocks that can lose 20-50% rapidly. Only invest money you can afford to lose completely. Not financial advice. Buy shares only."\n'
        '}'
    )

    prompt = (
        "Today is " + today_str + ".\n\n"

        "You are an aggressive short-term trader hunting for HIGH RISK / HIGH RETURN stock plays.\n\n"

        "=== YOUR MANDATE ===\n"
        "Find stocks that can move 15-40% in the next 3-14 days.\n"
        "These are NOT safe, stable investments. These are aggressive momentum plays.\n"
        "The investor knows these are risky and WANTS them anyway.\n\n"

        "=== WHAT TO LOOK FOR ===\n"
        "BIOTECH BINARY EVENTS:\n"
        "  - FDA PDUFA dates in the next 2-3 weeks (drug approval decisions)\n"
        "  - Phase 2/3 clinical trial readouts expected soon\n"
        "  - Small/mid-cap biotech with $500M-$5B market cap (not Pfizer/JNJ)\n"
        "  - Stocks that could double on approval or drop 50% on failure\n\n"
        "MOMENTUM BREAKOUTS:\n"
        "  - Stocks breaking out of multi-week consolidation on high volume\n"
        "  - AI/semiconductor names with strong earnings revisions\n"
        "  - Stocks hitting 52-week highs with institutional buying\n"
        "  - High-beta tech names (NVDA, AMD, MSTR, PLTR, SMCI, IONQ, RKLB)\n\n"
        "SHORT SQUEEZE SETUPS:\n"
        "  - High short interest (above 20% of float)\n"
        "  - Low days-to-cover with positive catalyst upcoming\n"
        "  - Recent short squeeze momentum (GME-style but smaller)\n\n"
        "EARNINGS SURPRISE PLAYS:\n"
        "  - Companies reporting earnings in next 5-10 days with beat potential\n"
        "  - Low analyst estimates vs strong sector trends\n"
        "  - Post-earnings drift on strong beats (buy dip after big gap up)\n\n"
        "HOT SECTOR MOMENTUM:\n"
        "  - Whatever sector has the hottest institutional money flow today\n"
        "  - AI infrastructure, quantum computing, defense tech, space, nuclear energy\n"
        "  - Names that haven't moved yet but peers already have\n\n"
        "SPECIFIC STOCK UNIVERSE TO CONSIDER (high beta, volatile names):\n"
        "  Biotech: SAVA, MDGL, ACAD, IONS, ARWR, VKTX, GILD, MRNA, BNTX, NVAX\n"
        "  AI/Chips: NVDA, AMD, SMCI, MRVL, AVGO, PLTR, AI, SOUN, IONQ, RKLB\n"
        "  Momentum: MSTR, COIN, HOOD, UPST, SOFI, AFRM, RDFN, OPEN\n"
        "  Squeeze candidates: Check highest short interest list\n"
        "  Small cap momentum: Whatever is in the top movers list this week\n\n"

        "=== ABSOLUTE RULES ===\n"
        "1. SHARES ONLY. Never mention options, calls, puts, contracts, strike price,\n"
        "   expiry, derivatives, futures, margin, or leverage. BUY SHARES, SELL SHARES.\n\n"
        "2. REAL PRICES. Use realistic current prices.\n"
        "   NVDA ~$900-1100, AMD ~$150-180, PLTR ~$80-120, MSTR ~$350-500,\n"
        "   COIN ~$200-280, SMCI ~$35-60, SOUN ~$8-15, IONQ ~$25-45, RKLB ~$18-28.\n"
        "   Biotech small caps vary widely - use reasonable estimates.\n\n"
        "3. TWO PRICE TARGETS per pick:\n"
        "   - Conservative target: 10-20% gain (more likely, take partial profits)\n"
        "   - Aggressive target: 25-50% gain (if momentum is strong, let it ride)\n\n"
        "4. TIGHT STOPS at 5-10% below entry (high volatility means wider stops).\n\n"
        "5. SPECIFIC DATES:\n"
        "   ~3 trading days = " + t3 + "\n"
        "   ~5 trading days = " + t5 + "\n"
        "   ~10 trading days = " + t10 + "\n"
        "   ~14 trading days = " + t14 + "\n\n"
        "6. SMALL POSITION SIZES. These are risky. Suggest 1-2% of portfolio max per pick.\n\n"
        "7. Generate 6 to 15 picks. Include biotech, momentum, and squeeze plays.\n"
        "   Include top_biotech_watch and short_squeeze_radar sections.\n\n"
        "8. EXPLICITLY AVOID: AAPL, MSFT, GOOGL, AMZN, BRK.B, JNJ, PG, KO, XOM\n"
        "   (These are stable large caps - wrong tool for this strategy)\n\n"

        "RESPOND WITH ONLY VALID JSON. No markdown. No explanation. No code fences.\n\n"
        + json_example
    )

    return prompt


def generate_picks() -> dict:
    print(f"Scanning for HIGH RISK / HIGH RETURN plays for {today_str}...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt()}]
    )

    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    start = raw.find('{')
    end   = raw.rfind('}') + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    data = json.loads(raw)
    picks = data.get("picks", [])

    print(f"\nGenerated {len(picks)} aggressive picks:")
    print(f"{'#':<3} {'Ticker':<7} {'Buy':>10} {'Cons.Target':>12} {'Aggr.Target':>12} {'Stop':>10} {'Upside(C)':>10} {'Prob':>6} {'Days'}")
    print("-" * 90)
    for p in picks:
        print(
            f"  #{str(p.get('rank','?')):<2} "
            f"{str(p.get('ticker','?')):<7} "
            f"{str(p.get('buy_price','?')):>10} "
            f"{str(p.get('sell_price_conservative','?')):>12} "
            f"{str(p.get('sell_price_aggressive','?')):>12} "
            f"{str(p.get('stop_loss','?')):>10} "
            f"{str(p.get('upside_conservative','?')):>10} "
            f"{str(p.get('probability_of_target','?')):>6} "
            f"{str(p.get('hold_days','?'))}"
        )

    biotech = data.get("top_biotech_watch", [])
    squeeze = data.get("short_squeeze_radar", [])
    if biotech:
        print(f"\nBiotech watch ({len(biotech)}): {', '.join(b.get('ticker','?') for b in biotech)}")
    if squeeze:
        print(f"Squeeze radar ({len(squeeze)}): {', '.join(s.get('ticker','?') for s in squeeze)}")

    return data


def save_picks(data: dict):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nSaved to {OUTPUT_FILE}")


def send_pushover(data: dict):
    if not PUSHOVER_TOKEN or not PUSHOVER_USER:
        print("Pushover not configured - skipping")
        return

    picks = data.get("picks", [])
    if not picks:
        return

    hi = [p for p in picks if p.get("conviction") == "high"]
    lines = [
        "AGGRESSIVE PICKS - HIGH RISK / HIGH RETURN",
        data.get("market_summary", ""),
        f"{len(picks)} picks | {len(hi)} high conviction\n"
    ]

    for p in picks[:6]:
        icon = {"high": "[HOT]", "medium": "[WARM]", "speculative": "[SPEC]"}.get(
            p.get("conviction", ""), "")
        lines.append(
            f"{icon} {p.get('ticker')} | "
            f"Buy {p.get('buy_price')} | "
            f"Target {p.get('sell_price_conservative')} / {p.get('sell_price_aggressive')} | "
            f"Stop {p.get('stop_loss')} | "
            f"{p.get('upside_conservative')} - {p.get('upside_aggressive')} | "
            f"{p.get('probability_of_target','?')} prob"
        )

    if len(picks) > 6:
        lines.append(f"...+{len(picks)-6} more on dashboard")

    biotech = data.get("top_biotech_watch", [])
    if biotech:
        lines.append(f"\nBiotech watch: {', '.join(b.get('ticker','?') for b in biotech)}")

    wisdom = data.get("daily_wisdom", "")
    if wisdom:
        lines.append(f'\n"{wisdom}"')

    r = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token":     PUSHOVER_TOKEN,
            "user":      PUSHOVER_USER,
            "title":     f"AlphaSignal AGGRESSIVE - {len(picks)} Picks | {today_str}",
            "message":   "\n".join(lines),
            "url":       DASHBOARD_URL,
            "url_title": "View dashboard",
            "priority":  1,
            "sound":     "cashregister",
        },
        timeout=10
    )
    print("Pushover sent" if r.status_code == 200 else f"Pushover failed: {r.status_code}")


if __name__ == "__main__":
    data = generate_picks()
    save_picks(data)
    send_pushover(data)
    print("Done.")
