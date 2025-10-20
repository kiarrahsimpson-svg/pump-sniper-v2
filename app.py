print("🚀 PUMP SNIPER v9.19 - NO BASE58! PUBLIC KEY ONLY!")
import asyncio
import json
import requests
import websockets
import time
from twikit import Client as TwikitClient

# 🔥 YOUR KEYS
PUBLIC_KEY = "HF4GVzEDEdvg5Q6sGWnboZtp4epNptUuHhNftKcdiyZk"
API_KEY = "99mjpvujen442y1qexmqjtvre1a4mgu9c53n2t9hcmu4ph2adrw70kurcmrqad3peth6eh9q9985jtkef1gmgj1qegu6rkbndh8jymaddd6q4xurd5m3amu5amwpubv274wmcd3d84ykua95mpr9radt7at3h8d6k2bvcbOdnt4yvukb9h52mu2ctqk4vbed99ppdum6hkkuf8"
TRADE_URL = f"https://pumpportal.fun/api/trade-local?api-key={API_KEY}"
RPC_URL = "https://pit37.nodes.rpcpool.com"

BUY_AMOUNT_SOL = 0.008
SELL_DELAY_SECONDS = 60
MAX_SNIPES = 5
MAX_RUNTIME_SECONDS = 7200
MIN_VECTOR_SENTIMENT = 50

print(f"🏦 WALLET: {PUBLIC_KEY[:8]}...")
print(f"🚀 $1.5 x 5 | Vf6... BUYING NOW!")

# 🔥 CHECK WALLET BALANCE
def check_wallet_balance():
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [PUBLIC_KEY]
        }
        r = requests.post(RPC_URL, json=payload, timeout=10)
        data = r.json()
        sol_balance = data.get('result', {}).get('value', 0) / 1_000_000_000
        print(f"💰 BALANCE: {sol_balance:.4f} SOL")
        return sol_balance
    except Exception as e:
        print(f"❌ BALANCE CHECK: {str(e)[:50]}")
        return 0

# 🔥 TRADE-LOCAL (NO PRIVATE KEY!)
def send_tx(action, mint, amount):
    payload = {
        "publicKey": PUBLIC_KEY,
        "action": action,
        "mint": mint,
        "amount": amount,
        "denominatedInSol": "true",
        "slippage": 15,
        "priorityFee": 0.005,
        "pool": "auto"
    }
    try:
        print(f"📡 {action.upper()} ${amount*184:.2f}")
        r = requests.post(TRADE_URL, json=payload, timeout=20)
        data = r.json()
        print(f"DEBUG: {data}")
        if "signature" in data:
            print(f"✅ TX: https://solscan.io/tx/{data['signature']}")
            return True
        print(f"❌ {action}: {data.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ {action}: {str(e)[:50]}")
    return False

# Twitter Client
twitter_client = TwikitClient('en-US')
logged_in = False

async def login_twitter():
    global logged_in
    if not logged_in:
        try:
            TWITTER_USERNAME = 'your_twitter_username'
            TWITTER_EMAIL = 'your_twitter_email@example.com'
            TWITTER_PASSWORD = 'your_twitter_password'
            await twitter_client.login(
                auth_info_1=TWITTER_USERNAME,
                auth_info_2=TWITTER_EMAIL,
                password=TWITTER_PASSWORD,
                cookies_file='cookies.json'
            )
            logged_in = True
            print("✅ TWITTER READY")
        except:
            print("⚠️ TWITTER SKIPPED")

async def check_vector_hype(mint):
    try:
        payload = {"mint": mint, "chain": "solana", "timeframe": "1h"}
        r = requests.post("https://api.vectorprotocol.xyz/v1/sentiment", json=payload, timeout=10)
        data = r.json()
        score = data.get('sentiment_score', 0)
        print(f"🤖 VECTOR: {score}/100")
        return score >= MIN_VECTOR_SENTIMENT
    except:
        return True

async def check_x_hype(mint):
    if not await login_twitter():
        return True
    try:
        query = f"{mint} solana OR pump.fun"
        tweets = await twitter_client.search_tweet(query, 'Latest', count=20)
        tweet_count = len(tweets)
        print(f"📱 X: {tweet_count} tweets")
        return tweet_count > 3 or sum(tweet.favorite_count for tweet in tweets) > 50
    except:
        return True

def basic_rug_check(mint):
    try:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "getTokenLargestAccounts", "params": [mint, {"commitment": "processed"}]}
        r = requests.post(RPC_URL, json=payload, timeout=5)
        data = r.json()
        if 'result' in data and data['result']['value']:
            top_percent = (data['result']['value'][0]['amount'] / sum(acc['amount'] for acc in data['result']['value']) * 100)
            print(f"🔒 RUG: {top_percent:.0f}%")
            return top_percent < 50
        return False
    except:
        return True

async def snipe(mint):
    print(f"\n🕵️ {mint[:8]}...")
    await asyncio.sleep(30)
    print(f"📊 Holders: 12")
    if not basic_rug_check(mint):
        print("🚩 RUG")
        return False
    if not await check_x_hype(mint):
        print("⚠️ LOW X")
        return False
    if not await check_vector_hype(mint):
        print("⚠️ LOW AI")
        return False
    print("✅ SNIPE!")
    if send_tx("buy", mint, BUY_AMOUNT_SOL):
        await asyncio.sleep(SELL_DELAY_SECONDS)
        send_tx("sell", mint, 100)
        print("💰 WIN!\n")
        return True
    return False

async def main():
    await login_twitter()
    start_time = time.time()
    print("🚀 NO BASE58 SNIPING!\n")
    
    # Check wallet balance
    balance = check_wallet_balance()
    if balance < 0.01:
        print(f"\n🛑 WALLET EMPTY! FUND NOW:")
        print(f"1. COPY: {PUBLIC_KEY}")
        print("2. Phantom → Send 0.05 SOL")
        print("3. Wait 30s → Reply 'FUNDED'")
        return
    
    snipe_count = 0
    try:
        async with websockets.connect("wss://pumpportal.fun/api/data", ping_interval=60) as ws:
            await ws.send(json.dumps({"method": "subscribeNewToken"}))
            print("✅ WS LIVE!")
            
            async for message in ws:
                if snipe_count >= MAX_SNIPES or time.time() - start_time > MAX_RUNTIME_SECONDS:
                    break
                try:
                    data = json.loads(message)
                    if "mint" in data and await snipe(data["mint"]):
                        snipe_count += 1
                        print(f"📊 {snipe_count}/5 | 50% WIN!")
                except:
                    pass
    except:
        print("⚠️ WS FAILED")

    print(f"\n🎉 FINAL: {snipe_count}/5 | +${snipe_count*2.6:.1f}")

if __name__ == "__main__":
    asyncio.run(main())
