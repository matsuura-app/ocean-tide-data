import json
from pathlib import Path
import urllib.request

# 2年分（2026年と2027年など）のデータを取得する場合
YEARS = [2026, 2027]

POINTS = {
    "otaru": "B3",      # 小樽（北海道）
    "kushiro": "KR",    # 釧路（北海道）
    "sendai": "SD",     # 仙台（太平洋）
    "choshi": "CS",     # 銚子（太平洋）
    "kushimoto": "KS",  # 串本（太平洋）
    "kure": "Q9",       # 呉（瀬戸内海）
    "hakata": "QF",     # 博多（日本海/九州）
    "niigata": "S6",    # 新潟（日本海）
    "sakai": "SK",      # 境（日本海）
    "miyazaki": "MG",   # 宮崎（太平洋）
    "okinawa": "ZO"     # 沖縄
}

Path("data").mkdir(exist_ok=True)

for name, code in POINTS.items():
    print(f"Processing {name} ({code})...")
    
    # Swift側で扱いやすい構造（日付をキーにした辞書など）にする
    tide_data_by_date = {}

    for year in YEARS:
        # 気象庁のデータURL
        url = f"https://www.data.jma.go.jp/gmd/kaiyou/data/db/tide/suisan/txt/{year}/{code}.txt"
        
        try:
            with urllib.request.urlopen(url) as response:
                # 気象庁のデータは shift_jis または cp932
                lines = response.read().decode('cp932').splitlines()
                
                for line in lines:
                    if not line.strip():
                        continue
                    
                    # 気象庁フォーマットの解析（固定長切り出し）
                    # 0-6文字目: 日付 (例: "260101" -> 2026年01月01日)
                    date_str = line[0:6]
                    # 西暦4桁の上位2桁を補完（例: "260101" -> "2026-01-01"）
                    formatted_date = f"20{date_str[0:2]}-{date_str[2:4]}-{date_str[4:6]}"
                    
                    # 7文字目から、3文字ずつ×24時間分の潮位（センチメートル単位）
                    hourly_tides = []
                    for h in range(24):
                        start_idx = 7 + (h * 3)
                        # 空白交じりの3文字を数値化
                        val_str = line[start_idx:start_idx+3].strip()
                        hourly_tides.append(int(val_str) if val_str else 0)
                    
                    tide_data_by_date[formatted_date] = hourly_tides
                    
        except Exception as e:
            print(f"  Error fetching {year} for {name}: {e}")

    # 最終的なJSON構造
    output_data = {
        "station_code": code,
        "station_name": name,
        "tide_data": tide_data_by_date  # {"2026-01-01": [120, 110, ... 24個], "2026-01-02": [...]}
    }

    with open(f"data/{name}.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

print("All done!")
