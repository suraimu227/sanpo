import httpx
import asyncio

async def test_overpass():
    q = '[out:json][timeout:20];(way["highway"](around:560,38.2601,140.8824);way["building"](around:560,38.2601,140.8824););out geom;'
    url = "https://overpass-api.de/api/interpreter"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params={"data": q})
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"Elements: {len(data.get('elements', []))}")
            else:
                print(f"Error: {resp.text}")
        except Exception as e:
            print(f"Exception: {e}")

asyncio.run(test_overpass())
