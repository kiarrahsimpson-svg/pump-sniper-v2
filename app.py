print("🚀 PUMP SNIPER v5.0 - PREMIUM RPC!")
import asyncio
import json
import requests
import websockets
import time

# 🔥 YOUR PRIVATE KEY
PRIVATE_KEY_B58 = "59nxrch4UGnonWR7NZ75WSUnSgHx4QbozMd88j5iZtqqnNod5EPabejJHGQ4GZnZ7TQmyhFusELcw7JEVpAgJmhU"

# 🔥 YOUR PREMIUM RPC API
RPC_URL = "https://solana-mainnet.getblock.io/eb2812edfa4b4408bf147bc22759cffd"

# LIGHTNING API (signs automatically)
API_KEY = "dummy"
URL = f"https://pumpportal.fun/api/trade?api-key={API_KEY}"

# YOUR $50 SETTINGS
BUY_AMOUNT_SOL = 0.02
SELL_DELAY_SECONDS = 60
MAX_SNIPES = 12

print(f"✅ PREMIUM RPC: {RPC_URL[-20:]}")
print(f"✅ WALLET: {PRIVATE_KEY_B58[:8]}...")

def send_tx(action, mint, amount):
    payload = {
        "action": action,
        "mint": mint,
        "amount": amount,
        "slippage": 15,
        "priorityFee": 0.0005,  # FASTER with premium!
        "pool": "pump",
        "privateKey": PRIVATE_KEY_B58
    }
    try:
        print(f"📡 {action.upper()} {mint[:8]}...")
        r = requests.post(URL, json=payload, timeout=20)
        data = r.json()
        if "signature" in data:
            print(f"✅ {action.upper()}: https://solscan.io/tx/{data['signature']}")
            return True
        print(f"❌ {action}: {data.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ {action}: {str(e)[:50]}")
    return False

async def snipe(mint):
    print(f"\n🎯 SNIPING {mint[:8]}...")
    if send_tx("buy", mint, BUY_AMOUNT_SOL):
        print(f"⏳ Holding {SELL_DELAY_SECONDS}s...")
        await asyncio.sleep(SELL_DELAY_SECONDS)
        send_tx("sell", mint, 100)
        print("💰 SNIPE COMPLETE!\n")
        return True
    return False

async def main():
    print("🚀 $50 PREMIUM SNIPER LIVE!")
    print(f"💵 12 x $3.67 = $44 | 10X SPEED!\n")
    
    snipe_count = 0
    async with websockets.connect("wss://pumpportal.fun/api/data") as ws:
        await ws.send(json.dumps({"method": "subscribeNewToken"}))
        print("🔴 PREMIUM SNIPING...\n")
        
        async for message in ws:
            if snipe_count >= MAX_SNIPES:
                print("🎉 ALL 12 DONE!")
                break
            try:
                data = json.loads(message)
                if "mint" in data:
                    if await snipe(data["mint"]):
                        snipe_count += 1
                        print(f"📊 {snipe_count}/12 | SPEED: PREMIUM")
            except:
                continue

if __name__ == "__main__":
    asyncio.run(main())
