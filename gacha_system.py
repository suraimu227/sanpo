import random
import json
import os

SAVE_FILE = "gacha_data.json"

class GachaSystem:
    def __init__(self):
        self.RATES = {"SSR": 0.05, "SR": 0.20, "R": 0.75}
        self.ITEMS = {
            "SSR": ["★SSR★ ロトのつるぎ", "★SSR★ 勇者の盾", "★SSR★ りゅうおうのこころ"],
            "SR":  ["☆SR☆ 鋼のつるぎ", "☆SR☆ 魔法の盾", "☆SR☆ キラーマシンのこころ"],
            "R":   ["[R] 銅の剣", "[R] 皮のたて", "[R] スライムのこころ", "[R] やくそう"]
        }
        self.COST = 10
        self.load()

    def load(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.gems = data.get("gems", 100)
                    self.inventory = data.get("inventory", [])
            except Exception:
                self.gems, self.inventory = 100, []
        else:
            self.gems, self.inventory = 100, []

    def save(self):
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"gems": self.gems, "inventory": self.inventory}, f, ensure_ascii=False, indent=2)

    def draw(self, count=1):
        cost = self.COST * count
        if self.gems < cost:
            return {"success": False, "message": "ガチャ石が足りません！"}

        self.gems -= cost
        results = []
        for _ in range(count):
            rand = random.random()
            rarity = "SSR" if rand < self.RATES["SSR"] else "SR" if rand < self.RATES["SSR"] + self.RATES["SR"] else "R"
            item = random.choice(self.ITEMS[rarity])
            results.append({"rarity": rarity, "name": item})
            self.inventory.append(item)

        self.save()
        return {"success": True, "results": results, "gems": self.gems}