import pandas as pd
import requests
from tqdm import tqdm
import time

# ===============================
# ⚙️ 설정
# ===============================
input_file = "merged_raw.xlsx"         # 이전 단계에서 생성된 파일
output_file = "merged_with_kakao_latlon.xlsx"
KAKAO_API_KEY = "f0291e3edfb99204ad274e5fe07bb1d8"  # 🔑 본인 키로 교체

# ===============================
# 📍 1️⃣ 데이터 불러오기
# ===============================
merged_df = pd.read_excel(input_file)
print(f"✅ 데이터 로드 완료: {merged_df.shape[0]}개 행")

# ===============================
# 📍 2️⃣ Kakao API로 주소 → 위경도 변환
# ===============================
def kakao_geocode(query):
    """카카오 API를 이용한 주소/장소명 → 위경도 변환"""
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": query}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        result = response.json()
        if result.get("documents"):
            lat = float(result["documents"][0]["y"])
            lon = float(result["documents"][0]["x"])
            return lat, lon
        else:
            return None, None
    except Exception:
        return None, None


lat_list, lon_list = [], []

for i, row in tqdm(merged_df.iterrows(), total=len(merged_df), desc="주소/명칭 → 위경도 변환 중"):
    addr = row.get("address", "")
    name = row.get("place_name", "")

    # ① 주소로 시도
    lat, lon = kakao_geocode(addr) if pd.notna(addr) and addr else (None, None)

    # ② 주소 실패 시 관광지명(place_name)으로 재시도
    if lat is None or lon is None:
        lat, lon = kakao_geocode(name)
        time.sleep(0.2)  # API 요청 제한 방지

    lat_list.append(lat)
    lon_list.append(lon)

merged_df["latitude"] = lat_list
merged_df["longitude"] = lon_list

# ===============================
# 💾 3️⃣ 결과 저장
# ===============================
merged_df.to_excel(output_file, index=False)
print(f"🎯 최종 결과 저장 완료: {output_file}")
