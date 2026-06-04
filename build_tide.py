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
                    if len(line) < 80: # 日付や地点コードが含まれる位置まで最低限あるかチェック
                        continue
                    
                    # 1. 先頭の72文字（3文字×24時間）を潮位データとして切り出す
                    tide_part = line[0:72]
                    hourly_tides = []
                    for h in range(24):
                        val_str = tide_part[h*3:(h+1)*3].strip()
                        if val_str and (val_str.isdigit() or (val_str.startswith('-') and val_str[1:].isdigit())):
                            hourly_tides.append(int(val_str))
                        else:
                            hourly_tides.append(0)
                    
                    # 2. 72文字目以降にあるはずの「日付」と「地点コード」を探す
                    # 例: "26 1 1Q9" や "260101Q9" などのパターンを正規表現で安全に抽出
                    # 72文字目から15文字分くらいをターゲットにする
                    meta_part = line[72:90]
                    
                    # スペースを含めて「年 月 日 地点コード」の並びを抽出
                    # 例: "26  1  1Q9" -> ['26', '1', '1', 'Q9']
                    match = re.findall(r'\d+|[A-Z0-9]{2}', meta_part)
                    
                    if len(match) >= 4:
                        y = match[0].strip().zfill(2)
                        m = match[1].strip().zfill(2)
                        d = match[2].strip().zfill(2)
                        station = match[3].strip()
                        
                        # 自信のある地点コードと一致している場合のみ採用
                        if station == code and len(hourly_tides) == 24:
                            formatted_date = f"20{y}-{m}-{d}"
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
