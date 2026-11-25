from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="자동차 소모품 교체 주기 가이드", page_icon="🚗", layout="wide"
)

st.title("🚗 자동차 주행거리 기반 소모품 교체 주기 가이드")
st.markdown(
    "차량 정보를 입력하면 **다음 교체까지 남은 주행거리와 예상 일수**를 계산하고 타임라인으로 보여줍니다."
)

# 1. 사이드바: 차량 정보 입력
st.sidebar.header("📋 차량 정보 입력")

# (1) 차종 선택
car_size = st.sidebar.selectbox("1. 차종 선택", ["소형", "대형"])

# (2) 연료 선택
fuel_type = st.sidebar.selectbox(
    "2. 연료 선택", ["휘발유", "디젤", "LPG", "하이브리드", "전기"]
)

# (3) 차량 연식 슬라이더 (1960 이하 ~ 2026)
model_year = st.sidebar.slider(
    "3. 차량 연식 (1960 선택 시 1960년 이하로 간주)",
    min_value=1960,
    max_value=2026,
    value=2020,
    step=1,
)

# (4) 현재 주행거리 입력
mileage = st.sidebar.number_input(
    "4. 현재 총 주행거리 (km)",
    min_value=0,
    max_value=2000000,
    value=45000,
    step=1000,
)

# (5) 분석 버튼
analyze_btn = st.sidebar.button(
    "🔍 소모품 교체 주기 분석하기", type="primary", use_container_width=True
)

# --- 소모품 데이터 및 계산 로직 ---
# 기본 교체 주기 설정 (단위: km)
# 연료별/차종별 특성을 반영하기 위한 기준 데이터
consumables_db = [
    {
        "name": "엔진오일 및 오일필터",
        "cycle": 10000 if fuel_type != "디젤" else 15000,
        "fuels": ["휘발유", "디젤", "LPG", "하이브리드"],
    },
    {
        "name": "에어컨 필터",
        "cycle": 15000,
        "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"],
    },
    {
        "name": "브레이크 오일",
        "cycle": 40000,
        "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"],
    },
    {
        "name": "타이어 위치교환",
        "cycle": 10000 if car_size == "소형" else 12000,
        "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"],
    },
    {
        "name": "타이어 교체",
        "cycle": 50000 if car_size == "소형" else 60000,
        "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"],
    },
    {
        "name": "브레이크 패드",
        "cycle": 35000 if fuel_type not in ["하이브리드", "전기"] else 60000,
        "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"],
    },
    {
        "name": "연료 필터",
        "cycle": 30000 if fuel_type == "디젤" else 60000,
        "fuels": ["휘발유", "디젤", "LPG", "하이브리드"],
    },
    {
        "name": "미션오일 (변속기오일)",
        "cycle": 80000,
        "fuels": ["휘발유", "디젤", "LPG", "하이브리드"],
    },
    {
        "name": "감속기 오일",
        "cycle": 60000,
        "fuels": ["전기"],
    },
    {
        "name": "냉각수 (부동액)",
        "cycle": 40000 if fuel_type != "전기" else 60000,
        "fuels": ["휘발유", "디젤", "LPG", "하이브리드", "전기"],
    },
    {
        "name": "점화플러그",
        "cycle": 40000 if fuel_type == "LPG" else 80000,
        "fuels": ["휘발유", "LPG", "하이브리드"],
    },
]

if analyze_btn:
    current_year = 2026
    # 연식 기반 운행 연수 계산 (최소 1년으로 보정하여 0으로 나누기 방지)
    car_age = max(1, current_year - model_year)

    # 일평균 주행거리 계산 (주행거리가 0이면 국내 평균치인 약 35km/일 적용)
    if mileage > 0:
        daily_km = mileage / (car_age * 365)
    else:
        daily_km = 35.0

    # 연식 표시 텍스트 처리
    year_display = "1960년 이하" if model_year == 1960 else f"{model_year}년식"

    st.subheader(
        f"📊 분석 결과 ({year_display} | {car_size} | {fuel_type} | 누적 {mileage:,} km)"
    )
    st.info(
        f"💡 차량 연식과 누적 주행거리를 바탕으로 추산한 일평균 주행거리는 약 **{daily_km:.1f} km/일**입니다. (이를 기준으로 남은 일수를 계산합니다)"
    )

    # 선택된 연료에 해당하는 소모품만 필터링 및 계산
    results = []
    for item in consumables_db:
        if fuel_type in item["fuels"]:
            cycle = item["cycle"]
            # 다음 교체 주행거리 계산
            next_replace_km = ((mileage // cycle) + 1) * cycle
            rem_km = next_replace_km - mileage
            rem_days = int(rem_km / daily_km) if daily_km > 0 else 0

            results.append({
                "소모품": item["name"],
                "기본주기(km)": cycle,
                "다음교체시점(km)": next_replace_km,
                "남은주행거리(km)": rem_km,
                "예상남은일수(일)": rem_days,
            })

    df_res = pd.DataFrame(results).sort_values(by="남은주행거리(km)")

    # (6) 수직선(타임라인) 시각화 - Plotly 활용
    st.markdown("### 📏 소모품별 다음 교체 시기 수직선 (타임라인)")

    fig = go.Figure()

    # 수직선 베이스라인 그리기
    max_target_km = df_res["다음교체시점(km)"].max()
    fig.add_shape(
        type="line",
        x0=mileage,
        y0=0.5,
        x1=max_target_km + 5000,
        y1=0.5,
        line=dict(color="gray", width=3),
    )

    # 현재 주행거리 마커 표시
    fig.add_trace(
        go.Scatter(
            x=[mileage],
            y=[0.5],
            mode="markers+text",
            marker=dict(size=16, color="red", symbol="diamond"),
            text=[f"<b>현재 위치</b><br>{mileage:,} km"],
            textposition="bottom center",
            name="현재 주행거리",
            hoverinfo="text",
        )
    )

    # 각 소모품 교체 시점 마커 표시 (라벨 겹침 방지를 위해 위/아래 높이 교차 배치)
    y_positions = [0.65, 0.35, 0.8, 0.2, 0.95, 0.05]

    for idx, row in enumerate(df_res.itertuples()):
        y_pos = y_positions[idx % len(y_positions)]
        target_km = row._3  # 다음교체시점(km)

        # 수직선에서 각 라벨까지 이어지는 점선
        fig.add_shape(
            type="line",
            x0=target_km,
            y0=0.5,
            x1=target_km,
            y1=y_pos,
            line=dict(color="royalblue", width=1, dash="dot"),
        )

        # 소모품 포인트 및 텍스트
        fig.add_trace(
            go.Scatter(
                x=[target_km],
                y=[y_pos],
                mode="markers+text",
                marker=dict(size=11, color="royalblue"),
                text=[f"<b>{row.소모품}</b><br>({target_km:,} km)"],
                textposition="top center" if y_pos > 0.5 else "bottom center",
                name=row.소모품,
                hovertemplate=(
                    f"<b>{row.소모품}</b><br>"
                    f"교체 예정: {target_km:,} km<br>"
                    f"남은 거리: {row._4:,} km<br>"
                    f"예상 남은 일수: 약 {row._5:,}일<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        height=420,
        showlegend=False,
        xaxis=dict(
            title="누적 주행거리 (km)",
            tickformat=",",
            range=[max(0, mileage - 3000), max_target_km + 8000],
            showgrid=True,
            gridcolor="lightgray",
        ),
        yaxis=dict(range=[-0.15, 1.15], visible=False),
        margin=dict(l=20, r=20, t=30, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)

    # (5) 텍스트 메시지로 소모품별 남은 주행거리 및 남은 일수 출력
    st.markdown("### 📝 소모품별 상세 교체 가이드 (임박한 순서)")

    for row in df_res.itertuples():
        name = row.소모품
        cycle = row._2
        next_km = row._3
        rem_km = row._4
        rem_days = row._5

        msg = (
            f"**[{name}]** (기본 주기: {cycle:,} km) ➔ 다음 교체 시점 **{next_km:,} km**까지 "
            f"**{rem_km:,} km** 남았습니다. (현재 주행 패턴 기준 **약 {rem_days:,}일** 후 교체 권장)"
        )

        # 남은 거리에 따라 알림 색상 다르게 표시
        if rem_km <= 2000:
            st.error(f"🚨 **[교체 임박]** {msg}")
        elif rem_km <= 5000:
            st.warning(f"⚠️ **[점검 권장]** {msg}")
        else:
            st.success(f"✅ **[여유 있음]** {msg}")

else:
    st.info(
        "👈 왼쪽 사이드바에서 차량 정보를 입력한 뒤 **'소모품 교체 주기 분석하기'** 버튼을 눌러주세요."
    )
