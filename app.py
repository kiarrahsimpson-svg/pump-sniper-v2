print("🚀 PUMP SNIPER STARTING...")
import asyncio
import json
import os
import requests
import websockets
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig
from solders.commitment_config import CommitmentLevel

PRIVATE_KEY_B58 = os.environ.get('59nxrch4UGnonWR7NZ75WSUnSgHx4QbozMd88j5iZtqqnNod5EPabejJHGQ4GZnZ7TQmyhFusELcw7JEVpAgJmhU', 'SETUP_NEEDED')
keypair = Keypair.from_base58_string(PRIVATE_KEY_B58)
public_key = keypair.pubkey()
sol_client = AsyncClient("https://api.mainnet-beta.solana.com")

BUY_AMOUNT_SOL = 0.02
SELL_DELAY_SECONDS = 60
MAX_SNIPES = 12

async def send_tx(action, mint, amount):
    body = {"publicKey": str(public_key), "action": action, "mint": mint, 
            "denominatedInSol": "true" if action == "buy" else "false", 
            "amount": amount, "slippage": 15, "priorityFee": 0.0001, "pool": "pump"}
    r = requests.post("https://pumpportal.fun/api/trade-local", json=body)
    if r.status_code == 200:
        tx = VersionedTransaction.from_bytes(r.content)
        tx.sign([keypair])
        sig = await sol_client.send_transaction(tx).value
        print(f"✅ {action.upper()}: https://solscan.io/tx/{sig}")
        return True
    return False

async def snipe(mint):
    print(f"🎯 SNIPING {mint[:8]}")
    await send_tx("buy", mint, BUY_AMOUNT_SOL)
    await asyncio.sleep(SELL_DELAY_SECONDS)
    await send_tx("sell", mint, 100)
    print("💰 DONE!\n")

async def main():
    print("🚀 LIVE ON RAILWAY!")
    snipe_count = 0
    async with websockets.connect("wss://pumpportal.fun/api/data") as ws:
        await ws.send(json.dumps({"method": "subscribeNewToken"}))
        print("🔴 WAITING...\n")
        async for msg in ws:
            data = json.loads(msg)
            if "mint" in data and snipe_count < MAX_SNIPES:
                await snipe(data["mint"])
                snipe_count += 1
                print(f"📊 {snipe_count}/12")

if __name__ == "__main__":
    asyncio.run(main())
