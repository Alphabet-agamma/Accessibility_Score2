import pandas as pd

# 서울 경계 (대략 범위)
SEOUL_LAT_MIN = 37.40
SEOUL_LAT_MAX = 37.70
SEOUL_LNG_MIN = 126.75
SEOUL_LNG_MAX = 127.20

df = pd.read_excel("merged_with_kakao_latlon_filled_google.xlsx")

# 좌표 결측 제거
df = df.dropna(subset=["latitude", "longitude"])

# Boolean mask
mask_outlier = ~(
    (df["latitude"].between(SEOUL_LAT_MIN, SEOUL_LAT_MAX)) &
    (df["longitude"].between(SEOUL_LNG_MIN, SEOUL_LNG_MAX))
)

# 분리 저장
df_outliers = df[mask_outlier]         # 서울 밖 좌표들
df_normal   = df[~mask_outlier]        # 정상적인 서울 내 좌표들

df_outliers.to_excel("outlier_locations.xlsx", index=False)
df_normal.to_excel("normal_locations.xlsx", index=False)

print("완료!")
print(f"서울 밖 좌표 개수: {len(df_outliers)}")
print("파일 생성: outlier_locations.xlsx / normal_locations.xlsx")
