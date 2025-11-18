import pandas as pd
import requests
import time

GOOGLE_API_KEY = "AIzaSyAWMvmfquPx_IO6BTs4xiGRIqBmV3kxl5Y"

def geocode(address):
    """주소 → 위경도 변환"""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "language": "ko",
        "region": "kr",
        "key": GOOGLE_API_KEY
    }
    r = requests.get(url, params=params).json()

    if r["status"] != "OK":
        print("❌ Geocode 실패:", r["status"], address)
        return None, None

    loc = r["results"][0]["geometry"]["location"]
    return loc["lat"], loc["lng"]


# 이상치 불러오기
df_out = pd.read_excel("outlier_locations.xlsx")

# 결과 저장용
new_lats = []
new_lngs = []

for idx, row in df_out.iterrows():
    addr = row["address"]
    print(f"📍 재조회 중: {addr}")

    lat, lng = geocode(addr)
    new_lats.append(lat)
    new_lngs.append(lng)

    time.sleep(0.15)   # rate limit 보호


df_out["latitude_corrected"] = new_lats
df_out["longitude_corrected"] = new_lngs

df_out.to_excel("fixed_outliers.xlsx", index=False)
print("🎉 이상치 좌표 자동 재조회 완료 → fixed_outliers.xlsx 생성")
