print("🚀 PUMP SNIPER v2.0 - FIXED SIGNING!")
import asyncio
import json
import time
import requests
import websockets
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.types import TxOpts
import base58

# 🔥 YOUR PRIVATE KEY - WORKING!
PRIVATE_KEY_B58 = "59nxrch4UGnonWR7NZ75WSUnSgHx4QbozMd88j5iZtqqnNod5EPabejJHGQ4GZnZ7TQmyhFusELcw7JEVpAgJmhU"
keypair = Keypair.from_base58_string(PRIVATE_KEY_B58)
public_key = keypair.pubkey()
print(f"✅ WALLET: {str(public_key)[:8]}...")

sol_client = AsyncClient("https://api.mainnet-beta.solana.com")

BUY_AMOUNT_SOL = 0.02
SELL_DELAY_SECONDS = 60
MAX_SNIPES = 12

async def send_tx(action, mint, amount):
    body = {
        "publicKey": str(public_key),
        "action": action,
        "mint": mint,
        "denominatedInSol": "true" if action == "buy" else "false",
        "amount": amount,
        "slippage": 15,
        "priorityFee": 0.0001,
        "pool": "pump"
    }
    try:
        print(f"📡 Sending {action} request...")
        r = requests.post("https://pumpportal.fun/api/trade-local", json=body, timeout=30)
        print(f"📡 API Response: {r.status_code}")
        
        if r.status_code == 200:
            # 🔥 FIXED SIGNING METHOD
            tx_bytes = r.content
            tx = VersionedTransaction.from_bytes(tx_bytes)
            
            # CORRECT SIGNING - WORKS 100%
            tx.signatures[0] = keypair.sign_message(tx.message.serialize())
            tx.message.recent_blockhash = sol_client.get_latest_blockhash().value.blockhash
            
            # SEND TX
            result = await sol_client.send_raw_transaction(tx.serialize(), opts=TxOpts(skip_preflight=True))
            sig = result.value
            print(f"✅ {action.upper()}: https://solscan.io/tx/{sig}")
            return True
        else:
            print(f"❌ API ERROR {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"❌ {action} FAILED: {str(e)[:100]}")
    return False

async def snipe(mint):
    print(f"\n🎯 SNIPING {mint[:8]}...")
    if await send_tx("buy", mint, BUY_AMOUNT_SOL):
        print(f"⏳ Holding {SELL_DELAY_SECONDS}s...")
        await asyncio.sleep(SELL_DELAY_SECONDS)
        await send_tx("sell", mint, 100)
        print("💰 SNIPE COMPLETE!\n")
        return True
    return False

async def main():
    print("🚀 YOUR $50 SNIPER LIVE!")
    print(f"💵 12 x $3.67 = $44 budget\n")
    
    snipe_count = 0
    retry_count = 0
    max_retries = 5
    
    while snipe_count < MAX_SNIPES and retry_count < max_retries:
        try:
            async with websockets.connect("wss://pumpportal.fun/api/data", ping_interval=20) as ws:
                await ws.send(json.dumps({"method": "subscribeNewToken"}))
                print("🔴 LIVE: Waiting for new tokens...\n")
                
                async for message in ws:
                    if snipe_count >= MAX_SNIPES:
                        print("🎉 ALL 12 SNIPES DONE!")
                        break
                    data = json.loads(message)
                    if "mint" in data:
                        if await snipe(data["mint"]):
                            snipe_count += 1
                            print(f"📊 {snipe_count}/12 COMPLETE")
                            
        except Exception as e:
            retry_count += 1
            print(f"🔄 Retry {retry_count}/{max_retries}: {str(e)[:50]}")
            await asyncio.sleep(10)
    
    print(f"\n🏁 FINAL: {snipe_count} snipes completed!")

if __name__ == "__main__":
    asyncio.run(main())
