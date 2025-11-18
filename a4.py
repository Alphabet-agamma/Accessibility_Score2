import pandas as pd

# =====================================================
# 1. 파일 불러오기
# =====================================================

input_file = "merged_clean_with_accessibility.xlsx"
output_file = "merged_clean_with_accessibility_normalized.xlsx"

print("📂 입력 파일:", input_file)

df = pd.read_excel(input_file)

if "accessibility_raw" not in df.columns:
    raise ValueError("❌ ERROR: accessibility_raw 컬럼이 파일에 존재하지 않습니다.")

# =====================================================
# 2. 정규화 수행 (Chen et al. 2023, Equation (8))
# =====================================================

print("\n=== [STEP 1] 접근성 정규화 시작 ===")

A = df["accessibility_raw"]
A_min = A.min()
A_max = A.max()

print(f"A_min = {A_min}")
print(f"A_max = {A_max}")

if A_max - A_min == 0:
    print("\n⚠ WARNING: 모든 접근성 값이 동일합니다. 정규화 결과는 모두 0으로 설정됩니다.")
    df["accessibility_norm"] = 0
else:
    df["accessibility_norm"] = (A - A_min) / (A_max - A_min)

# =====================================================
# 3. 디버깅 출력
# =====================================================

print("\n=== 정규화 결과 샘플 ===")
print(df[["place_name", "accessibility_raw", "accessibility_norm"]].head())

print("\n=== 정규화 통계 ===")
print(df["accessibility_norm"].describe())

# =====================================================
# 4. 저장
# =====================================================

df.to_excel(output_file, index=False)
print("\n🎉 정규화 완료!")
print("👉 저장됨:", output_file)
