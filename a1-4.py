import pandas as pd
import numpy as np

# -----------------------
# Haversine 거리 계산
# -----------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # km
    
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a)) * 1000   # meters

# ===============================
# 1. 데이터 로드
# ===============================
df = pd.read_excel("merged_clean.xlsx")
df = df.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)

used = set()     # 군집 확정된 index
clusters = []     # 최종 군집 리스트
cluster_id = 0

# ===============================
# 2. 군집 생성 시작
# ===============================
for i in range(len(df)):
    if i in used:
        continue
    
    # 새 cluster 시작
    cluster_indices = [i]
    used.add(i)
    
    # 초기 centroid = 자기 자신
    centroid_lat = df.loc[i, "latitude"]
    centroid_lng = df.loc[i, "longitude"]
    
    changed = True
    while changed:
        changed = False
        # centroid로부터 500m 이내 점 찾기
        for j in range(len(df)):
            if j in used:
                continue
            d = haversine(centroid_lat, centroid_lng,
                          df.loc[j, "latitude"], df.loc[j, "longitude"])
            if d <= 500:      # 500m 내라면 cluster에 추가
                cluster_indices.append(j)
                used.add(j)
                changed = True
        
        # cluster 멤버 기반으로 centroid 재계산
        centroid_lat = df.loc[cluster_indices, "latitude"].mean()
        centroid_lng = df.loc[cluster_indices, "longitude"].mean()
    
    # 최종 cluster 저장
    clusters.append({
        "cluster_id": cluster_id,
        "centroid_lat": centroid_lat,
        "centroid_lng": centroid_lng,
        "place_count": len(cluster_indices),
        "place_names": df.loc[cluster_indices, "place_name"].tolist()
    })
    
    df.loc[cluster_indices, "cluster_id"] = cluster_id
    cluster_id += 1

# ===============================
# 3. 결과 저장
# ===============================
df.to_excel("merged_with_clusters_500m.xlsx", index=False)

clusters_df = pd.DataFrame(clusters)
clusters_df.to_excel("clusters_500m.xlsx", index=False)

print("🎉 500m 군집 생성 완료 → clusters_500m.xlsx 생성")
