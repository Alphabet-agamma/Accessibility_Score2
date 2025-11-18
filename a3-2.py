import pandas as pd
import numpy as np
import re

# =====================================================
# 1. 데이터 로드
# =====================================================
places = pd.read_excel("merged_clean.xlsx")
travel = pd.read_excel("google_travel_long.xlsx")
prox = pd.read_excel("tour_proximity_result.xlsx")
pop = pd.read_excel("202510_202510_연령별인구현황_월간.xlsx")

places["place_id"] = places.index

print("=== [STEP 1] 데이터 로드 완료 ===")
print("places.shape:", places.shape)
print("travel.shape:", travel.shape)
print("prox.shape:", prox.shape)
print("pop.shape:", pop.shape)


# =====================================================
# 2. POP 정제 (구별 인구수)
# =====================================================
def extract_gu(x):
    """'서울특별시 종로구' → '종로구' 형태로 구명 추출"""
    if pd.isna(x):
        return None
    x = str(x)
    # 공백 제거 후 패턴 검색: '서울특별시종로구' 같은 것도 잡힘
    m = re.search(r"서울특별시\s*([가-힣]+구)", x.replace(" ", ""))
    if m:
        return m.group(1)
    return None

# 구명 추출
pop["구"] = pop["행정기관"].apply(extract_gu)
pop = pop[pop["구"].notna()]

# 콤마 제거 후 숫자 변환
pop["총 인구수"] = (
    pop["총 인구수"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .astype(float)
)

# 구별 인구 dict
gu_population = pop.groupby("구")["총 인구수"].sum().to_dict()

print("\n=== [STEP 2] POP 정제 결과 ===")
print("pop['구'].unique():", pop["구"].unique())
print("구 개수:", len(gu_population))
print("샘플 구별 인구수 (앞 10개):")
for gu, val in list(gu_population.items())[:10]:
    print(f"  {gu}: {val}")


# =====================================================
# 3. PROX 기반 TSP_j 계산
# =====================================================
prox_merged = places.merge(
    prox[["TourSpot", "SubwayStations_500m", "BusStops_500m"]],
    left_on="place_name",
    right_on="TourSpot",
    how="left"
)

print("\n=== [STEP 3-1] PROX 매칭 결과 ===")
print(prox_merged[["place_name", "SubwayStations_500m", "BusStops_500m"]].head())
print("SubwayStations_500m unique:", prox_merged["SubwayStations_500m"].unique())
print("BusStops_500m unique:", prox_merged["BusStops_500m"].unique())

def compute_tsp(row):
    sub = row["SubwayStations_500m"] if not pd.isna(row["SubwayStations_500m"]) else 0
    bus = row["BusStops_500m"]       if not pd.isna(row["BusStops_500m"])       else 0
    epsilon = 1   # 기본 접근성
    return np.log1p(sub)*4 + np.log1p(bus) + epsilon

prox_merged["TSP_j"] = prox_merged.apply(compute_tsp, axis=1)
TSP_map = prox_merged.set_index("place_id")["TSP_j"].to_dict()

print("\n=== [STEP 3-2] TSP_j 계산 결과 ===")
print(prox_merged[["place_name", "TSP_j"]].head())
print("TSP_j 통계:")
print(prox_merged["TSP_j"].describe())


# =====================================================
# 4. TRAVEL 기반 generalized cost C_ij
# =====================================================
travel = travel.merge(
    places[["place_name", "place_id"]],
    on="place_name",
    how="left"
)

before_dropna = travel.shape[0]
travel = travel.dropna(subset=["place_id"])
after_dropna = travel.shape[0]
travel["place_id"] = travel["place_id"].astype(int)

print("\n=== [STEP 4-1] TRAVEL-PLACES 매칭 결과 ===")
print(f"place_id NaN 제거 전: {before_dropna}행, 제거 후: {after_dropna}행")
print(travel[["place_name", "gu", "place_id"]].head())

alpha = 2
beta = 8
gamma_bus = 1.2
gamma_sub = 1.0

travel["C_ij"] = (
    gamma_sub * travel["T_subway"] +
    gamma_bus * travel["T_bus"] +
    alpha * travel["T_walk"] +
    beta * travel["N_transfer"]
)

print("\n=== [STEP 4-2] C_ij 계산 결과 ===")
print(travel[["place_name", "gu", "T_subway", "T_bus", "T_walk", "N_transfer", "C_ij"]].head())
print("C_ij 통계:")
print(travel["C_ij"].describe())


# 영어 구명 → 한국어 구명
eng_to_kor = {
    "Jongno-gu":"종로구","Jung-gu":"중구","Yongsan-gu":"용산구","Seongdong-gu":"성동구",
    "Gwangjin-gu":"광진구","Dongdaemun-gu":"동대문구","Jungnang-gu":"중랑구",
    "Seongbuk-gu":"성북구","Gangbuk-gu":"강북구","Dobong-gu":"도봉구","Nowon-gu":"노원구",
    "Eunpyeong-gu":"은평구","Seodaemun-gu":"서대문구","Mapo-gu":"마포구","Yangcheon-gu":"양천구",
    "Gangseo-gu":"강서구","Guro-gu":"구로구","Geumcheon-gu":"금천구","Yeongdeungpo-gu":"영등포구",
    "Dongjak-gu":"동작구","Gwanak-gu":"관악구","Seocho-gu":"서초구","Gangnam-gu":"강남구",
    "Songpa-gu":"송파구","Gangdong-gu":"강동구"
}

travel["gu_kor"] = travel["gu"].map(eng_to_kor)
travel["P_i"] = travel["gu_kor"].map(gu_population)

print("\n=== [STEP 4-3] P_i 매핑 결과 ===")
print(travel[["place_name", "gu", "gu_kor", "P_i"]].head(15))
print("P_i unique (앞 20개):", np.unique(travel["P_i"])[:20])


# =====================================================
# 5. 경쟁효과 D_j = Σ(P_i / C_ij)
# =====================================================
travel_valid = travel[travel["C_ij"] > 0]

print("\n=== [STEP 5-1] travel_valid 크기 ===")
print("travel_valid.shape:", travel_valid.shape)

D = travel_valid.groupby("place_id").apply(
    lambda df: np.sum(df["P_i"] / df["C_ij"])
).to_dict()

print("\n=== [STEP 5-2] D_j 값 샘플 ===")
for pid, val in list(D.items())[:10]:
    pname = places.loc[pid, "place_name"] if pid in places.index else "UNKNOWN"
    print(f"place_id={pid}, place_name={pname}, D_j={val}")


# =====================================================
# 6. 최종 접근성 Acc_j = TSP_j × D_j
# =====================================================
Acc = {}
for pid in places["place_id"]:
    Acc[pid] = TSP_map.get(pid, 0) * D.get(pid, 0)

print("\n=== [STEP 6] Acc_j 샘플 ===")
for pid in list(places["place_id"])[:10]:
    pname = places.loc[pid, "place_name"]
    print(f"place_id={pid}, place_name={pname}, "
          f"TSP_j={TSP_map.get(pid, 0)}, D_j={D.get(pid, 0)}, Acc={Acc[pid]}")


# =====================================================
# 7. merged_clean.xlsx 에 접근성 붙여서 저장
# =====================================================
places["accessibility_raw"] = places["place_id"].map(Acc)

places.to_excel("merged_clean_with_accessibility.xlsx", index=False)

print("\n🎉 최종 접근성 지표까지 계산 완료!")
print("👉 merged_clean_with_accessibility.xlsx 파일 생성됨")
