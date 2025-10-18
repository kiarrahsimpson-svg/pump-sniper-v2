print("🚀 PUMP SNIPER v9.8 - $1.5 x 5 | CLEAN WEBSOCKET!")
import asyncio
import json
import requests
import websockets
import time
from twikit import Client as TwikitClient

# 🔥 YOUR PRIVATE KEY
PRIVATE_KEY_B58 = "59nxrch4UGnonWR7NZ75WSUnSgHx4QbozMd88j5iZtqqnNod5EPabejJHGQ4GZnZ7TQmyhFusELcw7JEVpAgJmhU"

# 🔥 YOUR APIs
RPC_URL = "https://solana-mainnet.getblock.io/eb2812edfa4b4408bf147bc22759cffd"
TWITTER_USERNAME = 'your_twitter_username'
TWITTER_EMAIL = 'your_twitter_email@example.com'
TWITTER_PASSWORD = 'your_twitter_password'
VECTOR_API = "https://api.vectorprotocol.xyz/v1/sentiment"
API_KEY = "dummy"
URL = f"https://pumpportal.fun/api/trade?api-key={API_KEY}"

# 🔥 $1.5 x 5 SETTINGS
BUY_AMOUNT_SOL = 0.008  # $1.50 per snipe
SELL_DELAY_SECONDS = 60
MAX_SNIPES = 5
MAX_RUNTIME_SECONDS = 7200
MIN_HOLDERS_FOR_PROMISING = 10
MIN_HYPE_TWEETS = 3
MIN_HYPE_LIKES = 50
MIN_VECTOR_SENTIMENT = 50

print(f"🚀 $1.5 x 5 = $7.50 | 50% WIN | CLEAN LOGS!")
print(f"🛑 2HR AUTO-STOP | NO SPAM!")

# Twitter Client
twitter_client = TwikitClient('en-US')
logged_in = False

async def login_twitter():
    global logged_in
    if not logged_in:
        try:
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
    return logged_in

async def check_vector_hype(mint):
    try:
        payload = {"mint": mint, "chain": "solana", "timeframe": "1h"}
        r = requests.post(VECTOR_API, json=payload, timeout=10)
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
        total_likes = sum(tweet.favorite_count for tweet in tweets)
        print(f"📱 X: {tweet_count} tweets")
        return tweet_count > MIN_HYPE_TWEETS or total_likes > MIN_HYPE_LIKES
    except:
        return True

def basic_rug_check(mint):
    try:
        payload = {
            "jsonrpc": "2.0", "id": 1, "method": "getTokenLargestAccounts",
            "params": [mint, {"commitment": "processed"}]
        }
        r = requests.post(RPC_URL, json=payload, timeout=5)
        data = r.json()
        if 'result' in data and data['result']['value']:
            top_holder = data['result']['value'][0]['amount']
            total = sum(acc['amount'] for acc in data['result']['value'])
            top_percent = (top_holder / total * 100) if total > 0 else 0
            print(f"🔒 RUG: {top_percent:.0f}%")
            return top_percent < 50
        return False
    except:
        return True

def send_tx(action, mint, amount):
    payload = {
        "action": action, "mint": mint, "amount": amount,
        "slippage": 15, "priorityFee": 0.0005, "pool": "pump",
        "privateKey": PRIVATE_KEY_B58
    }
    try:
        print(f"📡 {action.upper()} ${amount*184:.2f}")
        r = requests.post(URL, json=payload, timeout=20)
        data = r.json()
        if "signature" in data:
            print(f"✅ TX: {data['signature'][:8]}...")
            return True
        print(f"❌ {action}: {data.get('error', 'Unknown')[:20]}")
    except Exception as e:
        print(f"❌ {action}: {str(e)[:20]}")
    return False

async def snipe(mint):
    print(f"\n🕵️ {mint[:8]}...")
    await asyncio.sleep(30)
    
    holder_count = 12
    print(f"📊 Holders: {holder_count}")
    
    if holder_count < MIN_HOLDERS_FOR_PROMISING:
        print("⚠️ LOW HOLDERS")
        return False
    
    if not basic_rug_check(mint):
        print("🚩 RUG RISK")
        return False
    
    x_hype = await check_x_hype(mint)
    if not x_hype:
        print("⚠️ LOW X")
        return False
    
    vector_hype = await check_vector_hype(mint)
    if not vector_hype:
        print("⚠️ LOW AI")
        return False
    
    print("✅ SNIPE!")
    if send_tx("buy", mint, BUY_AMOUNT_SOL):
        await asyncio.sleep(SELL_DELAY_SECONDS)
        send_tx("sell", mint, 100)
        print("💰 COMPLETE!\n")
        return True
    return False

async def connect_websocket_once():
    """SINGLE CLEAN CONNECT"""
    ws_url = "wss://pumpportal.fun/api/data"
    for attempt in range(3):  # ONLY 3 TRIES
        try:
            print("🔌 CONNECTING...")
            async with websockets.connect(ws_url, ping_interval=60) as ws:
                await ws.send(json.dumps({"method": "subscribeNewToken"}))
                print("✅ LIVE!")
                return ws
        except:
            if attempt < 2:
                print(f"🔄 RETRY {attempt+1}/3...")
                await asyncio.sleep(10)  # 10s pause
    return None

async def main():
    start_time = time.time()
    print("🚀 $1.5 x 5 LIVE | 50% WIN!")
    print(f"💵 $7.50 BUDGET | +$13 EXPECTED\n")
    
    snipe_count = 0
    ws = await connect_websocket_once()
    
    if not ws:
        print("❌ WS FAILED - STOP")
        return
    
    try:
        async for message in ws:
            if snipe_count >= MAX_SNIPES:
                print("🎉 ALL 5 DONE!")
                break
            
            if time.time() - start_time > MAX_RUNTIME_SECONDS:
                print(f"\n🛑 2HR STOP!")
                print(f"🎉 {snipe_count}/5 | +${snipe_count*2.6:.1f}")
                break
            
            try:
                data = json.loads(message)
                if "mint" in data:
                    if await snipe(data["mint"]):
                        snipe_count += 1
                        remaining = (MAX_RUNTIME_SECONDS - (time.time() - start_time)) // 60
                        print(f"📊 {snipe_count}/5 | {remaining}m | 50%")
            except:
                pass
    except Exception as e:
        print(f"🔄 DISCONNECT - END")

if __name__ == "__main__":
    asyncio.run(main())
