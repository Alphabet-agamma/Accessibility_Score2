import pandas as pd
import glob
import os
import chardet  # 인코딩 자동 감지용 (설치 필요: pip install chardet)

# -----------------------------
# ⚙️ 설정
# -----------------------------
input_folder = "C:/Users/nangg/public_transport/Seoul_parking"
output_file = "merged_all_csvs.xlsx"

# -----------------------------
# 1️⃣ 폴더 내 CSV 파일 탐색
# -----------------------------
csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
print(f"📂 발견된 CSV 파일 수: {len(csv_files)}")

if not csv_files:
    raise FileNotFoundError("❌ CSV 파일이 폴더 내에 없습니다.")

# -----------------------------
# 2️⃣ 파일별 데이터프레임 불러오기
# -----------------------------
merged_df_list = []

for file in csv_files:
    try:
        # 인코딩 자동 감지
        with open(file, "rb") as f:
            encoding = chardet.detect(f.read(10000))["encoding"]

        df = pd.read_csv(file, encoding=encoding)
        df["source_file"] = os.path.basename(file)
        merged_df_list.append(df)
        print(f"✅ 불러오기 성공: {os.path.basename(file)} ({df.shape[0]}행, 인코딩={encoding})")

    except Exception as e:
        print(f"⚠️ 오류 발생: {os.path.basename(file)} → {e}")

# -----------------------------
# 3️⃣ 통합 및 저장
# -----------------------------
if merged_df_list:
    merged_df = pd.concat(merged_df_list, ignore_index=True)
    merged_df.to_excel(output_file, index=False)
    print(f"💾 통합 완료: {output_file}")
else:
    raise ValueError("❌ 통합할 유효한 데이터가 없습니다.")
