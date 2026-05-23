import requests
import matplotlib.pyplot as plt
import sys

# デフォルト: 仙台駅
DEFAULT_LAT = 38.2601
DEFAULT_LON = 140.8822

def draw_map(lat, lon):
    print(f"位置 ({lat}, {lon}) の地図データを取得しています...")
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:30];
    (
      way["highway"](around:800,{lat},{lon});
      way["leisure"="park"](around:800,{lat},{lon});
    );
    out geom;
    """
    
    try:
        response = requests.get(overpass_url, params={'data': query}, timeout=20)
        if response.status_code != 200:
            print(f"サーバー混雑中 (Error: {response.status_code})。少し待って再試行してください。")
            return
        data = response.json()
    except Exception as e:
        print(f"接続エラーが発生しました: {e}")
        return

    # 描画の準備
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('#222222') 
    
    elements = data.get('elements', [])
    print(f"取得完了。要素数: {len(elements)}")

    for el in elements:
        if 'geometry' not in el: continue
        x = [point['lon'] for point in el['geometry']]
        y = [point['lat'] for point in el['geometry']]
        
        tags = el.get('tags', {})
        if 'highway' in tags:
            ax.plot(x, y, color='white', linewidth=0.8, alpha=0.7)
        elif 'leisure' in tags and tags['leisure'] == 'park':
            ax.fill(x, y, color='#4CAF50', alpha=0.5)

    # 現在地を大きな赤い点で表示
    ax.plot(lon, lat, 'ro', markersize=15, label="Current")
    
    delta = 0.006
    ax.set_xlim(lon - delta, lon + delta)
    ax.set_ylim(lat - delta, lat + delta)
    
    ax.set_aspect('equal')
    ax.set_title(f"MAP at {lat}, {lon}", color='white', fontsize=15)
    
    print("地図を表示します...")
    plt.show()

if __name__ == "__main__":
    lat = DEFAULT_LAT
    lon = DEFAULT_LON
    if len(sys.argv) >= 3:
        try:
            lat = float(sys.argv[1])
            lon = float(sys.argv[2])
        except ValueError:
            print("引数は 緯度 経度 の順で数値で入力してください。")
            sys.exit(1)
    
    draw_map(lat, lon)