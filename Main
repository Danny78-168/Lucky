from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI()

# 允許前端跨網域請求 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 實測階段允許所有來源，上線後可改為你的前端網址
    allow_methods=["*"],
    allow_headers=["*"],
)

# 獎項與權重設定
prizes = [
    {"index": 0, "text": "1u", "weight": 500},
    {"index": 1, "text": "8u", "weight": 250},
    {"index": 2, "text": "18u", "weight": 120},
    {"index": 3, "text": "28u", "weight": 70},
    {"index": 4, "text": "38u", "weight": 40},
    {"index": 5, "text": "58u", "weight": 15},
    {"index": 6, "text": "88u", "weight": 5}
]

# 模擬資料庫：預先產生的有效序號 (False 代表未被使用)
# 未來可以將這裡替換成連接 Google 試算表或 SQLite 資料庫
serials_db = {
    "VIP001": False,
    "VIP002": False,
    "VIP003": False,
    "LUCKY88": False
}

class SpinRequest(BaseModel):
    serial: str

@app.post("/api/spin")
def spin_wheel(req: SpinRequest):
    serial = req.serial.strip()
    
    # 1. 驗證序號是否存在
    if serial not in serials_db:
        raise HTTPException(status_code=400, detail="無效的序號，請重新確認！")
    
    # 2. 驗證序號是否已被使用
    if serials_db[serial]:
        raise HTTPException(status_code=400, detail="此序號已經抽過獎囉！")

    # 3. 根據權重抽獎
    population = [p["index"] for p in prizes]
    weights = [p["weight"] for p in prizes]
    winning_index = random.choices(population, weights=weights, k=1)[0]

    # 4. 將該序號標記為已使用
    serials_db[serial] = True

    return {
        "success": True, 
        "prize": prizes[winning_index]["text"], 
        "index": winning_index
    }
