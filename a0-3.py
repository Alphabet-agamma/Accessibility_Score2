import pandas as pd
import requests
from tqdm import tqdm
import time

# ===============================
# ⚙️ 설정
# ===============================
input_file = "merged_with_kakao_latlon.xlsx"        # 기존 결과 파일
output_file = "merged_with_kakao_latlon_filled_google.xlsx"
GOOGLE_API_KEY = "AIzaSyCDf8M1Dq8dj4p56alcR50MhiBlIWqwHIM"  # 🔑 본인 Google API 키로 교체

# ===============================
# 📍 1️⃣ 데이터 불러오기
# ===============================
df = pd.read_excel(input_file)
print(f"✅ 데이터 로드 완료: {df.shape[0]}개 행")

# 위도 또는 경도가 비어 있는 행만 필터링
missing_df = df[df["latitude"].isna() | df["longitude"].isna()].copy()
print(f"⚠️ 좌표 누락 행 수: {missing_df.shape[0]}개")

if missing_df.empty:
    print("🎯 모든 행에 좌표가 있습니다. 보완 작업 불필요.")
    exit()

# ===============================
# 📍 2️⃣ Google Maps Geocoding 함수
# ===============================
def google_geocode(address, api_key):
    """Google Maps API를 이용한 주소 → 위경도 변환"""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key, "language": "ko"}
    try:
        response = requests.get(url, params=params, timeout=8)
        result = response.json()
        if result["status"] == "OK":
            lat = result["results"][0]["geometry"]["location"]["lat"]
            lon = result["results"][0]["geometry"]["location"]["lng"]
            return lat, lon
        else:
            return None, None
    except Exception:
        return None, None

# ===============================
# 📍 3️⃣ 누락 좌표 채우기
# ===============================
lat_filled, lon_filled = [], []

for i, row in tqdm(missing_df.iterrows(), total=len(missing_df), desc="Google Maps로 좌표 보완 중"):
    address = row.get("address", "")
    if not address or pd.isna(address):
        lat_filled.append(None)
        lon_filled.append(None)
        continue

    lat, lon = google_geocode(address, GOOGLE_API_KEY)
    lat_filled.append(lat)
    lon_filled.append(lon)
    time.sleep(0.1)  # API 요청 속도 제한 (10회/초 이하 권장)

missing_df["latitude"] = lat_filled
missing_df["longitude"] = lon_filled

# ===============================
# 📍 4️⃣ 원본 데이터 업데이트
# ===============================
updated_df = df.copy()

for idx, row in missing_df.iterrows():
    if pd.notna(row["latitude"]) and pd.notna(row["longitude"]):
        updated_df.loc[idx, "latitude"] = row["latitude"]
        updated_df.loc[idx, "longitude"] = row["longitude"]

# ===============================
# 💾 5️⃣ 최종 저장
# ===============================
updated_df.to_excel(output_file, index=False)
print(f"🎯 Google Maps로 좌표 보완 완료: {output_file}")
