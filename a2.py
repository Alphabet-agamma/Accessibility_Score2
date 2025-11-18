import pandas as pd
import requests
import time
from tqdm import tqdm
import datetime
import numpy as np

GOOGLE_API_KEY = "AIzaSyAWMvmfquPx_IO6BTs4xiGRIqBmV3kxl5Y"

# ---------------------------------------
# 1. 구별 중심점
# ---------------------------------------
gu_centroids = {
    "Jongno-gu": (37.5731, 126.9794),
    "Jung-gu": (37.5610, 126.9997),
    "Yongsan-gu": (37.5323, 126.9908),
    "Seongdong-gu": (37.5634, 127.0364),
    "Gwangjin-gu": (37.5385, 127.0823),
    "Dongdaemun-gu": (37.5744, 127.0396),
    "Jungnang-gu": (37.6060, 127.0927),
    "Seongbuk-gu": (37.5894, 127.0167),
    "Gangbuk-gu": (37.6396, 127.0257),
    "Dobong-gu": (37.6688, 127.0471),
    "Nowon-gu": (37.6542, 127.0568),
    "Eunpyeong-gu": (37.6027, 126.9291),
    "Seodaemun-gu": (37.5791, 126.9368),
    "Mapo-gu": (37.5663, 126.9015),
    "Yangcheon-gu": (37.5170, 126.8665),
    "Gangseo-gu": (37.5607, 126.8220),
    "Guro-gu": (37.4953, 126.8877),
    "Geumcheon-gu": (37.4569, 126.8953),
    "Yeongdeungpo-gu": (37.5263, 126.8962),
    "Dongjak-gu": (37.5124, 126.9393),
    "Gwanak-gu": (37.4781, 126.9515),
    "Seocho-gu": (37.4836, 127.0327),
    "Gangnam-gu": (37.5172, 127.0473),
    "Songpa-gu": (37.5145, 127.1059),
    "Gangdong-gu": (37.5495, 127.1465)
}

# ---------------------------------------
# 2. 클러스터 데이터 로드
# ---------------------------------------
clusters = pd.read_excel("clusters_500m_2.xlsx")
clusters = clusters.dropna(subset=["centroid_lat", "centroid_lng"])

results = []

# ---------------------------------------
# 3. Transit API 호출 함수 (안전 버전)
# ---------------------------------------
def get_transit(orig_lat, orig_lng, dest_lat, dest_lng):

    # 내일 오후 2시
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    dt = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 14, 0, 0)
    timestamp = int(dt.timestamp())

    url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": f"{orig_lat},{orig_lng}",
        "destination": f"{dest_lat},{dest_lng}",
        "mode": "transit",
        "departure_time": timestamp,
        "language": "ko",
        "region": "KR",
        "key": GOOGLE_API_KEY,
    }

    try:
        r = requests.get(url, params=params, timeout=10).json()
    except:
        return None

    if r["status"] != "OK":
        return None

    try:
        leg = r["routes"][0]["legs"][0]
    except:
        return None

    total = leg["duration"]["value"] // 60
    T_walk, T_sub, T_bus = 0, 0, 0
    N_tr = 0

    for step in leg["steps"]:
        mode = step.get("travel_mode", None)

        if mode == "WALKING":
            T_walk += step["duration"]["value"] // 60

        elif mode == "TRANSIT":
            N_tr += 1
            dur = step["duration"]["value"] // 60

            transit_det = step.get("transit_details", {})
            line = transit_det.get("line", {})
            vehicle = line.get("vehicle", {})
            vtype = vehicle.get("type", None)

            if vtype == "SUBWAY":
                T_sub += dur
            elif vtype == "BUS":
                T_bus += dur

    N_tr = max(0, N_tr - 1)

    return total, T_walk, T_sub, T_bus, N_tr


# ---------------------------------------
# 4. 메인 루프 (군집 단위 계산)
# ---------------------------------------
total_clusters = len(clusters)
total_gus = len(gu_centroids)

print(f"총 예상 API 호출: {total_clusters * total_gus}")

for cidx, row in tqdm(clusters.iterrows(), total=total_clusters, desc="전체 군집 처리"):
    cluster_id = row["cluster_id"]
    lat_j = row["centroid_lat"]
    lng_j = row["centroid_lng"]

    for gu_idx, (gu, (lat_i, lng_i)) in tqdm(
        enumerate(gu_centroids.items()),
        total=len(gu_centroids),
        desc=f"{cidx+1}번째 군집",
        leave=False
    ):
        res = get_transit(lat_i, lng_i, lat_j, lng_j)

        if res is None:
            results.append([cluster_id, gu, np.nan, np.nan, np.nan, np.nan, np.nan])
            continue

        T_total, T_walk, T_sub, T_bus, N_tr = res

        results.append([
            cluster_id, gu, T_total, T_walk, T_sub, T_bus, N_tr
        ])

        time.sleep(0.1)

# ---------------------------------------
# 5. 저장
# ---------------------------------------
out = pd.DataFrame(results, columns=[
    "cluster_id", "gu", "T_total", "T_walk", "T_subway", "T_bus", "N_transfer"
])

out.to_excel("cluster_pathfind.xlsx", index=False)
print("🎉 완료: cluster_pathfind.xlsx 생성")
