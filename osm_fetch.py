"""
sanpo プロジェクト - OSM（OpenStreetMap）データ取得モジュール
フェーズ1「MAP基盤」実験: 指定緯度経度の半径500m以内の
道路(highway)・公園(leisure=park)・水辺(natural=water) を取得してコンソール表示する。
"""

import urllib.request
import urllib.parse
import json

# Overpass API エンドポイント（公開サーバー）
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter"
]

# 例: 仙台駅周辺
SENDAI_STATION_LAT = 38.2600
SENDAI_STATION_LON = 140.8824


def build_overpass_query(lat: float, lon: float, radius_m: int = 500) -> str:
    """
    指定座標周辺の OSM データ取得用クエリを組み立てる。
    取得対象: highway（道路）, leisure=park（公園）, natural=water（水辺）
    """
    return f"""
[out:json][timeout:25];
(
  way["highway"](around:{radius_m},{lat},{lon});
  way["leisure"="park"](around:{radius_m},{lat},{lon});
  way["natural"="water"](around:{radius_m},{lat},{lon});
);
out body;
>;
out skel qt;
"""


def fetch_osm_around(lat: float, lon: float, radius_m: int = 500) -> dict:
    """
    指定した緯度・経度の周辺（半径 radius_m メートル）の OSM データを取得する。
    複数のミラーサーバーを順次試行する。
    """
    query = build_overpass_query(lat, lon, radius_m)
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    
    last_error = None
    for url in OVERPASS_ENDPOINTS:
        try:
            print(f"Trying {url} ...")
            req = urllib.request.Request(
                url,
                data=data,
                method="POST",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "SanpoApp/1.0 (https://github.com/yourusername/sanpo)"
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"Failed to fetch from {url}: {e}")
            last_error = e
            continue
    
    raise last_error or Exception("All Overpass endpoints failed")


def classify_elements(response: dict) -> dict:
    """
    取得した OSM 要素を道路・公園・水辺に分類する。
    フェーズ1の判定基準: highway / leisure=park / natural=water
    """
    highways = []
    parks = []
    waters = []

    for elem in response.get("elements", []):
        if elem.get("type") != "way":
            continue
        tags = elem.get("tags") or {}

        if "highway" in tags:
            highways.append(elem)
        if tags.get("leisure") == "park":
            parks.append(elem)
        if tags.get("natural") == "water":
            waters.append(elem)

    return {
        "highway": highways,
        "park": parks,
        "water": waters,
    }


def _tag_name(elem: dict) -> str:
    """OSM要素の表示名を取得（name タグ or id）"""
    tags = elem.get("tags") or {}
    return tags.get("name") or tags.get("name:ja") or f"(id={elem.get('id')})"


def print_phase1_result(lat: float, lon: float, radius_m: int, classified: dict) -> None:
    """
    フェーズ1実験: 道路・公園・水辺の取得結果をコンソールに表示する。
    """
    print("=" * 60)
    print("フェーズ1「MAP基盤」実験 - OSM 取得結果")
    print("=" * 60)
    print(f"中心: 緯度 {lat}, 経度 {lon}  半径: {radius_m}m")
    print()

    print("【道路 (highway)】")
    print(f"  件数: {len(classified['highway'])}")
    for w in classified["highway"][:15]:
        tags = w.get("tags") or {}
        hw = tags.get("highway", "?")
        name = _tag_name(w)
        print(f"    - {name}  (highway={hw})")
    if len(classified["highway"]) > 15:
        print(f"    ... 他 {len(classified['highway']) - 15} 件")
    print()

    print("【公園 (leisure=park)】")
    print(f"  件数: {len(classified['park'])}")
    for w in classified["park"]:
        print(f"    - {_tag_name(w)}")
    print()

    print("【水辺 (natural=water)】")
    print(f"  件数: {len(classified['water'])}")
    for w in classified["water"]:
        print(f"    - {_tag_name(w)}")
    print("=" * 60)


if __name__ == "__main__":
    # 仙台駅周辺（緯度・経度は定数で変更可能）
    LAT, LON = SENDAI_STATION_LAT, SENDAI_STATION_LON
    radius = 500

    print("OpenStreetMap からデータ取得中（Overpass API）...")
    data = fetch_osm_around(LAT, LON, radius)
    classified = classify_elements(data)

    print_phase1_result(LAT, LON, radius, classified)
