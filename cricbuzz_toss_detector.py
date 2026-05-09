import requests
import time
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────
MATCH_ID  = 152075   # RR vs GT — har match ke liye badlo
API_KEY   = "a9ef6d69f3msh80ef0aa362b7573p1277e1jsnca6bd33977b6"

BOT_TOKEN = "8627084246:AAHPjhW7W7KfBBZ2QYN_teyE-VweAys9Auk"
CHAT_ID   = "8011028077"

POLL_INTERVAL = 2  # seconds

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

toss_alerted = False
prev_state   = None

def now():
    return datetime.now().strftime("%H:%M:%S")

def tg(text):
    try:
        requests.post(TG_URL, json={
            "chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"
        }, timeout=5)
    except Exception as e:
        print(f"[TG ERROR] {e}")

def fetch_match():
    try:
        url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{MATCH_ID}/hscard"
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.ok:
            return r.json()
    except Exception as e:
        print(f"[FETCH ERROR] {e}")
    return None

def check_toss(data):
    global toss_alerted, prev_state

    if not data:
        return

    # Toss info Cricbuzz mein matchHeader ke andar hoti hai
    header = data.get("matchHeader", {})
    toss   = header.get("toss", {})
    state  = header.get("state", "")

    toss_winner  = toss.get("winner", "")
    toss_decision = toss.get("decision", "")

    print(f"[{now()}] state={state} | toss_winner={toss_winner} | decision={toss_decision}")

    # Toss ho gaya detect
    if toss_winner and not toss_alerted:
        toss_alerted = True
        msg = (
            f"🚨 <b>TOSS RESULT! {now()}</b>\n\n"
            f"🏏 <b>{toss_winner}</b> won the toss!\n"
            f"📋 Decision: <b>{toss_decision}</b>\n\n"
            f"⚡ Source: Cricbuzz API\n"
            f"🎯 Match ID: {MATCH_ID}"
        )
        print(f"\n🚨 TOSS: {toss_winner} won! Decision: {toss_decision}\n")
        tg(msg)

def main():
    print("="*50)
    print("  Cricbuzz Toss Detector")
    print(f"  Match ID: {MATCH_ID}")
    print(f"  Poll: every {POLL_INTERVAL}s")
    print("="*50 + "\n")

    tg(
        f"✅ <b>Cricbuzz Bot Started</b>\n"
        f"🏏 Match ID: <code>{MATCH_ID}</code>\n"
        f"⚡ Polling every {POLL_INTERVAL}s"
    )

    # Test fetch
    data = fetch_match()
    if data:
        header = data.get("matchHeader", {})
        t1 = header.get("team1", {}).get("shortName", "?")
        t2 = header.get("team2", {}).get("shortName", "?")
        print(f"[{now()}] ✅ Match found: {t1} vs {t2}")
        tg(f"✅ Monitoring: <b>{t1} vs {t2}</b>")
    else:
        print(f"[{now()}] ⚠️ Could not fetch match data")
        tg("⚠️ Match data fetch failed — will keep retrying")

    loop = 0
    while True:
        time.sleep(POLL_INTERVAL)
        loop += 1

        if toss_alerted:
            print(f"[{now()}] Toss already detected. Bot idle.")
            time.sleep(60)
            continue

        data = fetch_match()
        check_toss(data)

        if loop % 30 == 0:
            print(f"[{now()}] Monitoring... {loop} checks")

if __name__ == "__main__":
    main()
