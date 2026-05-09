import requests
import json
import time

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter"
]

def get_map_data(lat, lon):
    # 現在地から半径500m以内を検索するクエリ
    # highway(道), leisure=park(公園), natural=water(水辺)を取得
    overpass_query = f"""
    [out:json];
    (
      way["highway"](around:500,{lat},{lon});
      way["leisure"="park"](around:500,{lat},{lon});
      relation["leisure"="park"](around:500,{lat},{lon});
      way["natural"="water"](around:500,{lat},{lon});
    );
    out tags;
    """
    
    print(f"座標 ({lat}, {lon}) の周辺データを取得中...")
    
    headers = {
        "User-Agent": "SanpoApp/1.0 (https://github.com/yourusername/sanpo)"
    }

    for url in OVERPASS_ENDPOINTS:
        try:
            print(f"Trying {url} ...")
            response = requests.get(url, params={'data': overpass_query}, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code} from {url}")
        except Exception as e:
            print(f"Failed to fetch from {url}: {e}")
            continue
            
    print("全エンドポイントで失敗しました")
    return None
# 仙台駅の座標でテスト
data = get_map_data(38.2601, 140.8822)

if data:
    elements = data.get('elements', [])
    print(f"--- 仙台駅周辺（500m圏内）のデータ ---")
    print(f"取得した要素数: {len(elements)}")
    
    # 統計をとってみる
    categories = {"都会(道/店)": 0, "自然(公園)": 0, "水辺": 0}
    
    for el in elements:
        tags = el.get('tags', {})
        if 'highway' in tags:
            categories["都会(道/店)"] += 1
        if 'leisure' in tags and tags['leisure'] == 'park':
            categories["自然(公園)"] += 1
        if 'natural' in tags and tags['natural'] == 'water':
            categories["水辺"] += 1

    for cat, count in categories.items():
        print(f"{cat}: {count}件")