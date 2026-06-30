import json
from pathlib import Path
import urllib.request
from datetime import datetime
current_year = datetime.now().year
YEARS = [current_year, current_year + 1]

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
            txt = urllib.request.urlopen(url).read().decode("cp932")
            for line in txt.splitlines():
                if len(line) < 80:
                    continue
                
                # 24時間潮位
                hourly_tides = []
                for h in range(24):
                    v = line[h*3:(h+1)*3].strip()
                    try:
                        hourly_tides.append(int(v))
                    except:
                        hourly_tides.append(0)
                
                # 固定長の日付
                yy = line[72:74].strip()
                mm = line[74:76].strip()
                dd = line[76:78].strip()
                st = line[78:80].strip()
                
                if st != code:
                    continue
                
                # 【安全対策】日付が空欄（欠測）だった場合にエラーで落ちないようにガード
                try:
                    formatted_date = (
                        f"20{int(yy):02d}-"
                        f"{int(mm):02d}-"
                        f"{int(dd):02d}"
                    )
                except ValueError:
                    # 日付が数字に変換できない（空欄などの）場合はこの行をスキップ
                    continue
                
                tide_data_by_date[formatted_date] = hourly_tides
                
        except Exception as e:
            print(name, year, e)
            
    output_data = {
        "station_code": code,
        "station_name": name,
        "tide_data": tide_data_by_date
    }
    
    with open(f"data/{name}.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

print("All done!")
