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
                # バイナリのまま1行ずつ綺麗に処理することで、文字コードによるズレを完全に防ぐ
                for line_bytes in response:
                    # 1行を文字列に変換し、前後の不要な改行を削除
                    line = line_bytes.decode("cp932").rstrip("\r\n")

                    # 資料の通り、最低限データが含まれる長さがあるかチェック
                    if len(line) < 80:
                        continue

                    # ==========================================
                    # ① 日付の取得（資料通りの73〜78カラム目 ＝ インデックス72:78）
                    # ==========================================
                    date_part = line[72:78].strip()

                    # もしスペースが含まれていたら、それは「月」や「日」が1桁の場合
                    # 例: "26 1 1" や "260101" どちらが来ても安全に分解できるようにする
                    if " " in date_part:
                        # スペース区切りの場合（例: "26  1  1"）
                        parts = date_part.split()
                        if len(parts) == 3:
                            yy = int(parts[0])
                            mm = int(parts[1])
                            dd = int(parts[2])
                        else:
                            continue
                    else:
                        # スペースなしのびっちり6桁の場合（例: "260101"）
                        if len(date_part) == 6 and date_part.isdigit():
                            yy = int(date_part[0:2])
                            mm = int(date_part[2:4])
                            dd = int(date_part[4:6])
                        else:
                            continue

                    # 正しい YYYY-MM-DD に成形
                    formatted_date = f"20{yy:02d}-{mm:02d}-{dd:02d}"

                    # ==========================================
                    # ② 観測点コードのチェック（79〜80カラム目 ＝ インデックス78:80）
                    # ==========================================
                    station = line[78:80].strip()
                    if station != code:
                        continue

                    # ==========================================
                    # ③ 潮位データのパース（1〜72カラム目 ＝ 3文字×24時間）
                    # ==========================================
                    tide_part = line[0:72]
                    hourly_tides = []

                    for h in range(24):
                        val = tide_part[h*3:(h+1)*3].strip()
                        if val == "" or val == "999":
                            hourly_tides.append(0)
                        else:
                            try:
                                hourly_tides.append(int(val))
                            except:
                                hourly_tides.append(0)

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
