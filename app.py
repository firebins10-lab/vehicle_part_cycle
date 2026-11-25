import streamlit as st
import streamlit.components.v1 as components

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
    {"name": "엔진오일/필터", "cycle": 10000 if fuel_type != "디젤" else 15000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드"]},
    {"name": "에어컨 필터", "cycle": 15000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"]},
    {"name": "타이어 위치교환", "cycle": 10000 if car_size == "소형" else 12000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"]},
    {"name": "브레이크 패드", "cycle": 35000 if fuel_type not in ["하이브리드", "전기"] else 60000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"]},
    {"name": "브레이크 오일", "cycle": 40000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"]},
    {"name": "연료 필터", "cycle": 30000 if fuel_type == "디젤" else 60000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드"]},
    {"name": "타이어 교체", "cycle": 50000 if car_size == "소형" else 60000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"]},
    {"name": "냉각수(부동액)", "cycle": 40000 if fuel_type != "전기" else 60000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"]},
    {"name": "감속기 오일", "cycle": 60000, "fuels": ["전기"]},
    {"name": "미션오일", "cycle": 80000, "fuels": ["휘발유", "디젤", "LPG", "하이브리드"]},
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

    # (6) 수직선(타임라인) 시각화 - SVG 벡터 그래픽으로 깨짐 없이 구현
    st.markdown("### 📏 소모품별 다음 교체 시기 수직선 (타임라인)")
    
    max_next_km = max(item["next_km"] for item in results)
    span_km = max(1, max_next_km - mileage)
    
    svg_width = 1000
    svg_height = 240
    start_x = 70
    end_x = 930
    line_y = 120
    
    # 라벨 높이 4단계로 분산하여 글자 겹침 완벽 방지
    label_y_levels = [35, 195, 70, 160]
    
    svg_items = ""
    for idx, item in enumerate(results):
        # 현재 주행거리부터 최대 교체 거리까지의 비율 위치 계산
        ratio = (item["next_km"] - mileage) / span_km
        x = start_x + ratio * (end_x - start_x)
        y_label = label_y_levels[idx % len(label_y_levels)]
        
        # 수직선에서 라벨까지 연결하는 세로 점선
        y_line_end = y_label + 15 if y_label < line_y else y_label - 22
        svg_items += f'<line x1="{x}" y1="{line_y}" x2="{x}" y2="{y_line_end}" stroke="#3182ce" stroke-width="1.5" stroke-dasharray="3,3" />'
        
        # 수직선 위의 파란색 포인트
        svg_items += f'<circle cx="{x}" cy="{line_y}" r="5" fill="#3182ce" />'
        
        # 소모품 이름 및 교체 시점 텍스트
        svg_items += f'''
        <text x="{x}" y="{y_label}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1a365d" text-anchor="middle">
            {item["name"]}
        </text>
        <text x="{x}" y="{y_label + 14}" font-family="sans-serif" font-size="11" fill="#4a5568" text-anchor="middle">
            ({item["next_km"]:,}km)
        </text>
        '''

    svg_html = f"""
    <div style="width: 100%; overflow-x: auto; background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; padding: 10px 0;">
        <svg width="100%" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" preserveAspectRatio="xMidYMid meet">
            <!-- 메인 수직선 (가로축) -->
            <line x1="{start_x}" y1="{line_y}" x2="{end_x}" y2="{line_y}" stroke="#cbd5e0" stroke-width="4" stroke-linecap="round" />
            
            <!-- 각 소모품 마커 및 라벨 -->
            {svg_items}
            
            <!-- 현재 주행거리 (빨간색 기준점) -->
            <circle cx="{start_x}" cy="{line_y}" r="8" fill="#e53e3e" />
            <text x="{start_x}" y="{line_y - 16}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#e53e3e" text-anchor="middle">현재 위치</text>
            <text x="{start_x}" y="{line_y + 24}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#e53e3e" text-anchor="middle">{mileage:,}km</text>
        </svg>
    </div>
    """
    components.html(svg_html, height=265)

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
