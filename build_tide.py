import json
from pathlib import Path
import urllib.request
import re

# 2026年と2027年の2年分を取得
YEARS = [2026, 2027]

POINTS = {
    "otaru": "B3",      # 小樽
    "kushiro": "KR",    # 釧路
    "sendai": "SD",     # 仙台
    "choshi": "CS",     # 銚子
    "kushimoto": "KS",  # 串本
    "kure": "Q9",       # 呉
    "hakata": "QF",     # 博多
    "niigata": "S6",    # 新潟
    "sakai": "SK",      # 境
    "miyazaki": "MG",   # 宮崎
    "okinawa": "ZO"     # 沖縄
}

Path("data").mkdir(exist_ok=True)

for name, code in POINTS.items():
    print(f"Processing {name} ({code})...")
    tide_data_by_date = {}

    for year in YEARS:
        url = f"https://www.data.jma.go.jp/gmd/kaiyou/data/db/tide/suisan/txt/{year}/{code}.txt"
        
        try:
            with urllib.request.urlopen(url) as response:
                lines = response.read().decode('cp932').splitlines()
                
                for line in lines:
                    if not line.strip() or len(line) < 75:
                        continue
                    
                    # 1. 【スクショの完全移植】地点コードの直前にある「年 月 日」を正規表現で安全に抽出
                    m = re.search(rf"(\d{{2}})\s+(\d{{1,2}})\s+(\d{{1,2}}){code}", line)
                    
                    if not m:
                        continue
                    
                    raw_year, raw_month, raw_day = m.groups()
                    
                    # 2. 潮位データのパース（先頭72文字、3文字×24時間）
                    tide_part = line[0:72]
                    hourly_tides = []
                    for h in range(24):
                        val_str = tide_part[h*3:(h+1)*3].strip()
                        if val_str and (val_str.isdigit() or (val_str.startswith('-') and val_str[1:].isdigit())):
                            hourly_tides.append(int(val_str))
                        else:
                            hourly_tides.append(0)
                    
                    # 3. YYYY-MM-DD フォーマットに整形（intに変換してから0埋め）
                    formatted_date = (
                        f"20{raw_year}-"
                        f"{int(raw_month):02d}-"
                        f"{int(raw_day):02d}"
                    )
                    
                    if len(hourly_tides) == 24:
                        tide_data_by_date[formatted_date] = hourly_tides
                        
        except Exception as e:
            print(f"  Error fetching {year} for {name}: {e}")

    output_data = {
        "station_code": code,
        "station_name": name,
        "tide_data": tide_data_by_date
    }

    with open(f"data/{name}.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

print("All done!")
