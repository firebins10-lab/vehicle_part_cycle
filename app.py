import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="자동차 소모품 교체 주기 가이드", page_icon="🚗", layout="wide")

st.title("🚗 자동차 주행거리 기반 소모품 교체 주기 가이드")
st.markdown("차량 정보를 입력하면 **다음 교체까지 남은 주행거리와 예상 일수**를 계산하고 수직선으로 보여줍니다.")

# 1. 사이드바: 차량 정보 입력
st.sidebar.header("📋 차량 정보 입력")

# (1) 차종 선택
car_size = st.sidebar.selectbox("1. 차종 선택", ["소형", "대형"])

# (2) 연료 선택
fuel_type = st.sidebar.selectbox("2. 연료 선택", ["휘발유", "디젤", "LPG", "하이브리드", "전기"])

# (3) 차량 연식 슬라이더 (1960 이하 ~ 2026)
model_year = st.sidebar.slider(
    "3. 차량 연식 (1960 선택 시 1960년 이하로 간주)",
    min_value=1960,
    max_value=2026,
    value=2020,
    step=1
)

# (4) 현재 주행거리 입력
mileage = st.sidebar.number_input(
    "4. 현재 총 주행거리 (km)",
    min_value=0,
    max_value=2000000,
    value=45000,
    step=1000
)

# (5) 분석 버튼
analyze_btn = st.sidebar.button("🔍 소모품 교체 주기 분석하기", type="primary", use_container_width=True)

# --- 소모품 기준 데이터 (단위: km) ---
consumables_db = [
    {"name": "엔진오일 및 오일필터", "cycle": 10000 if fuel_type != "디젤" else 15000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드"]},
    {"name": "에어컨 필터", "cycle": 15000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"]},
    {"name": "타이어 위치교환", "cycle": 10000 if car_size == "소형" else 12000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"]},
    {"name": "브레이크 패드", "cycle": 35000 if fuel_type not in ["하이브리드", "전기"] else 60000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"]},
    {"name": "브레이크 오일", "cycle": 40000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"]},
    {"name": "연료 필터", "cycle": 30000 if fuel_type == "디젤" else 60000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드"]},
    {"name": "타이어 교체", "cycle": 50000 if car_size == "소형" else 60000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"]},
    {"name": "냉각수 (부동액)", "cycle": 40000 if fuel_type != "전기" else 60000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"]},
    {"name": "감속기 오일", "cycle": 60000, "fuels": ["전기"]},
    {"name": "미션오일 (변속기오일)", "cycle": 80000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드"]},
    {"name": "점화플러그", "cycle": 40000 if fuel_type == "LPG" else 80000, "fuels": ["휘발유", "LPG", "하이브리드"]},
]

if analyze_btn:
    current_year = 2026
    car_age = max(1, current_year - model_year)
    
    # 일평균 주행거리 계산 (주행거리가 0이면 평균 35km 적용)
    daily_km = (mileage / (car_age * 365)) if mileage > 0 else 35.0
    year_display = "1960년 이하" if model_year == 1960 else f"{model_year}년식"
    
    st.subheader(f"📊 분석 결과 ({year_display} | {car_size} | {fuel_type} | 누적 {mileage:,} km)")
    st.info(f"💡 일평균 주행거리는 약 **{daily_km:.1f} km/일**로 추산되며, 이를 기준으로 남은 일수를 계산했습니다.")

    # 해당 연료의 소모품 계산 및 정렬
    results = []
    for item in consumables_db:
        if fuel_type in item["fuels"]:
            cycle = item["cycle"]
            next_km = ((mileage // cycle) + 1) * cycle
            rem_km = next_km - mileage
            rem_days = int(rem_km / daily_km) if daily_km > 0 else 0
            
            results.append({
                "name": item["name"],
                "cycle": cycle,
                "next_km": next_km,
                "rem_km": rem_km,
                "rem_days": rem_days
            })
            
    # 남은 주행거리가 짧은 순서로 정렬
    results.sort(key=lambda x: x["rem_km"])

    # (6) 수직선(타임라인) 시각화 - 별도 라이브러리 없이 순수 HTML/CSS로 구현
    st.markdown("### 📏 소모품별 다음 교체 시기 수직선 (타임라인)")
    
    max_next_km = max(item["next_km"] for item in results)
    span_km = max(1, max_next_km - mileage)
    
    # 수직선 상에 마커 생성
    markers_html = ""
    for idx, item in enumerate(results):
        # 현재 위치(0%)부터 가장 먼 교체 시점(95%) 사이의 위치 비율 계산
        pct = ((item["next_km"] - mileage) / span_km) * 90 + 5
        # 글자 겹침 방지를 위해 위/아래 번갈아 배치
        is_top = (idx % 2 == 0)
        top_pos = "5px" if is_top else "85px"
        line_top = "45px" if is_top else "65px"
        
        markers_html += f"""
        <div style="position: absolute; left: {pct}%; top: {line_top}; width: 2px; height: 20px; background-color: #2b6cb0; transform: translateX(-50%);"></div>
        <div style="position: absolute; left: {pct}%; top: {top_pos}; transform: translateX(-50%); text-align: center; font-size: 12px; white-space: nowrap; background: #ebf8ff; padding: 3px 6px; border-radius: 4px; border: 1px solid #90cdf4; color: #1a365d;">
            <b>{item['name']}</b><br>{item['next_km']:,}km
        </div>
        """

    timeline_html = f"""
    <div style="position: relative; width: 100%; height: 140px; margin: 20px 0; padding: 0 20px; box-sizing: border-box; overflow-x: auto;">
        <div style="min-width: 750px; position: relative; height: 100%;">
            <!-- 가로 수직선 -->
            <div style="position: absolute; top: 65px; left: 0; right: 0; height: 4px; background-color: #cbd5e0; border-radius: 2px;"></div>
            <!-- 현재 위치 (빨간색 점) -->
            <div style="position: absolute; left: 0%; top: 58px; width: 18px; height: 18px; background-color: #e53e3e; border-radius: 50%; transform: translateX(-50%); z-index: 2;"></div>
            <div style="position: absolute; left: 0%; top: 82px; font-size: 12px; font-weight: bold; color: #e53e3e; white-space: nowrap;">
                현재 ({mileage:,}km)
            </div>
            {markers_html}
        </div>
    </div>
    """
    st.markdown(timeline_html, unsafe_allow_html=True)

    # (5) 텍스트 메시지로 소모품별 남은 주행거리 및 남은 일수 출력
    st.markdown("### 📝 소모품별 상세 교체 가이드 (임박한 순서)")
    
    for item in results:
        msg = (
            f"**[{item['name']}]** (기본 주기: {item['cycle']:,} km) ➔ 다음 교체 시점 **{item['next_km']:,} km**까지 "
            f"**{item['rem_km']:,} km** 남았습니다. (현재 주행 패턴 기준 **약 {item['rem_days']:,}일** 후 교체 권장)"
        )
        
        if item["rem_km"] <= 2000:
            st.error(f"🚨 **[교체 임박]** {msg}")
        elif item["rem_km"] <= 5000:
            st.warning(f"⚠️ **[점검 권장]** {msg}")
        else:
            st.success(f"✅ **[여유 있음]** {msg}")

else:
    st.info("👈 왼쪽 사이드바에서 차량 정보를 입력한 뒤 **'소모품 교체 주기 분석하기'** 버튼을 눌러주세요.")
