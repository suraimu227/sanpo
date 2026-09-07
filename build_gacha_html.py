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
        display: none;
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 300px;
        background: #000;
        border: 4px solid #fff;
        border-radius: 8px;
        padding: 14px;
        color: #fff;
        font-family: 'DotGothic16', 'Press Start 2P', cursive;
        z-index: 999999;
        box-shadow: inset 0 0 0 2px #000, 0 0 0 2px #fff;
        text-align: center;
    }
    .gacha-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #fff;
        padding-bottom: 6px;
        margin-bottom: 8px;
    }
    .gacha-title-bar {
        font-size: 16px;
        color: #fff;
        font-weight: bold;
        letter-spacing: 2px;
    }
    #gacha-3d-canvas {
        width: 100%;
        height: 150px;
        background: #000;
        border-radius: 4px;
        margin: 6px 0;
        border: 2px solid #fff;
    }
    .gacha-btn-group {
        display: flex;
        gap: 8px;
        justify-content: center;
        margin-top: 6px;
    }
    .gacha-btn {
        background: #000;
        color: #fff;
        border: 2px solid #fff;
        padding: 10px 12px;
        font-size: 13px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
        font-family: 'DotGothic16', cursive;
        transition: all 0.2s;
    }
    .gacha-btn:hover:not(:disabled) {
        background: #fff;
        color: #000;
    }
    .gacha-btn:active:not(:disabled) {
        transform: scale(0.95);
    }
    .gacha-btn:disabled {
        opacity: 0.4;
        cursor: not-allowed;
    }
    #gacha-result-log {
        margin-top: 8px;
        background: #000;
        padding: 8px;
        border-radius: 4px;
        font-size: 12px;
        max-height: 90px;
        overflow-y: auto;
        border: 2px solid #fff;
        text-align: left;
        line-height: 1.5;
    }
    .rarity-ssr { color: #ffd700; font-weight: bold; text-shadow: 1px 1px 0 #000; }
    .rarity-sr { color: #c0c0c0; font-weight: bold; text-shadow: 1px 1px 0 #000; }
    .rarity-r { color: #cd7f32; }
</style>

<div id="gacha-floating-panel">
    <div class="gacha-header">
        <div class="gacha-title-bar">【 ふくびき 】</div>
        <div style="font-size: 12px; color: #fff; display: flex; align-items: center; gap: 8px;">
            <span>Ｇ ∞</span>
            <button onclick="document.getElementById('gacha-floating-panel').style.display='none'" style="background:transparent; border:none; color:#fff; font-weight:bold; cursor:pointer; font-size:16px; line-height:1;">×</button>
        </div>
    </div>
    
    <div id="gacha-3d-canvas"></div>

    <div class="gacha-btn-group">
        <button id="gacha-btn-1" class="gacha-btn" onclick="runGachaProcess(1)">１回 ひく</button>
        <button id="gacha-btn-10" class="gacha-btn" onclick="runGachaProcess(10)">１０回 ひく</button>
    </div>

    <div id="gacha-result-log">マップ初期化チェック中...</div>
</div>

<script>
(function() {
    const ITEMS_DB = {
        SSR: [
            { id: "ssr_1", name: "★SSR★ ロトのつるぎ", type: "weapon", atk: 120 },
            { id: "ssr_2", name: "★SSR★ 勇者の盾", type: "shield", def: 100 },
            { id: "ssr_3", name: "★SSR★ りゅうおうのこころ", type: "accessory", atk: 80, def: 80 }
        ],
        SR: [
            { id: "sr_1", name: "☆SR☆ 鋼のつるぎ", type: "weapon", atk: 50 },
            { id: "sr_2", name: "☆SR☆ 魔法の盾", type: "shield", def: 45 },
            { id: "sr_3", name: "☆SR☆ キラーマシンのこころ", type: "accessory", atk: 40, def: 30 }
        ],
        R: [
            { id: "r_1", name: "[R] 銅の剣", type: "weapon", atk: 15 },
            { id: "r_2", name: "[R] 皮のたて", type: "shield", def: 12 },
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
                const mainBtn = document.getElementById('gacha-btn-main');
                if (mainBtn) mainBtn.style.display = '';
            } else {
                setGachaButtonsState(false, "🌐 マップ読み込み待機中...");
                setTimeout(check, 500);
            }
        }
        check();
    }

    function forcePushToOriginalBag(item) {
        if (window.ITEM_DEFS) {
            window.ITEM_DEFS[item.name] = {
                type: item.type || "weapon",
                atk: item.atk || 0,
                def: item.def || 0,
                heal: item.heal || 0
            };
        }
        
        const possibleBagKeys = [
            'playerInventory', 'inventory', 'bag', 'items', 'itemList', 'playerBag',
            'playerState', 'player', 'gameState', 'userItems', 'myItems'
        ];

        possibleBagKeys.forEach(key => {
            if (window[key]) {
                if (Array.isArray(window[key])) {
                    window[key].push(item.name);
                } else if (typeof window[key] === 'object') {
                    ['inventory', 'bag', 'items', 'itemList'].forEach(subKey => {
                        if (Array.isArray(window[key][subKey])) {
                            window[key][subKey].push(item.name);
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
        const camera = new THREE.PerspectiveCamera(50, 272 / 150, 0.1, 1000);
        camera.position.z = 4.2;

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(272, 150);
        canvasBox.appendChild(renderer.domElement);

        const group = new THREE.Group();
        scene.add(group);

        const coreGroup = new THREE.Group();
        const coreMat = new THREE.MeshStandardMaterial({ 
            color: 0xcd7f32, 
            roughness: 0.8,
            metalness: 0.2
        });
        const bandMat = new THREE.MeshStandardMaterial({
            color: 0x888888,
            roughness: 0.4,
            metalness: 0.8
        });
        
        // Treasure Box Body
        const bodyGeo = new THREE.BoxGeometry(1.2, 0.8, 0.8);
        const bodyMesh = new THREE.Mesh(bodyGeo, coreMat);
        bodyMesh.position.y = -0.2;
        
        const band1 = new THREE.Mesh(new THREE.BoxGeometry(1.25, 0.1, 0.85), bandMat);
        band1.position.y = -0.2;
        
        // Treasure Box Lid
        const lidGroup = new THREE.Group();
        lidGroup.position.set(0, 0.2, -0.4); // Hinge position
        
        const lidGeo = new THREE.BoxGeometry(1.2, 0.3, 0.8);
        const lidMesh = new THREE.Mesh(lidGeo, coreMat);
        lidMesh.position.set(0, 0.15, 0.4); // Offset from hinge
        
        const band2 = new THREE.Mesh(new THREE.BoxGeometry(1.25, 0.35, 0.85), bandMat);
        band2.position.set(0, 0.15, 0.4);
        
        lidGroup.add(lidMesh);
        lidGroup.add(band2);
        
        coreGroup.add(bodyMesh);
        coreGroup.add(band1);
        coreGroup.add(lidGroup);
        
        group.add(coreGroup);
        const core = coreGroup;

        const pLight = new THREE.PointLight(0xffffff, 1.0, 10);
        pLight.position.set(0, 1, 2);
        scene.add(pLight);
        scene.add(new THREE.AmbientLight(0xffffff, 0.5));

        function renderLoop() {
            requestAnimationFrame(renderLoop);
            if (!isExecuting) {
                group.rotation.y += 0.01;
            }
            renderer.render(scene, camera);
        }
        renderLoop();

        window.runGachaProcess = function(count) {
            if (!isMapLoaded || isExecuting) return;

            isExecuting = true;
            setGachaButtonsState(false, "宝箱をあけている...");

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
            let duration = 3000;

            const targetColor = hasSSR ? 0xffd700 : hasSR ? 0xc0c0c0 : 0xcd7f32;
            
            // Initial reset
            lidGroup.rotation.x = 0;
            pLight.color.setHex(0xffffff);
            pLight.intensity = 1.0;

            function animate() {
                let elapsed = Date.now() - startTime;
                let progress = Math.min(elapsed / duration, 1.0);

                if (progress < 1.0) {
                    group.rotation.y += 0.05;

                    if (progress > 0.7) {
                        let openProgress = (progress - 0.7) / 0.3;
                        lidGroup.rotation.x = -Math.PI / 3 * openProgress;
                        
                        pLight.color.setHex(targetColor);
                        pLight.intensity = 1.0 + openProgress * 4.0;
                    } else {
                        // Shake before opening
                        let shake = Math.sin(progress * Math.PI * 40) * 0.05;
                        core.position.x = shake;
                    }

                    requestAnimationFrame(animate);
                } else {
                    isExecuting = false;
                    core.position.x = 0;
                    lidGroup.rotation.x = -Math.PI / 3;
                    pLight.intensity = 2.0;

                    let html = `<b>＊ 獲得アイテム (${count}件)</b><br>`;
                    results.forEach((res, idx) => {
                        let rClass = res.rarity === "SSR" ? "rarity-ssr" : res.rarity === "SR" ? "rarity-sr" : "rarity-r";
                        html += `${idx + 1}. <span class="${rClass}">${res.name}</span><br>`;
                    });
                    html += `<br>＊ ふくろに しまった！`;

                    setGachaButtonsState(isMapLoaded, html);
                }
            }
            animate();
        };

        const bagGui = document.getElementById('bag-gui');
        if (bagGui && !document.getElementById('gacha-btn-main')) {
            const btn = document.createElement('button');
            btn.id = 'gacha-btn-main';
            btn.className = 'game-btn';
            btn.innerText = 'ふくびき';
            btn.style.display = 'none'; // Hidden until map loads
            btn.onclick = () => {
                const panel = document.getElementById('gacha-floating-panel');
                panel.style.display = (panel.style.display === 'none' || panel.style.display === '') ? 'block' : 'none';
            };
            bagGui.appendChild(btn);
        }

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