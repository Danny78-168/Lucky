from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import random
import urllib.parse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 你的 Google Apps Script 網頁應用程式網址
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwT2qt9tgnOqysXKMHgp5ufieLyQ8WV2UvR6oo4VfPn65B6RZmLusmrAd709vRD_fKa/exec"

# 新的獎項與權重設定 (總權重 1000)
prizes = [
    {"index": 0, "text": "8u", "weight": 450},   # 機率 45.0%
    {"index": 1, "text": "18u", "weight": 250},  # 機率 25.0%
    {"index": 2, "text": "38u", "weight": 180},  # 機率 18.0%
    {"index": 3, "text": "58u", "weight": 80},   # 機率 8.0%
    {"index": 4, "text": "128u", "weight": 20},  # 機率 2.0%
    {"index": 5, "text": "188u", "weight": 15},  # 機率 1.5%
    {"index": 6, "text": "288u", "weight": 5}    # 機率 0.5%
]

class SpinRequest(BaseModel):
    account: str
    serial: str

@app.post("/api/spin")
def spin_wheel(req: SpinRequest, request: Request):
    account = req.account.strip()
    serial = req.serial.strip()
    
    if not account:
        raise HTTPException(status_code=400, detail="請輸入會員帳號！")

    # 準確取得使用者真實 IP (支援 Render 代理轉發)
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "Unknown"
    
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
    prize_won = prizes[winning_index]["text"]

    # 5. 通知 Google 試算表將序號更新為已使用，並完整帶入：IP、會員帳號、中獎金額
    try:
        encoded_account = urllib.parse.quote(account)
        encoded_prize = urllib.parse.quote(prize_won)
        requests.get(f"{GOOGLE_SCRIPT_URL}?action=use_serial&serial={serial}&account={encoded_account}&ip={client_ip}&prize={encoded_prize}")
    except:
        pass

    return {
        "success": True, 
        "prize": prize_won, 
        "index": winning_index
    }
    
