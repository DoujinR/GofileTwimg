#!/usr/bin/env python3
import os, json, subprocess, requests, time

# --- 設定 ---
API_BASE = "https://api.gofile.io"
JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "videos.json")
THUMB_DIR = os.path.join(os.path.dirname(__file__), "..", "thumbnails")

# フォルダ作成
os.makedirs(THUMB_DIR, exist_ok=True)

# JSON 読み込み
with open(JSON_PATH, encoding="utf-8") as f:
    videos = json.load(f)

# 各動画について処理
for v in videos:
    file_id = v["url"].rstrip("/").split("/")[-1]
    thumb_path = os.path.join(THUMB_DIR, f"{file_id}.png")
    # 既に生成済みならスキップ
    if os.path.exists(thumb_path):
        v["thumbnail"] = f"thumbnails/{file_id}.png"
        continue

    # 1) サーバー取得（無料枠でも動く / rate-limit かからない程度に sleep を入れる）
    res = requests.get(f"{API_BASE}/getServer?c={file_id}")
    data = res.json()
    if data["status"] != "ok":
        print(f"ERROR: サーバー取得失敗 for {file_id}", data)
        continue
    server = data["data"]["server"]
    raw_url = f"https://{server}.gofile.io/download/{file_id}"

    # 2) ffmpeg で１フレーム目を切り出し
    print(f"Generating thumbnail for {file_id} ...")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-ss", "00:00:01",
        "-i", raw_url,
        "-frames:v", "1",
        "-q:v", "2",
        thumb_path
    ], check=False)

    # 3) JSON に thumbnail パスをセット
    v["thumbnail"] = f"thumbnails/{file_id}.png"

    # 過度な API 呼び出し防止
    time.sleep(1)

# 4) JSON 上書き
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(videos, f, ensure_ascii=False, indent=2)

print("Done. videos.json and thumbnails/ updated.")
