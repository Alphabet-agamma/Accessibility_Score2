import pandas as pd

# 입력 파일들
df_normal = pd.read_excel("normal_locations.xlsx")
df_fixed  = pd.read_excel("fixed_outliers.xlsx")

# corrected 좌표를 원본 좌표로 덮어쓰기
df_fixed["latitude"]  = df_fixed["latitude_corrected"]
df_fixed["longitude"] = df_fixed["longitude_corrected"]

# 필요 없는 열 삭제
df_fixed = df_fixed.drop(columns=["latitude_corrected", "longitude_corrected"])

# 병합
df_clean = pd.concat([df_normal, df_fixed], ignore_index=True)

# 저장
df_clean.to_excel("merged_clean.xlsx", index=False)

print("🎉 최종 클린 파일 생성 → merged_clean.xlsx")
