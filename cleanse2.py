import pandas as pd
import re

# -----------------------------
# ⚙️ 설정
# -----------------------------
input_file = "merged_all_csvs_geocoded.xlsx"
output_file = "seoul_parking_cleaned.xlsx"

# -----------------------------
# 1️⃣ 데이터 불러오기
# -----------------------------
df = pd.read_excel(input_file)
print(f"✅ 원본 데이터 로드 완료: {df.shape}")

# -----------------------------
# 2️⃣ 필요한 컬럼만 남기기
# -----------------------------
cols_to_keep = [
    "주차장명",
    "소재지도로명주소",
    "소재지지번주소",
    "주차구획수",
    "급지구분",
    "운영요일",
    "요금정보",
    "위도",
    "경도",
]
df = df[cols_to_keep]
print(f"✅ 주요 컬럼만 선택: {df.shape}")

# -----------------------------
# 3️⃣ 주소 기반 '시군구' 추출
# -----------------------------

def extract_sigungu(row):
    """도로명주소 또는 지번주소에서 '서울특별시 ~구' 패턴 추출"""
    text = row["소재지도로명주소"]
    if pd.isna(text) or not isinstance(text, str) or text.strip() == "":
        text = row["소재지지번주소"]
    if pd.isna(text) or not isinstance(text, str):
        return None

    match = re.search(r"(서울특별시\s?[가-힣]{1,3}구)", text)
    if match:
        return match.group(1)
    else:
        return None

df["시군구"] = df.apply(extract_sigungu, axis=1)

# -----------------------------
# 4️⃣ 불필요한 주소 컬럼 삭제
# -----------------------------
df = df.drop(columns=["소재지도로명주소", "소재지지번주소"])
print("🧹 주소 컬럼 삭제 완료")

# -----------------------------
# 5️⃣ 결과 저장
# -----------------------------
df.to_excel(output_file, index=False)
print(f"💾 데이터 정제 및 저장 완료: {output_file}")

# -----------------------------
# 6️⃣ 결과 미리보기
# -----------------------------
print("\n📄 샘플 미리보기:")
print(df.head(10)[["주차장명", "시군구", "주차구획수", "급지구분", "요금정보"]])
