import pandas as pd
import folium
from matplotlib import cm
import numpy as np

# ---------------------------------------
# 1. 입력 파일 로드
# ---------------------------------------
df = pd.read_excel("merged_with_clusters_500m.xlsx")
clusters = pd.read_excel("clusters_500m.xlsx")

print("📂 데이터 로드 완료")
print(df.head())
print(clusters.head())


# ---------------------------------------
# 2. 지도 객체 생성 (서울 중심으로)
# ---------------------------------------
m = folium.Map(location=[37.55, 126.98], zoom_start=11)


# ---------------------------------------
# 3. 색상 매핑 (cluster_id → 색)
# ---------------------------------------
num_clusters = len(clusters)
color_map = cm.tab20(np.linspace(0, 1, num_clusters))

def color_hex(i):
    r, g, b, _ = color_map[i % len(color_map)]
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


# ---------------------------------------
# 4. 클러스터 중심점 표시
# ---------------------------------------
for _, row in clusters.iterrows():
    cid = int(row["cluster_id"])
    lat = row["centroid_lat"]
    lng = row["centroid_lng"]
    count = row["place_count"]
    
    folium.CircleMarker(
        location=[lat, lng],
        radius=10,
        color=color_hex(cid),
        fill=True,
        fill_opacity=0.9,
        popup=folium.Popup(
            f"<b>Cluster {cid}</b><br>"
            f"Places: {count}",
            max_width=250
        )
    ).add_to(m)


# ---------------------------------------
# 5. 개별 장소도 지도에 표시
# ---------------------------------------
for _, row in df.iterrows():
    cid = int(row["cluster_id"])
    pname = row["place_name"]
    lat = row["latitude"]
    lng = row["longitude"]
    
    folium.CircleMarker(
        location=[lat, lng],
        radius=4,
        color=color_hex(cid),
        fill=True,
        fill_opacity=0.7,
        popup=folium.Popup(
            f"{pname}<br>Cluster {cid}",
            max_width=250
        )
    ).add_to(m)


# ---------------------------------------
# 6. 지도 저장
# ---------------------------------------
output = "clusters_500m_map.html"
m.save(output)
print(f"🎉 군집 시각화 지도 생성 완료 → {output}")
