import os
import re

def find_index_html():
    for root, dirs, files in os.walk("."):
        if "node_modules" in root or ".git" in root or ".next" in root:
            continue
        if "index.html" in files:
            return os.path.join(root, "index.html")
    return None

INDEX_FILE = find_index_html()

GACHA_UI_HTML = """<!-- GACHA_SYSTEM_START -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<style>
    #gacha-floating-panel {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 300px;
        background: rgba(6, 10, 20, 0.95);
        border: 1px solid #00f3ff;
        border-radius: 14px;
        padding: 14px;
        color: #e0f7fa;
        font-family: monospace, sans-serif;
        z-index: 999999;
        box-shadow: 0 0 25px rgba(0, 243, 255, 0.3), inset 0 0 10px rgba(0, 243, 255, 0.1);
        backdrop-filter: blur(8px);
        text-align: center;
    }
    .gacha-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(0, 243, 255, 0.3);
        padding-bottom: 6px;
        margin-bottom: 8px;
    }
    .gacha-title-bar {
        font-size: 0.9rem;
        color: #00f3ff;
        font-weight: bold;
        letter-spacing: 1px;
        text-shadow: 0 0 8px rgba(0, 243, 255, 0.8);
    }
    #gacha-3d-canvas {
        width: 100%;
        height: 150px;
        background: radial-gradient(circle at center, #0a1128 0%, #02040a 100%);
        border-radius: 8px;
        margin: 6px 0;
        border: 1px solid rgba(0, 243, 255, 0.2);
    }
    .gacha-btn-group {
        display: flex;
        gap: 8px;
        justify-content: center;
        margin-top: 6px;
    }
    .gacha-btn {
        background: linear-gradient(135deg, rgba(0,243,255,0.2) 0%, rgba(0,119,255,0.4) 100%);
        color: #00f3ff;
        border: 1px solid #00f3ff;
        padding: 8px 12px;
        font-size: 0.8rem;
        border-radius: 6px;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.2s;
    }
    .gacha-btn.ten {
        background: linear-gradient(135deg, rgba(255,0,128,0.2) 0%, rgba(255,0,85,0.5) 100%);
        color: #ff007f;
        border-color: #ff007f;
    }
    .gacha-btn:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 0 12px currentColor;
    }
    .gacha-btn:disabled {
        opacity: 0.4;
        cursor: not-allowed;
        border-color: #555 !important;
        color: #888 !important;
        background: rgba(50, 50, 50, 0.3) !important;
        box-shadow: none !important;
    }
    #gacha-result-log {
        margin-top: 8px;
        background: rgba(0, 0, 0, 0.7);
        padding: 8px;
        border-radius: 6px;
        font-size: 0.78rem;
        max-height: 90px;
        overflow-y: auto;
        border: 1px solid rgba(255, 255, 255, 0.08);
        text-align: left;
        line-height: 1.4;
    }
    .rarity-ssr { color: #ffe600; font-weight: bold; text-shadow: 0 0 8px #ffaa00; }
    .rarity-sr { color: #e0e0e0; font-weight: bold; text-shadow: 0 0 5px #aaa; }
    .rarity-r { color: #64b5f6; }
</style>

<div id="gacha-floating-panel">
    <div class="gacha-header">
        <div class="gacha-title-bar">✦ CYBER GACHA</div>
        <div style="font-size: 0.8rem; color: #00f3ff;">💎 ∞</div>
    </div>
    
    <div id="gacha-3d-canvas"></div>

    <div class="gacha-btn-group">
        <button id="gacha-btn-1" class="gacha-btn" onclick="runGachaProcess(1)">EXECUTE x1</button>
        <button id="gacha-btn-10" class="gacha-btn ten" onclick="runGachaProcess(10)">EXECUTE x10</button>
    </div>

    <div id="gacha-result-log">マップ初期化チェック中...</div>
</div>

<script>
(function() {
    const ITEMS_DB = {
        SSR: [
            { id: "ssr_1", name: "★SSR★ ロトのつるぎ", type: "weapon", atk: 120 },
            { id: "ssr_2", name: "★SSR★ 勇者の盾", type: "armor", def: 100 },
            { id: "ssr_3", name: "★SSR★ りゅうおうのこころ", type: "accessory", atk: 80, def: 80 }
        ],
        SR: [
            { id: "sr_1", name: "☆SR☆ 鋼のつるぎ", type: "weapon", atk: 50 },
            { id: "sr_2", name: "☆SR☆ 魔法の盾", type: "armor", def: 45 },
            { id: "sr_3", name: "☆SR☆ キラーマシンのこころ", type: "accessory", atk: 40, def: 30 }
        ],
        R: [
            { id: "r_1", name: "[R] 銅の剣", type: "weapon", atk: 15 },
            { id: "r_2", name: "[R] 皮のたて", type: "armor", def: 12 },
            { id: "r_3", name: "[R] スライムのこころ", type: "accessory", atk: 10, def: 10 }
        ]
    };

    let isMapLoaded = false;
    let isExecuting = false;

    function setGachaButtonsState(enabled, message) {
        const btn1 = document.getElementById('gacha-btn-1');
        const btn10 = document.getElementById('gacha-btn-10');
        const logBox = document.getElementById('gacha-result-log');

        if (btn1) btn1.disabled = !enabled;
        if (btn10) btn10.disabled = !enabled;
        if (message && logBox) logBox.innerHTML = message;
    }

    function initMapObserver() {
        let attempts = 0;
        function check() {
            attempts++;
            const hasMapElem = document.querySelector('.leaflet-container, .mapboxgl-map, #map, canvas');
            const hasMapObj = window.map || window.leafletMap || window.mapboxMap || window.isMapReady;

            if (hasMapElem || hasMapObj || attempts >= 10) { 
                isMapLoaded = true;
                if (!isExecuting) {
                    setGachaButtonsState(true, "システム起動完了。実行可能です。");
                }
            } else {
                setGachaButtonsState(false, "🌐 マップ読み込み待機中...");
                setTimeout(check, 500);
            }
        }
        check();
    }

    function forcePushToOriginalBag(item) {
        const possibleBagKeys = [
            'playerInventory', 'inventory', 'bag', 'items', 'itemList', 'playerBag',
            'playerState', 'player', 'gameState', 'userItems', 'myItems'
        ];

        possibleBagKeys.forEach(key => {
            if (window[key]) {
                if (Array.isArray(window[key])) {
                    window[key].push(item);
                } else if (typeof window[key] === 'object') {
                    ['inventory', 'bag', 'items', 'itemList'].forEach(subKey => {
                        if (Array.isArray(window[key][subKey])) {
                            window[key][subKey].push(item);
                        }
                    });
                }
            }
        });

        const possibleUpdateFuncs = [
            'updateInventoryUI', 'renderBag', 'updateBag', 'renderInventory',
            'updatePlayerStats', 'drawBag', 'refreshBag', 'renderItems', 'updateUI', 'render'
        ];

        possibleUpdateFuncs.forEach(funcName => {
            if (typeof window[funcName] === 'function') {
                try { window[funcName](); } catch(e) {}
            }
        });

        window.dispatchEvent(new CustomEvent('gachaItemObtained', { detail: item }));
    }

    function init3D() {
        const canvasBox = document.getElementById('gacha-3d-canvas');
        if (!canvasBox) return;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(50, canvasBox.clientWidth / canvasBox.clientHeight, 0.1, 1000);
        camera.position.z = 4.2;

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(canvasBox.clientWidth, canvasBox.clientHeight);
        canvasBox.appendChild(renderer.domElement);

        const group = new THREE.Group();
        scene.add(group);

        const ringGeo = new THREE.TorusGeometry(1.3, 0.02, 16, 100);
        const ringMat = new THREE.MeshBasicMaterial({ color: 0x00f3ff, wireframe: true });
        const ring1 = new THREE.Mesh(ringGeo, ringMat);
        group.add(ring1);

        const ring2 = new THREE.Mesh(ringGeo, ringMat);
        ring2.rotation.x = Math.PI;
        ring2.rotation.y = Math.PI / 4;
        group.add(ring2);

        const coreGeo = new THREE.OctahedronGeometry(0.75, 0);
        const coreMat = new THREE.MeshStandardMaterial({ 
            color: 0x00f3ff, 
            wireframe: true,
            emissive: 0x00aaff,
            emissiveIntensity: 0.6
        });
        const core = new THREE.Mesh(coreGeo, coreMat);
        group.add(core);

        const pLight = new THREE.PointLight(0x00f3ff, 2.5, 10);
        pLight.position.set(0, 0, 2);
        scene.add(pLight);
        scene.add(new THREE.AmbientLight(0x222244));

        function renderLoop() {
            requestAnimationFrame(renderLoop);
            if (!isExecuting) {
                group.rotation.y += 0.01;
                group.rotation.x += 0.005;
                ring1.rotation.z -= 0.015;
                ring2.rotation.z += 0.015;
            }
            renderer.render(scene, camera);
        }
        renderLoop();

        window.runGachaProcess = function(count) {
            if (!isMapLoaded || isExecuting) return;

            isExecuting = true;
            setGachaButtonsState(false, "⚡ <span style='color:#00f3ff;'>高次元エネルギー充填中...</span>");

            let results = [];
            let hasSSR = false;
            let hasSR = false;

            for (let i = 0; i < count; i++) {
                const rand = Math.random();
                let rarity = rand < 0.08 ? "SSR" : rand < 0.30 ? "SR" : "R";
                if (rarity === "SSR") hasSSR = true;
                if (rarity === "SR") hasSR = true;

                const pool = ITEMS_DB[rarity];
                const picked = pool[Math.floor(Math.random() * pool.length)];
                
                const itemData = { ...picked, rarity, obtainedAt: Date.now() };
                results.push(itemData);

                forcePushToOriginalBag(itemData);
            }

            let startTime = Date.now();
            let duration = 3800;

            const targetColor = hasSSR ? 0xff007f : hasSR ? 0xffaa00 : 0x00f3ff;
            ringMat.color.setHex(targetColor);
            coreMat.color.setHex(targetColor);
            coreMat.emissive.setHex(targetColor);
            pLight.color.setHex(targetColor);

            function animate() {
                let elapsed = Date.now() - startTime;
                let progress = Math.min(elapsed / duration, 1.0);

                if (progress < 1.0) {
                    let speedFactor = 0.01 + Math.pow(progress, 3) * 1.4;

                    group.rotation.y += speedFactor;
                    group.rotation.x += speedFactor * 0.7;
                    ring1.rotation.z -= speedFactor * 1.6;
                    ring2.rotation.z += speedFactor * 1.8;

                    coreMat.emissiveIntensity = 0.6 + Math.pow(progress, 2) * 8.0;
                    pLight.intensity = 2.5 + Math.pow(progress, 2) * 15.0;

                    let scalePulse = 1 + Math.sin(progress * Math.PI * 12) * (0.05 + progress * 0.4);
                    core.scale.setScalar(scalePulse);

                    requestAnimationFrame(animate);
                } else {
                    isExecuting = false;
                    core.scale.setScalar(1);
                    coreMat.emissiveIntensity = 0.6;
                    pLight.intensity = 2.5;

                    let html = `<b>✦ 獲得アイテム (${count}件)</b><br>`;
                    results.forEach((res, idx) => {
                        let rClass = res.rarity === "SSR" ? "rarity-ssr" : res.rarity === "SR" ? "rarity-sr" : "rarity-r";
                        html += `${idx + 1}. <span class="${rClass}">${res.name}</span><br>`;
                    });
                    html += `<small style="color:#00f3ff;">✔ ふくろに格納されました</small>`;

                    setGachaButtonsState(isMapLoaded, html);
                }
            }
            animate();
        };

        initMapObserver();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init3D);
    } else {
        init3D();
    }
})();
</script>
<!-- GACHA_SYSTEM_END -->"""

def inject_gacha():
    if not INDEX_FILE or not os.path.exists(INDEX_FILE):
        print("❌ 'index.html' が見つかりませんでした。")
        return

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 既存のガチャコード領域があれば綺麗にクリア
    content = re.sub(r'<!-- GACHA_SYSTEM_START -->.*?<!-- GACHA_SYSTEM_END -->', '', content, flags=re.DOTALL)

    # </body> 直前か末尾に確実に挿入
    if "</body>" in content:
        new_content = content.replace("</body>", f"{GACHA_UI_HTML}\n</body>")
    else:
        new_content = content + "\n" + GACHA_UI_HTML

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("✅ 安全に index.html への組み込みが完了しました！")

if __name__ == "__main__":
    inject_gacha()