# ========================================================
# help.py : 敵（モンスター）やスポットの配置データを管理する補助ファイル
# ========================================================
import random

def generate_game_elements(current_lat, current_lon):
    """
    プレイヤーの現在地（緯度・経度）を受け取って、
    その周辺に配置する「敵」と「スポット」のデータを自動で計算して返す関数
    """
    print(f"[help.py] 現在地 ({current_lat}, {current_lon}) の周辺データを生成します。")

    # 1. 敵（モンスター）のデータリスト
    # dx, dz はプレイヤーからの位置のズレ（メートル単位）です
    monsters = [
        {"name": "スライム", "type": "monster", "dx": 15.0, "dz": 15.0},
        {"name": "ドラキー", "type": "monster", "dx": -25.0, "dz": 10.0},
        {"name": "ゴーレム", "type": "monster", "dx": 5.0, "dz": -30.0}
    ]

    # 2. スポット（回復のツボなど）のデータリスト
    spots = [
        {"name": "回復のツボ", "type": "spot", "dx": -10.0, "dz": -15.0},
        {"name": "イベントスポット", "type": "spot", "dx": 20.0, "dz": -5.0}
    ]

    # メイン側にまとめて渡す
    return {
        "status": "success",
        "monsters": monsters,
        "spots": spots
    }