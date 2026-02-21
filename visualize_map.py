import requests
import matplotlib.pyplot as plt

def visualize_area(lat, lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    # 描画のために座標データ（geom）を含めて取得します
    query = f"""
    [out:json];
    (
      way["highway"](around:500,{lat},{lon});
      way["leisure"="park"](around:500,{lat},{lon});
      way["natural"="water"](around:500,{lat},{lon});
    );
    out geom;
    """
    
    response = requests.get(overpass_url, params={'data': query})
    data = response.json()

    plt.figure(figsize=(10, 10))
    # 背景色を少し暗めにしてゲームっぽく
    plt.gca().set_facecolor('#222222')

    for el in data.get('elements', []):
        if 'geometry' not in el: continue
        
        # 緯度(lat)をY、経度(lon)をXとしてリスト化
        x = [point['lon'] for point in el['geometry']]
        y = [point['lat'] for point in el['geometry']]
        
        tags = el.get('tags', {})
        
        # 属性ごとに色分けして描画
        if 'highway' in tags:
            plt.plot(x, y, color='white', linewidth=0.5, alpha=0.7) # 道は白
        elif 'leisure' in tags and tags['leisure'] == 'park':
            plt.fill(x, y, color='#4CAF50', alpha=0.5) # 公園は緑の塗りつぶし
        elif 'natural' in tags and tags['natural'] == 'water':
            plt.fill(x, y, color='#00BCD4', alpha=0.5) # 水辺は水色

    # 現在地（中心点）にモンスターの代わりに赤い点を打つ
    plt.plot(lon, lat, 'ro', markersize=10, label="Monster")
    
    plt.title(f"Map Visualization around ({lat}, {lon})")
    plt.axis('equal') # 縦横比を維持
    plt.show()

# 仙台駅で実行
visualize_area(38.2601, 140.8822)