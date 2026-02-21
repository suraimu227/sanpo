from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# データベース初期化
def init_db():
    conn = sqlite3.connect("monster.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monster_status (
            id INTEGER PRIMARY KEY,
            level INTEGER DEFAULT 1,
            exp_city INTEGER DEFAULT 0,
            exp_nature INTEGER DEFAULT 0
        )
    """)
    cursor.execute("SELECT count(*) FROM monster_status")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO monster_status (level) VALUES (1)")
    conn.commit()
    conn.close()

init_db()

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 判定と歩行処理（ここを改善しました）
@app.get("/walk")
def walk(lat: float, lon: float, steps: int = 1000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f'[out:json][timeout:10];(way["highway"](around:200,{lat},{lon});way["leisure"="park"](around:200,{lat},{lon}););out tags;'
    
    try:
        # タイムアウトを短め(10秒)にして、ダメならすぐに諦めて次に進むようにします
        response = requests.get(overpass_url, params={'data': query}, timeout=10)
        elements = response.json().get('elements', [])
    except Exception as e:
        print(f"地図サーバーが重いため、デフォルト判定(都会)を行います: {e}")
        elements = [{"tags": {"highway": "residential"}}] # 失敗時のダミーデータ

    city_count = sum(1 for e in elements if 'highway' in e.get('tags', {}))
    park_count = sum(1 for e in elements if e.get('tags', {}).get('leisure') == 'park')
    
    attr = "city" if city_count > (park_count * 10) else "nature"
    
    conn = sqlite3.connect("monster.db")
    cursor = conn.cursor()
    if attr == "city":
        cursor.execute("UPDATE monster_status SET exp_city = exp_city + ?", (steps,))
    else:
        cursor.execute("UPDATE monster_status SET exp_nature = exp_nature + ?", (steps,))
    conn.commit()
    cursor.execute("SELECT level, exp_city, exp_nature FROM monster_status WHERE id = 1")
    status = cursor.fetchone()
    conn.close()
    
    return {"attr": attr, "status": {"level": status[0], "city": status[1], "nature": status[2]}}