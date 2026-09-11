import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import pickle
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Kalahari Manganese AI Center",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. HIGH-IMPACT ADVANCED CSS ---
st.markdown("""
    <style>
    /* Dark Command Center Background */
    .stApp {
        background: linear-gradient(135deg, #0b0e14 0%, #121824 100%);
        color: #e0e6ed;
    }
    
    /* Team Note */
    .team-note {
        font-size: 1.1rem;
        color: #00e676;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: -10px;
    }

/* Modern Header Banners */
    .main-title {
        font-size: 4.8rem; /* Massively increased size */
        font-weight: 900; /* Maximum boldness */
        background: linear-gradient(90deg, #00e676, #00b0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        line-height: 1.1;
    }

    .sub-title {
        color: #8b9bb4;
        font-size: 1.1rem;
        margin-top: 5px;
        margin-bottom: 25px;
    }

    /* Glassmorphism KPI Cards */
    div[data-testid="stMetric"] {
        background: rgba(20, 27, 41, 0.7);
        border: 1px solid rgba(0, 230, 118, 0.2);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        transition: transform 0.2s ease-in-out;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: rgba(0, 230, 118, 0.6);
        transform: translateY(-2px);
    }

    div[data-testid="stMetricValue"] {
        color: #00e676 !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
    }

    div[data-testid="stMetricLabel"] {
        color: #90a4ae !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* Tab Navigation Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        color: #b0bec5;
        font-weight: 600;
        padding: 0px 20px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00b0ff, #00e676) !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border: none !important;
    }

    /* Custom Button Styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #00e676, #00b0ff);
        color: #000000;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 15px rgba(0, 230, 118, 0.5);
        color: #000000;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DASHBOARD HEADER ---
st.markdown('<p class="team-note">🚀 Developed by Team: THE ARCHONS</p>', unsafe_allow_html=True)
st.markdown('<p class="main-title">⚡ KALAHARI MANGANESE AI OPERATIONS</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Hotazel Mine Exploration & Real-Time Production Shortfall Intelligence</p>', unsafe_allow_html=True)

# --- 4. DATA & MODEL LOADERS ---
@st.cache_resource
def load_models():
    reserve_model, shortfall_model = None, None
    if os.path.exists("models/reserve_model.pkl"):
        reserve_model = pickle.load(open("models/reserve_model.pkl", "rb"))
    if os.path.exists("models/shortfall_model.pkl"):
        shortfall_model = pickle.load(open("models/shortfall_model.pkl", "rb"))
    return reserve_model, shortfall_model

rf_reserve, rf_shortfall = load_models()

def load_data(query):
    db_path = "database/mine_data.db" if os.path.exists("database/mine_data.db") else "mine_data.db"
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df_reserves = load_data("SELECT * FROM reserves")
df_production = load_data("SELECT * FROM daily_production")

# --- 5. TOP METRICS PANEL ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Extracted Tonnage", f"{df_production['actual_tonnage'].sum():,.0f} T")
with col2:
    st.metric("Avg Rainfall", f"{df_production['rainfall_mm'].mean():.1f} mm")
with col3:
    st.metric("Avg Machine Downtime", f"{df_production['equipment_downtime_hours'].mean():.1f} hrs")
with col4:
    st.metric("Peak Prospect Grade", f"{df_reserves['manganese_grade_percent'].max():.1f}% Mn")

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. DASHBOARD TABS ---
tab1, tab2, tab3 = st.tabs(["🗺️ Geospatial Reserve Map", "📊 Shortfall Predictor", "🤖 AI Action Center"])

# TAB 1: GEOSPATIAL MAP (High-Res Satellite View)
with tab1:
    st.subheader("Borehole Target Classification")
    map_col, data_col = st.columns([2.2, 1])
    
    with map_col:
        # High-Resolution Satellite Base Map
        m = folium.Map(
            location=[-27.20, 22.95], 
            zoom_start=13, 
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri World Imagery'
        )
        
        for _, row in df_reserves.iterrows():
            color = "#00e676" if row['target_label'] == 1 else "#ff1744"
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=9, 
                popup=f"Grade: {row['manganese_grade_percent']}% Mn",
                color=color, 
                fill=True, 
                fill_color=color,
                fill_opacity=0.9
            ).add_to(m)
        st_folium(m, width=800, height=450)
        
    with data_col:
        st.markdown("**Deposit Classification:**")
        st.markdown("🟢 **High-Grade Deposit** (Viable Target)")
        st.markdown("🔴 **Low-Grade Waste** (Non-Viable Target)")
        st.divider()
        st.dataframe(
            df_reserves[['borehole_id', 'depth_meters', 'manganese_grade_percent']], 
            hide_index=True,
            use_container_width=True
        )
# TAB 2: SHORTFALL AI PREDICTOR
with tab2:
    st.subheader("Live Operational Shortfall Forecasting")
    
    fig = px.line(
        df_production, x='date', y=['planned_tonnage', 'actual_tonnage'], 
        title="Historical Tonnage Performance (Planned vs Actual)", 
        markers=True,
        template="plotly_dark",
        color_discrete_sequence=["#00b0ff", "#00e676"]
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#b0bec5")
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔮 Operational Risk Simulator")
    pred_col1, pred_col2, pred_col3 = st.columns(3)
    with pred_col1:
        sim_rain = st.number_input("Forecasted Rainfall (mm)", min_value=0.0, value=25.0)
    with pred_col2:
        sim_down = st.number_input("Forecasted Downtime (hours)", min_value=0.0, value=4.0)
    with pred_col3:
        st.write("")
        st.write("")
        if st.button("Calculate Output Shortfall"):
            if rf_shortfall:
                prediction = rf_shortfall.predict([[sim_rain, sim_down]])[0]
                if prediction > 15:
                    st.error(f"⚠️ HIGH RISK DETECTED: Predicted Shortfall of {prediction:.2f}%")
                else:
                    st.success(f"✅ NORMAL OPERATIONS: Predicted Shortfall of {prediction:.2f}%")
            else:
                st.warning("Model missing. Ensure train_shortfall_model.py was executed.")

# TAB 3: ACTION CENTER
with tab3:
    st.subheader("Automated Operational Prescriptions")
    st.info("Trigger Rule: Weather alert (> 20mm rainfall) or predicted shortfall > 15%")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.checkbox("Reroute heavy haul trucks to paved Sector B road"):
            st.success("Dispatched to Fleet Management Network")
    with col_b:
        if st.checkbox("Increase primary crushing plant feed rate by 15%"):
            st.success("Plant Operations Notified")