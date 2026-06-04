import json
from pathlib import Path
import urllib.request

# =========================
# 取得対象年
# =========================
YEARS = [2026, 2027]

# =========================
# 観測地点
# =========================
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

# =========================
# 出力フォルダ
# =========================
Path("data").mkdir(exist_ok=True)


# =========================
# メイン処理
# =========================
for name, code in POINTS.items():
    print(f"Processing {name} ({code})...")

    tide_data_by_date = {}

    for year in YEARS:
        url = f"https://www.data.jma.go.jp/gmd/kaiyou/data/db/tide/suisan/txt/{year}/{code}.txt"

        try:
            with urllib.request.urlopen(url) as response:
                lines = response.read().decode("cp932").splitlines()

                for line in lines:

                    # =========================
                    # 最低長チェック（安全）
                    # =========================
                    if len(line) < 80:
                        continue

                    # =========================
                    # ① 潮位（固定：先頭72文字）
                    # =========================
                    tide_part = line[:72]

                    hourly_tides = []
                    for h in range(24):
                        val_str = tide_part[h*3:(h+1)*3].strip()

                        if val_str and (
                            val_str.isdigit() or
                            (val_str.startswith("-") and val_str[1:].isdigit())
                        ):
                            hourly_tides.append(int(val_str))
                        else:
                            hourly_tides.append(0)

                    # =========================
                    # ② 日付抽出（完全固定ロジック）
                    # =========================
                    qpos = line.find(code)
                    if qpos == -1:
                        continue

                    # Q位置の直前6文字 = "26 1 1" 等
                    date_raw = line[max(0, qpos-6):qpos].strip()
                    parts = date_raw.split()

                    if len(parts) != 3:
                        continue

                    y, m, d = parts

                    if not (y.isdigit() and m.isdigit() and d.isdigit()):
                        continue

                    # =========================
                    # ③ 日付フォーマット
                    # =========================
                    formatted_date = f"20{int(y):02d}-{int(m):02d}-{int(d):02d}"

                    # =========================
                    # ④ 格納
                    # =========================
                    if len(hourly_tides) == 24:
                        tide_data_by_date[formatted_date] = hourly_tides

        except Exception as e:
            print(f"  Error fetching {year} for {name}: {e}")

    # =========================
    # JSON出力
    # =========================
    output_data = {
        "station_code": code,
        "station_name": name,
        "tide_data": tide_data_by_date
    }

    with open(f"data/{name}.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

print("All done!")
