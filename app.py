print("🚀 PUMP SNIPER STARTING WITH YOUR KEY...")
import asyncio
import json
import time
import requests
import websockets
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig
from solders.commitment_config import CommitmentLevel

# 🔥 YOUR PRIVATE KEY - HARDCODED & READY!
PRIVATE_KEY_B58 = "59nxrch4UGnonWR7NZ75WSUnSgHx4QbozMd88j5iZtqqnNod5EPabejJHGQ4GZnZ7TQmyhFusELcw7JEVpAgJmhU"
keypair = Keypair.from_base58_string(PRIVATE_KEY_B58)
public_key = keypair.pubkey()
print(f"✅ WALLET LOADED: {str(public_key)[:8]}...")

sol_client = AsyncClient("https://api.mainnet-beta.solina.com")

# YOUR $50 SETTINGS
BUY_AMOUNT_SOL = 0.02  # $3.67 per snipe
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
        r = requests.post("https://pumpportal.fun/api/trade-local", json=body, timeout=30)
        if r.status_code == 200:
            tx = VersionedTransaction.from_bytes(r.content)
            tx.sign([keypair])
            config = RpcSendTransactionConfig(preflight_commitment=CommitmentLevel.PROCESSED)
            sig = await sol_client.send_transaction(tx, opts=config)
            print(f"✅ {action.upper()}: https://solscan.io/tx/{sig.value}")
            return True
        print(f"❌ {action} API: {r.status_code}")
    except Exception as e:
        print(f"❌ {action} ERROR: {e}")
    return False

async def snipe(mint):
    print(f"🎯 SNIPING {mint[:8]}...")
    if await send_tx("buy", mint, BUY_AMOUNT_SOL):
        print(f"⏳ Holding {SELL_DELAY_SECONDS}s...")
        await asyncio.sleep(SELL_DELAY_SECONDS)
        await send_tx("sell", mint, 100)
        print("💰 SNIPE COMPLETE!\n")
        return True
    return False

async def main():
    print("🚀 YOUR $50 PUMP SNIPER LIVE!")
    print(f"💵 Budget: {BUY_AMOUNT_SOL * MAX_SNIPES * 184:.0f} = 12 snipes\n")
    
    snipe_count = 0
    try:
        async with websockets.connect("wss://pumpportal.fun/api/data") as ws:
            await ws.send(json.dumps({"method": "subscribeNewToken"}))
            print("🔴 LIVE: SNIPING NEW TOKENS...\n")
            
            async for message in ws:
                if snipe_count >= MAX_SNIPES:
                    print("🎉 MAX SNIPES REACHED!")
                    break
                data = json.loads(message)
                if "mint" in data:
                    if await snipe(data["mint"]):
                        snipe_count += 1
                        print(f"📊 {snipe_count}/{MAX_SNIPES} SNIPES DONE")
    except Exception as e:
        print(f"🔄 RETRYING: {e}")
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
