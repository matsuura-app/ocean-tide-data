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

                    if len(line) < 80:
                        continue

                    # =========================
                    # ① 潮位（1-72）
                    # =========================
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

                    # =========================
                    # ② 日付（73-78 = yymmdd）
                    # =========================
                    date_part = line[72:78]

                    if len(date_part) != 6 or not date_part.isdigit():
                        continue

                    yy = int(date_part[0:2])
                    mm = int(date_part[2:4])
                    dd = int(date_part[4:6])

                    formatted_date = f"20{yy:02d}-{mm:02d}-{dd:02d}"

                    # =========================
                    # ③ 観測点コード（79-80）
                    # =========================
                    station = line[78:80].strip()

                    if station != code:
                        continue

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
