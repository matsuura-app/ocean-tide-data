import json
from pathlib import Path
import urllib.request

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
                    if not line.strip() or len(line) < 80:
                        continue
                    
                    # 1. 地点コード（例: Q9, CS）の位置を特定する
                    qpos = line.find(code)
                    if qpos == -1:
                        continue
                    
                    # 2. 地点コードの位置を基準に、潮位データと日付を分解する
                    # 地点コード（qpos）より前にあるデータが「潮位＋日付」
                    # そのうち、直前の6〜7文字分（例: "26 1 1"）が日付情報
                    date_part = line[qpos-6:qpos]
                    parts = date_part.split()
                    
                    # 万が一、月の前にスペースがなくてくっついている等のイレギュラー対策で
                    # 文字数がズレた場合は、もう少し広めに取ってパースする
                    if len(parts) != 3:
                        date_part = line[qpos-7:qpos]
                        parts = date_part.split()
                        
                    if len(parts) != 3:
                        continue
                        
                    raw_year, raw_month, raw_day = parts
                    
                    # 3. 潮位データのパース（先頭から日付の手前まで、3文字ずつ区切る）
                    # 確実に24時間分（72文字分）を取り出します
                    tide_part = line[0:72]
                    hourly_tides = []
                    for h in range(24):
                        val_str = tide_part[h*3:(h+1)*3].strip()
                        if val_str and (val_str.isdigit() or (val_str.startswith('-') and val_str[1:].isdigit())):
                            hourly_tides.append(int(val_str))
                        else:
                            hourly_tides.append(0)
                    
                    # 4. 正しい日付フォーマット（YYYY-MM-DD）に整形して格納
                    # 年が「26」のように2桁の数字であることを確認
                    if raw_year.isdigit() and raw_month.isdigit() and raw_day.isdigit():
                        formatted_date = f"20{raw_year.zfill(2)}-{raw_month.zfill(2)}-{raw_day.zfill(2)}"
                        
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
