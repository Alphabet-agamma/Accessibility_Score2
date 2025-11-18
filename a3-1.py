import pandas as pd
import re

pop = pd.read_excel("202510_202510_연령별인구현황_월간.xlsx")

def extract_gu(x):
    """ '서울특별시 종로구' → '종로구' """
    if pd.isna(x):
        return None
    x = str(x)
    m = re.search(r"서울특별시\s*([가-힣]+구)", x)
    if m:
        return m.group(1)
    return None

# 1) 구명 추출
pop["구"] = pop["행정기관"].apply(extract_gu)

# 2) 구(null) 제거
pop = pop[pop["구"].notna()].copy()

# 3) '총 인구수'에서 콤마 제거 + 숫자로 변환
pop["총 인구수"] = pop["총 인구수"].astype(str).str.replace(",", "")
pop["총 인구수"] = pd.to_numeric(pop["총 인구수"], errors="coerce").fillna(0).astype(int)

# 4) 구별 인구수 dict 생성
gu_population = pop.groupby("구")["총 인구수"].sum().to_dict()

print("\n===== 최종 구별 인구수 =====")
for gu, n in gu_population.items():
    print(gu, ":", n)
