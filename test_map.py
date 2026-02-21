import requests
import json

def get_map_data(lat, lon):
    # 現在地から半径500m以内を検索するクエリ
    # highway(道), leisure=park(公園), natural=water(水辺)を取得
    overpass_url = "http://overpass-api.de/api/interpreter"
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
    response = requests.get(overpass_url, params={'data': overpass_query})
    
    if response.status_code == 200:
        return response.json()
    else:
        print("エラーが発生しました")
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