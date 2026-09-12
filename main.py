from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import string

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# 自動產生 7 位數安全序號的輔助函式 (混合大小寫英文與數字)
def generate_secure_serials(count=20):
    serials = {}
    chars = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    for _ in range(count):
        # 產生 7 位數亂碼
        code = ''.join(random.choices(chars, k=7))
        serials[code] = False
    return serials

# 系統啟動時自動產生 20 組 7 位數序號
serials_db = generate_secure_serials(20)

# 在 Render 後台日誌印出這批產生的序號，方便你複製發給用戶
print("=== 本次自動生成的 7 位數抽獎序號 ===")
for s in serials_db.keys():
print(s)
print("=======================================")

class SpinRequest(BaseModel):
    serial: str

@app.post("/api/spin")
def spin_wheel(req: SpinRequest):
    serial = req.serial.strip()
    
    if serial not in serials_db:
        raise HTTPException(status_code=400, detail="無效的序號，請重新確認！")
    
    if serials_db[serial]:
        raise HTTPException(status_code=400, detail="此序號已經抽過獎囉！")

    population = [p["index"] for p in prizes]
    weights = [p["weight"] for p in prizes]
    winning_index = random.choices(population, weights=weights, k=1)[0]

    serials_db[serial] = True

    return {
        "success": True, 
        "prize": prizes[winning_index]["text"], 
        "index": winning_index
    }
