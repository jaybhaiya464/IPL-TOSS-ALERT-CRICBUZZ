import requests
import time
from datetime import datetime

# ─── CONFIG — Har match ke liye sirf MATCH_ID badlo ──────────
MATCH_ID  = 153341   # TEST: PAK W vs ZIM W 4 PM
# MATCH_ID  = 152075   # MAIN: RR vs GT 7 PM

API_KEY   = "a9ef6d69f3msh80ef0aa362b7573p1277e1jsnca6bd33977b6"
BOT_TOKEN = "8627084246:AAHPjhW7W7KfBBZ2QYN_teyE-VweAys9Auk"
CHAT_ID   = "8011028077"

POLL_INTERVAL = 0.5  # 500ms

TG_URL  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

toss_alerted = False

def now():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def tg(text):
    try:
        requests.post(TG_URL, json={
            "chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"
        }, timeout=5)
    except Exception as e:
        print(f"[TG ERROR] {e}")

def fetch():
    try:
        r = requests.get(
            f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{MATCH_ID}/hscard",
            headers=HEADERS, timeout=5
        )
        if r.ok:
            return r.json()
    except Exception as e:
        print(f"[FETCH ERROR] {e}")
    return None

def extract_toss(data):
    winner = ""
    decision = ""

    # Path 1: matchHeader.toss
    header = data.get("matchHeader", {})
    toss   = header.get("toss", {})
    winner   = toss.get("winner", "") or toss.get("tossWinner", "")
    decision = toss.get("decision", "") or toss.get("tossDecision", "")

    # Path 2: matchInfo
    if not winner:
        mi       = data.get("matchInfo", {})
        winner   = mi.get("tossWinner", "")
        decision = mi.get("tossDecision", "")

    # Path 3: scoreCard[0]
    if not winner:
        sc = data.get("scoreCard", [])
        if sc:
            t        = sc[0].get("toss", {})
            winner   = t.get("winner", "")
            decision = t.get("decision", "")

    return winner, decision

def check_toss(data):
    global toss_alerted
    if not data or toss_alerted:
        return

    winner, decision = extract_toss(data)

    if winner:
        toss_alerted = True
        t = now()
        msg = (
            f"🚨 <b>TOSS! {t}</b>\n\n"
            f"🏏 <b>{winner}</b> won the toss!\n"
            f"📋 Decision: <b>{decision}</b>\n\n"
            f"⚡ Cricbuzz | 500ms poll"
        )
        print(f"\n{'='*50}")
        print(f"🚨 TOSS at {t}: {winner} | {decision}")
        print(f"{'='*50}\n")
        tg(msg)

def main():
    print("="*50)
    print(f"  Cricbuzz Toss Detector")
    print(f"  Match ID: {MATCH_ID}")
    print(f"  Poll: {POLL_INTERVAL}s")
    print("="*50 + "\n")

    tg(
        f"✅ <b>Cricbuzz Bot Started</b>\n"
        f"🏏 Match: <code>{MATCH_ID}</code>\n"
        f"⚡ Poll every 500ms"
    )

    loop = 0
    while True:
        time.sleep(POLL_INTERVAL)
        loop += 1

        if toss_alerted:
            if loop % 120 == 0:
                print(f"[{now()}] Toss done. Idle.")
            continue

        data = fetch()
        if data:
            check_toss(data)

        if loop % 60 == 0:
            print(f"[{now()}] Monitoring... {loop} checks")

if __name__ == "__main__":
    main()
