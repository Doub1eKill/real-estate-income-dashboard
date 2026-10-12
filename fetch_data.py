"""ดึงข้อมูลล่าสุดจาก data.go.th (CKAN Datastore API) แล้วบันทึกเป็น data/income_real_estate.csv

ชุดข้อมูล: รายได้จากการซื้อขายอสังหาริมทรัพย์ (กรมที่ดิน)
https://data.go.th/dataset/income-2

ใช้งาน:  python fetch_data.py
"""
import csv
import json
import sys
import urllib.request
from pathlib import Path

API = "https://data.go.th/api/3/action"
DATASET_ID = "income-2"
OUT = Path(__file__).parent / "data" / "income_real_estate.csv"


def get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "streamlit-dashboard"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)["result"]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # ให้พิมพ์ภาษาไทยบน Windows console ได้
    package = get(f"{API}/package_show?id={DATASET_ID}")
    rows = []
    for res in package["resources"]:
        if not res.get("datastore_active"):
            continue
        print("ดึงข้อมูล:", res["name"])
        result = get(f"{API}/datastore_search?limit=10000&resource_id={res['id']}")
        for r in result["records"]:
            rows.append([r["ปี"], r["ภาค"], r["ประเภทรายได้"], r["บาท"]])

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["year", "region", "income_type", "amount_baht"])
        writer.writerows(rows)
    print(f"บันทึก {len(rows)} แถว -> {OUT}")


if __name__ == "__main__":
    main()
