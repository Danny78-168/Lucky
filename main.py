from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 你的 Google Apps Script 網頁應用程式網址
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzCz5bJJjwh56ZA0Uc2NtZbKGeh_0RqNp2JWri5kfJaZomUT1e5gD-hezSRu8o_bQ2aow/exec"

# 獎項與權重設定 (總權重 1000)
prizes = [
    {"index": 0, "text": "1u", "weight": 500},
    {"index": 1, "text": "8u", "weight": 250},
    {"index": 2, "text": "18u", "weight": 120},
    {"index": 3, "text": "28u", "weight": 70},
    {"index": 4, "text": "38u", "weight": 40},
    {"index": 5, "text": "58u", "weight": 15},
    {"index": 6, "text": "88u", "weight": 5}
]

class SpinRequest(BaseModel):
    serial: str

@app.post("/api/spin")
def spin_wheel(req: SpinRequest):
    serial = req.serial.strip()
    
    try:
        # 1. 從 Google 試算表取得最新序號資料庫
        res = requests.get(f"{GOOGLE_SCRIPT_URL}?action=get_serials")
        serials_db = res.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="無法連線至序號資料庫")

    # 2. 驗證序號是否存在
    if serial not in serials_db:
        raise HTTPException(status_code=400, detail="無效的序號，請重新確認！")
    
    # 3. 驗證是否已被使用
    if serials_db[serial]:
        raise HTTPException(status_code=400, detail="此序號已經抽過獎囉！")

    # 4. 根據權重抽獎
    population = [p["index"] for p in prizes]
    weights = [p["weight"] for p in prizes]
    winning_index = random.choices(population, weights=weights, k=1)[0]

    # 5. 通知 Google 試算表將該序號更新為已使用 (TRUE)
    try:
        requests.get(f"{GOOGLE_SCRIPT_URL}?action=use_serial&serial={serial}")
    except:
        pass

    return {
        "success": True, 
        "prize": prizes[winning_index]["text"], 
        "index": winning_index
    }
