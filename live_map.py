import requests
import matplotlib.pyplot as plt

# 仙台駅の座標（最初に成功した地点）
current_lat = 38.2601
current_lon = 140.8822

def draw_sendai_map():
    print(f"仙台駅 ({current_lat}, {current_lon}) の地図データを取得しています...")
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    # シンプルなクエリにして、エラーを防ぎます
    query = f"""
    [out:json][timeout:30];
    (
      way["highway"](around:800,{current_lat},{current_lon});
      way["leisure"="park"](around:800,{current_lat},{current_lon});
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
    ax.set_facecolor('#222222') # 暗い背景
    
    elements = data.get('elements', [])
    print(f"取得完了。要素数: {len(elements)}")

    for el in elements:
        if 'geometry' not in el: continue
        x = [point['lon'] for point in el['geometry']]
        y = [point['lat'] for point in el['geometry']]
        
        tags = el.get('tags', {})
        # 道
        if 'highway' in tags:
            ax.plot(x, y, color='white', linewidth=0.8, alpha=0.7)
        # 公園
        elif 'leisure' in tags and tags['leisure'] == 'park':
            ax.fill(x, y, color='#4CAF50', alpha=0.5)

    # 現在地（仙台駅）を大きな赤い点で表示
    ax.plot(current_lon, current_lat, 'ro', markersize=15, label="Monster")
    
    # 範囲を固定（約1.2km四方）
    delta = 0.006
    ax.set_xlim(current_lon - delta, current_lon + delta)
    ax.set_ylim(current_lat - delta, current_lat + delta)
    
    ax.set_aspect('equal')
    ax.set_title(f"SENDAI STATION MAP", color='white', fontsize=15)
    
    print("地図を表示します...")
    plt.show()

# 実行
draw_sendai_map()