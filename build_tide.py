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
                    # 気象庁フォーマット: 最低でも毎時潮位（72文字）＋日付等（7文字以上）が必要
                    if len(line) < 72:
                        continue
                    
                    # 0〜6文字目から日付を安全に抽出（スペースを除去）
                    # 例: "26 1 1" や "260101" などの表記揺れをすべてカバー
                    raw_date = line[0:6]
                    
                    # 年、月、日を2文字ずつの固定長で安全に切り出す
                    y = raw_date[0:2].strip().zfill(2)
                    m = raw_date[2:4].strip().zfill(2)
                    d = raw_date[4:6].strip().zfill(2)
                    
                    if not (y.isdigit() and m.isdigit() and d.isdigit()):
                        continue
                        
                    formatted_date = f"20{y}-{m}-{d}"
                    
                    # 毎時潮位は 6文字目から 3文字ずつ 24時間分（計72文字）
                    hourly_tides = []
                    tide_part = line[6:78]
                    
                    for h in range(24):
                        start = h * 3
                        end = start + 3
                        val_str = tide_part[start:end].strip()
                        
                        # 数字、またはマイナスから始まる数字（負の潮位）を安全にパース
                        if val_str and (val_str.isdigit() or (val_str.startswith('-') and val_str[1:].isdigit())):
                            hourly_tides.append(int(val_str))
                        else:
                            # 予期せぬ空欄などの場合は、前後の値から補完するか0にする
                            hourly_tides.append(0)
                    
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
