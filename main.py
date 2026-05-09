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
    """
    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://z.overpass-api.de/api/interpreter",
        "https://overpass.nchc.org.tw/api/interpreter"
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for url in endpoints:
            try:
                # GET または POST でデータを送信
                # 長いクエリの場合は本来 POST が望ましいが、一旦フロントエンドに合わせて GET で試行
                response = await client.get(url, params={"data": data})
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f"Proxy error for {url}: {e}")
                continue
                
    return {"error": "All Overpass endpoints failed or timed out"}
