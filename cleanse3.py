import pandas as pd
import os
import re
from deep_translator import GoogleTranslator

# ===============================
# ⚙️ 설정
# ===============================
input_files = [
    "서울시_공영주차장_위치정보.xlsx",
    "서울시_버스정류소_위치정보.xlsx",
    "서울지하철역_위경도.xlsx",
]
output_folder = "standardized_excels"
os.makedirs(output_folder, exist_ok=True)

# ===============================
# 🧩 1️⃣ 번역기 초기화
# ===============================
translator = GoogleTranslator()

# ===============================
# 🧩 2️⃣ 의미가 같은 컬럼 통합 사전
# ===============================
# 번역된 결과가 달라도 같은 의미면 강제로 통일
manual_map = {
    "주차장명": "place_name",
    "정류소명": "place_name",
    "역명": "place_name",
    "station_name": "place_name",
    "정류장명": "place_name",
    "소재지도로명주소": "address",
    "소재지지번주소": "address",
    "주소": "address",
    "location": "address",
    "위치": "address",
    "위도": "latitude",
    "경도": "longitude",
    "latitude": "latitude",
    "longitude": "longitude",
    "위치_x좌표": "longitude",
    "위치_y좌표": "latitude",
    "관리번호": "id",
    "정류소id": "id",
    "정류소_id": "id",
    "노선번호": "route_number",
    "운영요일": "operating_days",
    "급지구분": "zone_type",
}

# ===============================
# 🧩 3️⃣ 컬럼명 표준화 함수
# ===============================
def clean_and_translate_columns(columns):
    new_cols = []
    for col in columns:
        col_clean = col.strip().replace(" ", "_").replace("(", "").replace(")", "")
        
        # 한글 번역
        try:
            translated = GoogleTranslator(source="ko", target="en").translate(col_clean)
            translated = translated.lower().strip().replace(" ", "_")
            new_cols.append(translated)
        except Exception:
            new_cols.append(col_clean.lower())
    return new_cols


# ===============================
# 🧩 4️⃣ 파일별 처리
# ===============================
for file in input_files:
    print(f"📄 {file} 처리 중...")
    df = pd.read_excel(file, engine="openpyxl")

    # 번역 + 표준화
    df.columns = clean_and_translate_columns(df.columns)

    # 저장
    output_path = os.path.join(output_folder, os.path.basename(file))
    df.to_excel(output_path, index=False)
    print(f"✅ 완료: {output_path}")

print("🎯 모든 파일의 컬럼명이 영어로 변환 및 통일되었습니다!")
