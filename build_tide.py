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
                    # 水産フォーマットは最低限の長さ（80文字以上）があるかチェック
                    if len(line) < 80:
                        continue
                    
                    # 1. 先頭72文字（3文字 × 24時間）から潮位を確実に1時間ずつ取得
                    tide_part = line[0:72]
                    hourly_tides = []
                    for h in range(24):
                        val_str = tide_part[h*3:(h+1)*3].strip()
                        # 数字、またはマイナスから始まる数字
                        if val_str and (val_str.isdigit() or (val_str.startswith('-') and val_str[1:].isdigit())):
                            hourly_tides.append(int(val_str))
                        else:
                            hourly_tides.append(0)
                    
                    # 2. 【ここが固定長】72文字目〜80文字目から「年」「月」「日」「地点」をピンポイント抽出
                    # 気象庁の仕様: 72-74:年(2桁), 74-76:月(2桁), 76-78:日(2桁), 78-80:地点コード
                    raw_year  = line[72:74].strip()
                    raw_month = line[74:76].strip()
                    raw_day   = line[76:78].strip()
                    raw_code  = line[78:80].strip()
                    
                    # 抽出した地点コードが一致し、年月日がすべて数字のときだけ採用
                    if raw_code == code and raw_year.isdigit() and raw_month.isdigit() and raw_day.isdigit():
                        # strip() しているので、1桁の数字（" 1" など）でも正しく "01" に埋められます
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
