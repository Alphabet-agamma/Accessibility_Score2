import pandas as pd
import glob
import os
from tqdm import tqdm

# ===============================
# ⚙️ 설정
# ===============================
folder_path = r"C:\\Users\\nangg\\문서\\TEST\\result_seoul_with_dong"  # 엑셀 파일들이 들어있는 폴더
output_file = "merged_raw.xlsx"

# ===============================
# 🧩 1️⃣ 엑셀 파일 불러오기 및 통합
# ===============================
all_files = glob.glob(os.path.join(folder_path, "*.xlsx"))
# 🔥 임시(~$) 파일 제외
all_files = [f for f in all_files if not os.path.basename(f).startswith("~$")]

merged_df = pd.DataFrame()

for file in tqdm(all_files, desc="파일 통합 중"):
    base_name = os.path.basename(file)
    category = base_name.split("_")[0]  # 파일 이름에서 category 추출

    df = pd.read_excel(file, engine="openpyxl")

    # 컬럼명 통일
    df.columns = [c.lower().strip() for c in df.columns]
    rename_map = {}
    for col in df.columns:
        if col in ["place_name", "명칭"]:
            rename_map[col] = "place_name"
        elif col in ["address", "주소"]:
            rename_map[col] = "address"
    df = df.rename(columns=rename_map)

    # 필요한 컬럼만 남기기
    keep_cols = ["place_name", "address"]
    df = df[[c for c in keep_cols if c in df.columns]]

    df["category"] = category
    merged_df = pd.concat([merged_df, df], ignore_index=True)

print(f"✅ 파일 통합 완료: {merged_df.shape[0]}개 행")

# 저장
merged_df.to_excel(output_file, index=False)
print(f"💾 통합 결과 저장 완료: {output_file}")
