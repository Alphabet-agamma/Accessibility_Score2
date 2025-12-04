import pandas as pd
import requests
import time
import numpy as np

# -----------------------------
# ⚙️ 설정
# -----------------------------
input_file = "merged_all_csvs.xlsx"
output_file = "merged_all_csvs_geocoded.xlsx"

# 🔑 구글 API 키 입력
GOOGLE_API_KEY = "AIzaSyCDf8M1Dq8dj4p56alcR50MhiBlIWqwHIM"

# -----------------------------
# 1️⃣ 데이터 불러오기
# -----------------------------
# ❗엑셀 파일은 read_excel로 불러야 함
df = pd.read_excel(input_file)
print(f"✅ 데이터 로드 완료: {df.shape}")

# -----------------------------
# 2️⃣ 위경도 결측 행만 추출
# -----------------------------
mask_missing = df["위도"].isna() | df["경도"].isna()
missing_df = df[mask_missing]
print(f"📍 결측 위경도 행 수: {len(missing_df)}")

# -----------------------------
# 3️⃣ Google Geocoding API 함수
# -----------------------------
def geocode_address(address):
    """주소 문자열을 받아 구글 지오코딩 API로 위경도 반환"""
    if not isinstance(address, str) or address.strip() == "":
        return None, None
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": GOOGLE_API_KEY}
        response = requests.get(url, params=params)
        result = response.json()

        if result["status"] == "OK":
            location = result["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            return None, None
    except Exception as e:
        print(f"⚠️ 오류 ({address}): {e}")
        return None, None

# -----------------------------
# 4️⃣ 결측 좌표 채우기
# -----------------------------
filled_count = 0

for idx, row in missing_df.iterrows():
    lat, lon = None, None

    for col in ["소재지도로명주소", "소재지지번주소", "주차장명"]:
        value = row.get(col, "")
        if isinstance(value, str) and value.strip():
            lat, lon = geocode_address(value)
            if lat and lon:
                break  # 성공 시 종료

    if lat and lon:
        df.at[idx, "위도"] = lat
        df.at[idx, "경도"] = lon
        filled_count += 1

    time.sleep(0.3)  # API 요청 제한

print(f"✅ 좌표 채움 완료: {filled_count}개 업데이트됨")

# -----------------------------
# 5️⃣ 결과 저장
# -----------------------------
df.to_excel(output_file, index=False)
print(f"💾 결과 저장 완료: {output_file}")

# -----------------------------
# 6️⃣ 요약 출력
# -----------------------------
remaining_missing = df["위도"].isna().sum() + df["경도"].isna().sum()
print(f"📊 남은 결측 좌표 수: {remaining_missing // 2}개")
