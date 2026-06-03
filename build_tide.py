import json

POINTS = {
    "otaru": "B3",
    "kushiro": "KR",
    "sendai": "SD",
    "choshi": "CS",
    "kushimoto": "KS",
    "kure": "Q9",
    "miyazaki": "MG",
    "okinawa": "ZO",
    "hakata": "QF",
    "niigata": "S6",
    "sakai": "SK"
}

for name, code in POINTS.items():
    data = {
        "station": code,
        "name": name
    }

    with open(
        f"data/{name}.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

print("done")