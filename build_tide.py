import json
from pathlib import Path
import urllib.request

YEARS = [2026, 2027]

POINTS = {
    "otaru": "B3",
    "kushiro": "KR",
    "sendai": "SD",
    "choshi": "CS",
    "kushimoto": "KS",
    "kure": "Q9",
    "hakata": "QF",
    "niigata": "S6",
    "sakai": "SK",
    "miyazaki": "MG",
    "okinawa": "ZO"
}

Path("data").mkdir(exist_ok=True)

for name, code in POINTS.items():
    print(f"Processing {name} ({code})...")
    tide_data_by_date = {}

    for year in YEARS:
        url = f"https://www.data.jma.go.jp/gmd/kaiyou/data/db/tide/suisan/txt/{year}/{code}.txt"

        try:
            with urllib.request.urlopen(url) as response:
                lines = response.read().decode("cp932").splitlines()

                for line in lines:
                    # 観測点コードが格納されている79〜80カラム目（インデックス78:80）をチェック
                    if len(line) < 80:
                        continue
                    
                    station = line[78:80].strip()
                    if station != code:
                        continue

                    # =========================
                    # ① 日付のパース（73〜78カラム目を安全に分解）
                    # =========================
                    # 例: "15 116" や "26 1 1" などのスペース混じりの6文字を取得
                    date_part = line[72:78]
                    
                    # 2文字ずつ正確に切り出す
                    raw_yy = date_part[0:2].strip()
                    raw_mm = date_part[2:4].strip()
                    raw_dd = date_part[4:6].strip()

                    # すべて数字に変換できるか確認（スペースを排除しているためisdigitで判定可能）
                    if not (raw_yy.isdigit() and raw_mm.isdigit() and raw_dd.isdigit()):
                        continue

                    # int型にキャストして 0埋めフォーマット（例: 26, 1, 1 -> 2026-01-01）
                    formatted_date = f"20{int(raw_yy):02d}-{int(raw_mm):02d}-{int(raw_day := raw_dd):02d}"

                    # =========================
                    # ② 潮位データのパース（1〜72カラム目を3文字ずつ取得）
                    # =========================
                    tide_part = line[0:72]
                    hourly_tides = []

                    for h in range(24):
                        val = tide_part[h*3:(h+1)*3].strip()
                        # 欠測値 "999" や空文字は 0 に置き換える
                        if val == "" or val == "999":
                            hourly_tides.append(0)
                        else:
                            try:
                                hourly_tides.append(int(val))
                            except:
                                hourly_tides.append(0)

                    # 24時間分しっかり揃っていれば採用
                    if len(hourly_tides) == 24:
                        tide_data_by_date[formatted_date] = hourly_tides

        except Exception as e:
            print(f"Error {year} {name}: {e}")

    output = {
        "station_code": code,
        "station_name": name,
        "tide_data": tide_data_by_date
    }

    with open(f"data/{name}.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

print("All done!")
