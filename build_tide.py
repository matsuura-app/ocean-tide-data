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
                    # 公式仕様: 136カラム（文字）ある固定長。データが欠損している行などを除外
                    if len(line) < 80:
                        continue

                    # ==========================================
                    # ① 観測点コードのチェック（79〜80カラム ＝ インデックス78:80）
                    # ==========================================
                    station = line[78:80].strip()
                    if station != code:
                        continue

                    # ==========================================
                    # ② 年月日の抽出（73〜78カラム ＝ 2桁×3）
                    # ==========================================
                    # 2文字ずつ固定で切り出して、個別に前後のスペースを削除する
                    raw_yy = line[72:74].strip()
                    raw_mm = line[74:76].strip()
                    raw_dd = line[76:78].strip()

                    # スペースを消した状態で、すべて数字になっているか確認
                    if not (raw_yy.isdigit() and raw_mm.isdigit() and raw_dd.isdigit()):
                        continue

                    # int型に変換してから綺麗に 0埋めフォーマット（例: "26", " 1", " 1" -> "2026-01-01"）
                    formatted_date = f"20{int(raw_yy):02d}-{int(raw_mm):02d}-{int(raw_dd):02d}"

                    # ==========================================
                    # ③ 毎時潮位の取得（1〜72カラム ＝ 3桁×24時間）
                    # ==========================================
                    tide_part = line[0:72]
                    hourly_tides = []

                    for h in range(24):
                        val = tide_part[h*3:(h+1)*3].strip()
                        # 欠測や空っぽの場合は 0 に、正常な数字はintに変換
                        if val == "" or val == "999":
                            hourly_tides.append(0)
                        else:
                            try:
                                hourly_tides.append(int(val))
                            except:
                                hourly_tides.append(0)

                    # 24時間分しっかり揃っていればデータに採用
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
