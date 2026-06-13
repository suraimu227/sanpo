import os
import httpx
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# フォルダパスの設定
current_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(current_dir, "static")

# staticフォルダの設定（存在する場合）
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(current_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "index.html not found"

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    target = os.path.join(static_path, "favicon.ico")
    if os.path.exists(target):
        return FileResponse(target)
    return HTMLResponse(status_code=404)

@app.get("/api/overpass")
async def proxy_overpass(data: str = Query(...)):
    """
    Overpass API へのプロキシ。CORS 回避用。
    エラーやタイムアウト対策を強化した安全版。
    """
    # 接続先エンドポイント（優先度の高い順）
    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://z.overpass-api.de/api/interpreter",
        "https://overpass.nchc.org.tw/api/interpreter"
    ]
    
    # 接続元（ブラウザ）を偽装してブロックを防ぐためのヘッダー
    headers = {
        "User-Agent": "SanpoRPGApp/1.0 (https://github.com/yourusername/sanpo)",
        "Accept-Encoding": "gzip, deflate, br"
    }
    
    # タイムアウトを少し長めの45秒に設定（地図データが大きい時の対策）
    async with httpx.AsyncClient(timeout=45.0, follow_redirects=True) as client:
        for url in endpoints:
            try:
                print(f"[Overpass Proxy] Trying endpoint: {url}")
                
                # 安全のため、長いクエリでも失敗しにくい POST メソッドでリクエストを送信
                response = await client.post(url, data={"data": data}, headers=headers)
                
                # ステータスコードが200（成功）ならデータをフロントに返す
                if response.status_code == 200:
                    print(f"[Overpass Proxy] Success! Data fetched from {url}")
                    return response.json()
                else:
                    print(f"[Overpass Proxy] Status {response.status_code} from {url}: {response.text[:100]}")
                    
            except httpx.TimeoutException:
                print(f"[Overpass Proxy] Timeout occurred while connecting to {url}")
                continue
            except Exception as e:
                print(f"[Overpass Proxy] Error connecting to {url}: {str(e)}")
                continue
                
    # すべてのサーバーが全滅した場合のエラーレスポンス
    from fastapi import HTTPException
    raise HTTPException(status_code=503, detail="All Overpass API endpoints failed or timed out.")
