import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist

# -----------------------------
# ⚙️ 설정
# -----------------------------
input_file = "merged_with_kakao_latlon_filled_google.xlsx"  # 위경도 포함된 파일
output_dist_file = "matrix.npy"  # 군집 코드에서 불러올 파일명

# -----------------------------
# 1️⃣ 데이터 불러오기
# -----------------------------
data = pd.read_excel(input_file)
data = data.dropna(subset=["latitude", "longitude"])
coords = data[["latitude", "longitude"]].to_numpy()
print(f"✅ 데이터 로드 완료: {data.shape}")

# -----------------------------
# 2️⃣ Haversine 거리 계산 함수
# -----------------------------
def haversine_pdist(coords):
    """
    위도/경도 좌표 배열을 받아
    각 점 사이의 Haversine 거리(미터 단위)를 반환
    """
    R = 6371000  # 지구 반지름 (m)
    coords_rad = np.radians(coords)

    def pairwise(u, v):
        dlat = v[0] - u[0]
        dlon = v[1] - u[1]
        a = np.sin(dlat / 2) ** 2 + np.cos(u[0]) * np.cos(v[0]) * np.sin(dlon / 2) ** 2
        return 2 * R * np.arcsin(np.sqrt(a))

    return pdist(coords_rad, metric=pairwise)

# -----------------------------
# 3️⃣ 거리 행렬 계산
# -----------------------------
print("📏 거리 행렬 계산 중...")
dist_matrix = haversine_pdist(coords)

# -----------------------------
# 4️⃣ 저장
# -----------------------------
np.save(output_dist_file, dist_matrix)
print(f"💾 거리 행렬 저장 완료: {output_dist_file}")
print(f"➡️ 총 거리 원소 개수: {len(dist_matrix)}")
