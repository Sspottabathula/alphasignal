# 📈 AlphaSignal — Daily AI Stock Picks

> High-risk / high-return US stock picks generated every weekday at 9:15 AM ET using Claude AI.
> Accessible from any device at: **https://sspottabathula.github.io/alphasignal**

---

## 🚀 Quick Setup (5 minutes)

### 1. Create the repo on GitHub
- Go to [github.com/new](https://github.com/new)
- Name it `alphasignal`
- Set to **Public**
- Click **Create repository**
- Push these files to it

```bash
git init
git add .
git commit -m "Initial AlphaSignal setup"
git branch -M main
git remote add origin https://github.com/Sspottabathula/alphasignal.git
git push -u origin main
```

### 2. Add your Anthropic API key
- Go to your repo → **Settings** → **Secrets and variables** → **Actions**
- Click **New repository secret**
- Name: `ANTHROPIC_API_KEY`
- Value: your key from [console.anthropic.com](https://console.anthropic.com)

### 3. (Optional) Add Pushover for phone notifications
- Sign up at [pushover.net](https://pushover.net) — one-time $5 app fee
- Create an application → copy the **App Token**
- Copy your **User Key** from the dashboard
- Add two more GitHub secrets:
  - `PUSHOVER_TOKEN` → your app token
  - `PUSHOVER_USER` → your user key

### 4. Enable GitHub Pages
- Go to your repo → **Settings** → **Pages**
- Source: **Deploy from a branch**
- Branch: `main` / `/ (root)`
- Click **Save**
- Your URL: `https://sspottabathula.github.io/alphasignal`

### 5. Run it manually the first time
- Go to your repo → **Actions** tab
- Click **Daily Stock Picks** → **Run workflow** → **Run workflow**
- Wait ~30 seconds — picks.json will be committed and the site will update

---

## 📁 File Structure

```
alphasignal/
├── index.html                    # Dashboard (loads picks.json)
├── picks.json                    # Auto-updated daily by GitHub Actions
├── generate_picks.py             # Python script that calls Claude API
├── README.md                     # This file
└── .github/
    └── workflows/
        └── daily-picks.yml       # GitHub Actions cron job
```

---

## ⏰ Schedule

The GitHub Actions workflow runs automatically:
- **Every weekday (Mon–Fri) at 9:15 AM ET** (14:15 UTC)
- Generates 3 picks, saves to `picks.json`, deploys via GitHub Pages
- Optionally sends a Pushover push notification to your phone

---

## 📱 Phone Alerts via Robinhood

1. Open Robinhood → search the ticker
2. Tap the 🔔 bell icon
3. Set price alert at the **entry price** (buy signal)
4. Set a second alert at the **exit target** (sell signal)
5. Repeat for all 3 picks

---

## ⚠️ Disclaimer

This tool is for **informational purposes only** and does NOT constitute financial advice.
These are high-risk, speculative picks — you may lose your entire investment.
Always do your own research before investing.
