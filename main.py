import asyncio
import aiohttp
import aiosqlite
import json
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List,Any
from fastapi.responses import HTMLResponse
from pathlib import Path
import uvicorn

app = FastAPI()

SYMBOLS = ['BTCUSDT', 'ETHUSDT']
UPDATE_INTERVAL = 5 # this should be picked from a config eventually

# In-memory storage for active Websocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

connectionManager = ConnectionManager()

async def init_db():
    async with aiosqlite.connect("crypto_history.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            symbol TEXT,
                            price REAL,
                            timestamp DATETIME
                        )
            """)
        await db.commit()

async def fetch_price(session, symbol):
    """Fetches price from Binance Public API"""
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    async with session.get(url) as response:
        data = await response.json()
        return {"symbol": symbol, "price": float(data['price'])}

async def price_fetcher_loop():
    """Background task to fetch prices and save it to DB """
    await init_db()
    async with aiohttp.ClientSession() as session:
        while True:
            # 1. Fetch all prices concurrently
            tasks = [fetch_price(session, s) for s in SYMBOLS]
            results = await asyncio.gather(*tasks)

            # 2. Save to Database and Broadcast to UI
            async with aiosqlite.connect("crypto_history.db") as db:
                for item in results:
                    now = datetime.now().isoformat()
                    await db.execute(
                        "INSERT INTO price_history (symbol, price, timestamp) VALUES (?, ?, ?)",
                                                (item['symbol'], item['price'], now)
                    )

                    await db.commit()

                    # Send to any connected browser
                    payload = json.dumps({"symbol": item['symbol'], "price": item['price'], "time": now})
                    await connectionManager.broadcast(payload)

            print(f"Fetched and stored: {results}")
            await asyncio.sleep(UPDATE_INTERVAL)


@app.on_event('startup')
async def startup_event():
    asyncio.create_task(price_fetcher_loop())


# @app.get('/')
# async def get_root():
#     return {'message': 'Crypto Tracker is running. Connect to /ws for live data.'}


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await connectionManager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        connectionManager.disconnect(websocket)


@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return Path("templates/index.html").read_text()

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
