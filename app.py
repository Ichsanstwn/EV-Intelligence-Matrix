import re
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Sistem Pendukung Keputusan Pemilihan Mobil Listrik | AHP-TOPSIS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def clean_html(html_str: str) -> str:
    # Minifies HTML/CSS by stripping newlines and multiple spaces to prevent Streamlit Markdown parser issues
    cleaned = html_str.replace("\n", " ")
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned

# Custom CSS Injections (Bright dashboard theme with soft glow accents)
st.markdown(
    clean_html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Orbitron:wght@600;700;800;900&display=swap');
    
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Light app background */
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 18% 8%, rgba(0, 119, 182, 0.15), transparent 28%),
            radial-gradient(circle at 82% 16%, rgba(245, 158, 11, 0.12), transparent 24%),
            radial-gradient(circle at 58% 92%, rgba(47, 128, 237, 0.11), transparent 30%),
            linear-gradient(180deg, #F8FBFF 0%, #EEF5FF 100%) !important;
        background-size: 100% 100%;
        color: #243044 !important;
        position: relative;
    }

    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        opacity: 0.42;
        background:
            radial-gradient(circle at center, rgba(0, 90, 156, 0.20) 0 1px, transparent 1.5px);
        background-size: 28px 28px;
        mask-image: linear-gradient(180deg, rgba(0,0,0,0.42), rgba(0,0,0,0.16) 62%, transparent);
    }

    [data-testid="stAppViewContainer"]::after {
        content: none;
        position: fixed;
    }

    [data-testid="stAppViewContainer"] > .main {
        position: relative;
        z-index: 1;
    }

    
    /* Global Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', sans-serif !important;
        color: #102A43 !important;
        letter-spacing: 0.5px;
    }
    
    :root {
        --ugm-blue: #003D7C;
        --ugm-gold: #F5A623;
        --ugm-light: #E8F0FA;
        --cyber-cyan: #0077B6;
        --cyber-blue: #2F80ED;
        --cyber-orange: #F59E0B;
        --glow-blue: rgba(0, 119, 182, 0.28);
        --glow-gold: rgba(245, 158, 11, 0.32);
        --glow-green: rgba(16, 185, 129, 0.24);
    }
    
    .main-header {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(226, 244, 255, 0.94) 58%, rgba(255, 248, 225, 0.86) 100%);
        border: 1px solid rgba(0, 119, 182, 0.20);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: #102A43;
        box-shadow: 0 12px 34px rgba(15, 53, 92, 0.12), 0 0 34px rgba(0, 119, 182, 0.16), inset 0 0 18px rgba(255, 255, 255, 0.80);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
        isolation: isolate;
    }

    
    .section-title {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 1.25rem;
        font-weight: 700;
        color: #005A9C !important;
        border-left: 5px solid #F59E0B;
        padding-left: 0.8rem;
        margin: 1.8rem 0 1.2rem;
        text-shadow: 0 0 12px rgba(0, 119, 182, 0.24);
    }
    
    /* Light dashboard cards */
    .gallery-card {
        background: rgba(255, 255, 255, 0.96) !important;
        border: 1px solid rgba(0, 61, 124, 0.10) !important;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 20px rgba(15, 53, 92, 0.08), 0 0 18px rgba(0, 119, 182, 0.08) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .gallery-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 14px 30px rgba(15, 53, 92, 0.14), 0 0 28px rgba(0, 119, 182, 0.24) !important;
        border-color: #0077B6 !important;
        background: #FFFFFF !important;
    }
    
    .rank-card {
        background: rgba(255, 255, 255, 0.96) !important;
        border: 1px solid rgba(0, 61, 124, 0.10) !important;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 1.2rem;
        box-shadow: 0 6px 18px rgba(15, 53, 92, 0.08), 0 0 14px rgba(0, 119, 182, 0.07) !important;
        transition: all 0.2s ease-in-out;
    }
    .rank-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(15, 53, 92, 0.12), 0 0 24px rgba(0, 119, 182, 0.20) !important;
        border-color: #0077B6 !important;
        background: #FFFFFF !important;
    }
    
    .rank-card img {
        height: 70px;
        width: 105px;
        object-fit: cover;
        border-radius: 8px;
        border: 1px solid rgba(0, 119, 182, 0.18);
        box-shadow: 0 4px 12px rgba(15, 53, 92, 0.08), 0 0 12px rgba(0, 119, 182, 0.10);
        transition: all 0.2s ease-in-out;
    }
    .rank-card:hover img {
        border-color: #0077B6;
        box-shadow: 0 8px 18px rgba(15, 53, 92, 0.14), 0 0 20px rgba(0, 119, 182, 0.26);
    }
    
    .rank-badge-1 { background:#F5A623; color:white; border-radius:50%; width:38px; height:38px;
                    display:flex; align-items:center; justify-content:center; font-weight:900; font-size:1.15rem; flex-shrink:0; box-shadow:0 0 10px rgba(245,166,35,0.4); }
    .rank-badge-2 { background:#C0C0C0; color:white; border-radius:50%; width:38px; height:38px;
                    display:flex; align-items:center; justify-content:center; font-weight:900; font-size:1.1rem; flex-shrink:0; box-shadow:0 0 10px rgba(192,192,192,0.4); }
    .rank-badge-3 { background:#CD7F32; color:white; border-radius:50%; width:38px; height:38px;
                    display:flex; align-items:center; justify-content:center; font-weight:900; font-size:1.1rem; flex-shrink:0; box-shadow:0 0 10px rgba(205,127,50,0.4); }
    .rank-badge   { background:#E8F0FA; color:#005A9C; border-radius:50%; width:38px; height:38px; border:1.5px solid rgba(0, 90, 156, 0.18);
                    display:flex; align-items:center; justify-content:center; font-weight:700; font-size:1rem; flex-shrink:0; box-shadow:0 0 12px rgba(0, 119, 182, 0.16); }
    
    .rank-info .name  { font-weight:700; font-size:1.1rem; color:#102A43; }
    .rank-info .specs { font-size:0.85rem; color:#52677A; margin-top:2px; }
    .rank-score {
        text-align: right;
        min-width: 90px;
        flex-shrink: 0;
    }
    .rank-score .value {
        font-size: 1.45rem;
        font-weight: 900;
        color: #005A9C;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 10px rgba(0, 119, 182, 0.22);
    }
    .rank-score .label {
        font-size: 0.7rem;
        color: #52677A;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    .cr-ok  { background:rgba(16, 185, 129, 0.10); color:#047857; padding:6px 14px; border-radius:20px; font-weight:700; font-size:0.9rem; display:inline-block; border: 1px solid rgba(16, 185, 129, 0.24); box-shadow: 0 0 16px rgba(16, 185, 129, 0.18); }
    .cr-bad { background:rgba(220, 38, 38, 0.10); color:#B91C1C; padding:6px 14px; border-radius:20px; font-weight:700; font-size:0.9rem; display:inline-block; border: 1px solid rgba(220, 38, 38, 0.24); box-shadow: 0 0 16px rgba(220, 38, 38, 0.14); }
    
    .info-bar { display:flex; gap:0.8rem; margin-bottom:1.5rem; flex-wrap:wrap; }
    .info-pill { background:linear-gradient(180deg, rgba(255,255,255,0.96), rgba(239,247,255,0.92)); border:1px solid rgba(0,119,182,0.13); border-radius:12px; padding:0.8rem 1.2rem;
                 flex:1; min-width:120px; text-align:center; box-shadow:0 6px 16px rgba(15, 53, 92, 0.07), 0 0 18px rgba(0, 119, 182, 0.08); }
    .info-pill .lbl { font-size:0.75rem; color:#52677A; margin-bottom:4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .info-pill .val { font-size:1.4rem; font-weight:800; color:#005A9C; font-family: 'Orbitron', sans-serif !important; text-shadow:0 0 10px rgba(0, 119, 182, 0.22); }
    
    /* Cyber sliders & tabs */
    .slider-label { 
        display:flex; 
        justify-content:space-between; 
        font-size:0.78rem; 
        color:#243044; 
        margin-bottom:-8px;
        font-weight: 600;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-weight: 600 !important;
        color: #005A9C !important;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 8px rgba(0, 119, 182, 0.18);
    }
    div[data-testid="stSlider"] {
        padding-bottom: 0px !important;
        margin-bottom: -15px !important;
    }
    
    /* Streamlit Tabs Futuristic Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.94) !important;
        border-radius: 12px !important;
        padding: 6px !important;
        border: 1px solid rgba(0, 61, 124, 0.10) !important;
        gap: 1rem;
        justify-content: space-around;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.05rem;
        padding: 0.8rem 1.5rem;
        min-width: 150px;
        font-weight: 600;
        color: #52677A !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        color: #005A9C !important;
        background-color: rgba(0, 90, 156, 0.10) !important;
        border-radius: 8px !important;
        text-shadow: 0 0 10px rgba(0, 119, 182, 0.18);
        box-shadow: 0 0 16px rgba(0, 119, 182, 0.12) !important;
    }
    
    /* Streamlit widgets overrides */
    div[data-testid="stVerticalBlock"],
    div[data-testid="stHorizontalBlock"],
    div[data-testid="stColumn"],
    div[data-testid="stElementContainer"],
    div[data-testid="stMarkdownContainer"] {
        color: #243044 !important;
    }

    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.92) !important;
        border: 1px solid rgba(0, 119, 182, 0.13) !important;
        border-radius: 12px !important;
        box-shadow: 0 6px 18px rgba(15, 53, 92, 0.07), 0 0 14px rgba(0, 119, 182, 0.06) !important;
    }

    div[data-testid="stExpander"] details,
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] div[role="button"] {
        background: transparent !important;
        color: #243044 !important;
    }

    div[data-testid="stMultiSelect"],
    div[data-testid="stSelectbox"],
    div[data-testid="stRadio"],
    div[data-testid="stSlider"] {
        color: #243044 !important;
    }

    div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.98) !important;
        border: 1px solid rgba(0, 61, 124, 0.14) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 14px rgba(15, 53, 92, 0.06) !important;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"],
    div[data-baseweb="input"],
    input,
    textarea {
        background-color: #FFFFFF !important;
        color: #243044 !important;
        border-color: rgba(0, 61, 124, 0.14) !important;
    }

    div[data-baseweb="tag"] {
        background: rgba(0, 119, 182, 0.10) !important;
        color: #005A9C !important;
        border: 1px solid rgba(0, 119, 182, 0.18) !important;
    }

    div[data-baseweb="tag"] span {
        color: #005A9C !important;
    }

    /* GANTI DENGAN KODE INI */
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div:first-child {
        padding-left: 8px !important;
        margin-left: 4px !important;
    }

    div[data-testid="stMultiSelect"] div[data-baseweb="tag"] {
        margin-left: 4px !important;
        margin-right: 4px !important;
        padding-left: 8px !important; /* Memperbaiki teks huruf pertama agar tidak mepet */
    }

    div[data-testid="stMultiSelect"] div[data-baseweb="tag"] {
        box-sizing: border-box !important;
        display: inline-flex !important;
        align-items: center !important;
        margin-left: 8px !important;
        padding: 2px 10px 2px 18px !important;
        position: relative !important;
        left: 0 !important;
        transform: none !important;
        text-indent: 0 !important;
        clip-path: none !important;
    }

    div[data-testid="stMultiSelect"] div[data-baseweb="tag"]:first-of-type {
        margin-left: 10px !important;
    }

    div[data-testid="stMultiSelect"] div[data-baseweb="tag"] *,
    div[data-testid="stMultiSelect"] div[data-baseweb="tag"] span,
    div[data-testid="stMultiSelect"] div[data-baseweb="tag"] [title] {
        box-sizing: border-box !important;
        margin-left: 0 !important;
        padding-left: 0 !important;
        position: static !important;
        left: auto !important;
        transform: none !important;
        text-indent: 0 !important;
        clip-path: none !important;
        color: #005A9C !important;
    }

    div[role="radiogroup"] label,
    div[role="radiogroup"] p,
    div[role="radiogroup"] span {
        color: #243044 !important;
    }

    div[role="radio"] {
        background-color: #FFFFFF !important;
        border-color: rgba(0, 119, 182, 0.22) !important;
    }

    div[role="listbox"] {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(0, 61, 124, 0.14) !important;
        color: #243044 !important;
        box-shadow: 0 12px 30px rgba(15, 53, 92, 0.12) !important;
    }

    div[role="option"],
    li[role="option"],
    ul[role="listbox"] li {
        background-color: #FFFFFF !important;
        color: #243044 !important;
    }

    div[role="option"]:hover,
    li[role="option"]:hover {
        background-color: #E8F0FA !important;
        color: #005A9C !important;
    }

    div[data-testid="stMetricValue"] {
        color: #005A9C !important;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 10px rgba(0, 119, 182, 0.20);
    }

    table,
    thead,
    tbody,
    tr,
    th,
    td {
        background-color: #FFFFFF !important;
        color: #243044 !important;
        border-color: rgba(0, 61, 124, 0.12) !important;
    }

    thead th {
        background-color: #E8F0FA !important;
        color: #102A43 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stAlert"] {
        background-color: rgba(255, 255, 255, 0.96) !important;
        color: #243044 !important;
        border-color: rgba(0, 119, 182, 0.16) !important;
    }

    .stMarkdown, .stText, p, label, small, div[data-testid="stMetricLabel"] {
        color: #243044 !important;
    }
    .main-header p, .rank-info .specs, .rank-score .label, .info-pill .lbl {
        color: #52677A !important;
    }
    .gallery-card div[style*="color:#FFFFFF"],
    .rank-card div[style*="color:#FFFFFF"],
    h3[style*="color:#FFFFFF"],
    h4[style*="color:#FFFFFF"] {
        color: #102A43 !important;
    }
    div[style*="color:#8892B0"],
    .rank-card div[style*="color:#8892B0"] {
        color: #52677A !important;
    }
    div[style*="background:rgba(255, 255, 255, 0.02)"],
    div[style*="background:rgba(255,255,255,0.02)"] {
        background: #FFFFFF !important;
        border-color: rgba(0, 61, 124, 0.10) !important;
        box-shadow: 0 8px 20px rgba(15, 53, 92, 0.08) !important;
    }
    div[style*="border-top:1px solid rgba(255,255,255,0.06)"] {
        border-top-color: rgba(0, 61, 124, 0.10) !important;
    }
</style>
"""),
    unsafe_allow_html=True,
)

DATASET_CSV = Path("dataset_ev_with_prices.csv")
FALLBACK_CSV = Path("df_ev_final.csv")

NON_INDICATOR_COLUMNS = {
    "brand",
    "model",
    "source_url",
    "ev_name",
    "image_url",
}

# The 20 Decision Features (incorporating all numerical indicators + mapped categorical ones)
LABELS = {
    "price_germany_eur": "Harga Jerman (EUR)",
    "range_km": "Jarak Tempuh (km)",
    "efficiency_wh_per_km": "Efisiensi Energi (Wh/km)",
    "fast_charging_power_kw_dc": "Daya Fast Charging (kW)",
    "battery_capacity_kWh": "Kapasitas Baterai (kWh)",
    "top_speed_kmh": "Kecepatan Maksimum (km/h)",
    "acceleration_0_100_s": "Akselerasi 0-100 km/h (detik)",
    "torque_nm": "Torsi Motor (Nm)",
    "number_of_cells": "Jumlah Sel Baterai",
    "towing_capacity_kg": "Kapasitas Towing (kg)",
    "cargo_volume_l": "Volume Bagasi (L)",
    "seats": "Jumlah Kursi",
    "length_mm": "Panjang (mm)",
    "width_mm": "Lebar (mm)",
    "height_mm": "Tinggi (mm)",
    "battery_type": "Tipe Baterai (Skala NMC)",
    "fast_charge_port": "Port Fast Charge (Skala Standar)",
    "drivetrain": "Sistem Penggerak (Skala Traksi)",
    "segment": "Segmen Ukuran Mobil",
    "car_body_type": "Tipe Bodi Kendaraan",
}

DEFAULT_TYPES = {
    "price_germany_eur": "cost",
    "efficiency_wh_per_km": "cost",
    "acceleration_0_100_s": "cost",
    "top_speed_kmh": "benefit",
    "battery_capacity_kWh": "benefit",
    "number_of_cells": "benefit",
    "torque_nm": "benefit",
    "range_km": "benefit",
    "fast_charging_power_kw_dc": "benefit",
    "towing_capacity_kg": "benefit",
    "cargo_volume_l": "benefit",
    "seats": "benefit",
    "length_mm": "benefit",
    "width_mm": "benefit",
    "height_mm": "benefit",
    "battery_type": "benefit",
    "fast_charge_port": "benefit",
    "drivetrain": "benefit",
    "segment": "benefit",
    "car_body_type": "benefit",
}

DEFAULT_INDICATORS = [
    "price_germany_eur",
    "range_km",
    "efficiency_wh_per_km",
    "fast_charging_power_kw_dc",
    "battery_capacity_kWh",
    "top_speed_kmh",
    "acceleration_0_100_s",
    "torque_nm",
    "cargo_volume_l",
    "drivetrain",
]

RI = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12, 
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49, 
    11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59,
}

@st.cache_data
def load_data() -> pd.DataFrame:
    if DATASET_CSV.exists():
        df = pd.read_csv(DATASET_CSV)
    elif FALLBACK_CSV.exists():
        df = pd.read_csv(FALLBACK_CSV)
    else:
        raise FileNotFoundError("Tidak menemukan dataset_ev_with_prices.csv atau df_ev_final.csv.")

    df = df.copy()
    
    # 1. Clean cargo volume (replacing non-numeric values like "10 Banana Boxes" to standard liter capacity)
    if "cargo_volume_l" in df.columns:
        df["cargo_volume_l"] = df["cargo_volume_l"].astype(str).str.replace(r".*Banana Boxes.*", "400", regex=True)

    # Store raw copies of categorical fields for filtering and human-readable displays
    df["brand_raw"] = df["brand"].fillna("Unknown").astype(str)
    df["segment_raw"] = df["segment"].fillna("Unknown").astype(str)
    df["car_body_type_raw"] = df["car_body_type"].fillna("Unknown").astype(str)
    df["drivetrain_raw"] = df["drivetrain"].fillna("Unknown").astype(str)
    df["fast_charge_port_raw"] = df["fast_charge_port"].fillna("Unknown").astype(str)

    # 2. Encode categorical indicators numerically to serve as active MCDM features
    if "battery_type" in df.columns:
        df["battery_type"] = df["battery_type"].map({"Lithium-ion": 1.0}).fillna(0.0)
    if "fast_charge_port" in df.columns:
        df["fast_charge_port"] = df["fast_charge_port"].map({"CCS": 2.0, "CHAdeMO": 1.0}).fillna(0.0)
    if "drivetrain" in df.columns:
        df["drivetrain"] = df["drivetrain"].map({"AWD": 3.0, "RWD": 2.0, "FWD": 1.0}).fillna(0.0)
        
    if "segment" in df.columns:
        def map_segment(s):
            if pd.isna(s): return 0.0
            s = str(s).upper()
            if 'MINI' in s or 'A -' in s: return 1.0
            if 'COMPACT' in s or 'B -' in s: return 2.0
            if 'MEDIUM' in s or 'C -' in s: return 3.0
            if 'LARGE' in s or 'D -' in s: return 4.0
            if 'EXECUTIVE' in s or 'E -' in s: return 5.0
            if 'LUXURY' in s or 'F -' in s or 'I -' in s: return 6.0
            if 'SPORTS' in s or 'G -' in s: return 5.0
            if 'VAN' in s or 'N -' in s: return 3.0
            return 3.0
        df["segment"] = df["segment"].apply(map_segment)
        
    if "car_body_type" in df.columns:
        body_map = {
            "SUV": 5.0, "Small Passenger Van": 4.0, "Station/Estate": 4.0,
            "Sedan": 3.0, "Liftback Sedan": 3.0, "Coupe": 2.0, "Cabriolet": 2.0,
            "Hatchback": 1.0
        }
        df["car_body_type"] = df["car_body_type"].map(body_map).fillna(0.0)

    # 3. Numeric conversion of features
    for col in df.columns:
        if col not in NON_INDICATOR_COLUMNS and col not in ["brand_raw", "segment_raw", "car_body_type_raw", "drivetrain_raw", "fast_charge_port_raw"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["brand"] = df["brand_raw"]
    df["model"] = df["model"].fillna("Unknown").astype(str)
    df["ev_name"] = df["brand"] + " " + df["model"]
    df.reset_index(drop=True, inplace=True)
    return df

def indicator_columns(df: pd.DataFrame) -> list[str]:
    # Returns all 20 decision features
    return list(LABELS.keys())

def label_for(key: str) -> str:
    return LABELS.get(key, key.replace("_", " ").title())

def multiselect_label_for(key: str) -> str:
    return f"\u00a0{label_for(key)}"

def build_criteria(keys: list[str], types: dict[str, str]) -> dict[str, dict[str, str]]:
    return {
        key: {
            "label": label_for(key),
            "code": f"C{i + 1}",
            "type": types.get(key, DEFAULT_TYPES.get(key, "benefit")),
        }
        for i, key in enumerate(keys)
    }

def build_pairwise_matrix(slider_values: dict, n: int) -> np.ndarray:
    mat = np.ones((n, n))
    for idx, (i, j) in enumerate(combinations(range(n), 2)):
        val = slider_values.get(f"{i}_{j}", 0)
        # slider maps -8 to 8 linearly matching AHP Saaty 1-9 scale with 0 as equal
        if val == 0:
            ratio = 1.0
        elif val > 0:
            ratio = float(val + 1)
        else:
            ratio = 1.0 / (abs(float(val)) + 1.0)
        mat[i, j] = ratio
        mat[j, i] = 1.0 / ratio
    return mat

def build_pairwise_matrix_from_ratings(ratings: dict, keys: list[str]) -> np.ndarray:
    n = len(keys)
    mat = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                r_i = float(ratings.get(keys[i], 5))
                r_j = float(ratings.get(keys[j], 5))
                mat[i, j] = r_i / r_j
    return mat

def compute_ahp(mat: np.ndarray):
    n = mat.shape[0]
    col_sums = mat.sum(axis=0)
    norm = mat / col_sums
    weights = norm.mean(axis=1)

    weighted_sum = mat @ weights
    lambda_vec = weighted_sum / weights
    lambda_max = lambda_vec.mean()
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0
    ri = RI.get(n, 1.59)
    cr = ci / ri if ri else 0
    return weights, lambda_max, ci, cr

def run_topsis(df: pd.DataFrame, criteria: dict[str, dict[str, str]], weights: np.ndarray) -> pd.DataFrame:
    keys = list(criteria.keys())
    result = df.copy()
    
    # Extract decision matrix values
    dm = result[keys].to_numpy(dtype=float)

    # Impute NaNs dynamically with column median to prevent row deletion, keeping dataset complete
    for j in range(dm.shape[1]):
        col = dm[:, j]
        nan_mask = np.isnan(col)
        if nan_mask.any():
            median_val = np.nanmedian(col)
            if np.isnan(median_val):
                median_val = 0.0
            col[nan_mask] = median_val
            dm[:, j] = col

    norms = np.sqrt((dm**2).sum(axis=0))
    norms[norms == 0] = 1
    weighted = (dm / norms) * weights

    a_pos = np.zeros(len(keys))
    a_neg = np.zeros(len(keys))
    for j, key in enumerate(keys):
        if criteria[key]["type"] == "benefit":
            a_pos[j] = weighted[:, j].max()
            a_neg[j] = weighted[:, j].min()
        else:
            a_pos[j] = weighted[:, j].min()
            a_neg[j] = weighted[:, j].max()

    d_pos = np.sqrt(((weighted - a_pos) ** 2).sum(axis=1))
    d_neg = np.sqrt(((weighted - a_neg) ** 2).sum(axis=1))
    result["topsis_score"] = d_neg / (d_pos + d_neg + 1e-10)
    result = result.sort_values("topsis_score", ascending=False).reset_index(drop=True)
    result["rank"] = result.index + 1
    return result

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    filter_cols = ["brand", "segment", "car_body_type", "drivetrain", "fast_charge_port"]
    with st.expander("⚙️ Filter alternatif EV", expanded=False):
        for col in filter_cols:
            raw_col = f"{col}_raw"
            options = sorted(filtered[raw_col].dropna().astype(str).unique())
            selected = st.multiselect(label_for(col), options, default=options, key=f"filter_{col}")
            if selected:
                filtered = filtered[filtered[raw_col].astype(str).isin(selected)]
    return filtered

def format_price(value):
    try:
        value = float(value)
        return f"€{value:,.0f}"
    except (TypeError, ValueError):
        return "N/A"

def format_metric(value, unit=""):
    if pd.isna(value):
        return "N/A"
    if isinstance(value, (int, np.integer)):
        return f"{value}{unit}"
    if isinstance(value, (float, np.floating)):
        if value.is_integer():
            return f"{int(value)}{unit}"
        return f"{value:.1f}{unit}"
    return f"{value}{unit}"

def light_table_style(styler):
    return styler.set_properties(
        **{
            "background-color": "#FFFFFF",
            "color": "#243044",
            "border-color": "rgba(0, 61, 124, 0.12)",
        }
    ).set_table_styles(
        [
            {"selector": "table", "props": [("background-color", "#FFFFFF"), ("color", "#243044")]},
            {"selector": "thead th", "props": [("background-color", "#E8F0FA"), ("color", "#102A43"), ("font-weight", "700")]},
            {"selector": "tbody th", "props": [("background-color", "#F8FBFF"), ("color", "#102A43"), ("font-weight", "700")]},
            {"selector": "td", "props": [("background-color", "#FFFFFF"), ("color", "#243044")]},
        ],
        overwrite=False,
    )

def render_gallery(results_df: pd.DataFrame):
    st.markdown('<div class="section-title">🏆 Top 3 Rekomendasi Utama</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    top3 = results_df.head(3)
    for idx, (_, row) in enumerate(top3.iterrows()):
        rank = idx + 1
        score_pct = int(round(row["topsis_score"] * 100))
        img_url = row.get("image_url")
        if pd.isna(img_url) or not img_url:
            img_html = '<div style="width:100%; height:130px; background:rgba(232,240,250,0.75); border-radius:12px; display:flex; align-items:center; justify-content:center; color:#0077B6; font-weight:700; margin-bottom:1rem; border:1px solid rgba(0,61,124,0.10);">Gambar Tidak Tersedia</div>'
        else:
            img_html = f'<img src="{img_url}" alt="{row["ev_name"]}" style="width:100%; height:130px; object-fit:cover; border-radius:12px; margin-bottom:1rem; border:1.5px solid rgba(0, 119, 182, 0.20); box-shadow:0 6px 14px rgba(15,53,92,0.10), 0 0 18px rgba(0,119,182,0.16);" />'
        
        badge_color = "linear-gradient(90deg, #F59E0B 0%, #FCD34D 100%)" if rank == 1 else ("linear-gradient(90deg, #9AD0EC 0%, #B8E1FF 100%)" if rank == 2 else "linear-gradient(90deg, #B5838D 0%, #E0A96D 100%)")
        medal = "🥇 TELEMETRY #1" if rank == 1 else ("🥈 TELEMETRY #2" if rank == 2 else "🥉 TELEMETRY #3")
        
        drivetrain_val = row.get("drivetrain_raw", "N/A")
        body_val = row.get("car_body_type_raw", "N/A")
        
        with cols[idx]:
            html_content = f"""
            <div class="gallery-card">
                <div style="background:{badge_color}; color:white; font-weight:800; padding:0.25rem 0.8rem; border-radius:20px; font-size:0.8rem; display:inline-block; margin-bottom:0.8rem; font-family:\'Orbitron\',sans-serif; text-shadow:0 0 8px rgba(255,255,255,0.42); box-shadow:0 0 16px rgba(245,158,11,0.26);">{medal}</div>
                {img_html}
                <div style="font-weight:800; font-size:1.1rem; color:#102A43; margin-bottom:0.5rem; height: 45px; display: flex; align-items: center; justify-content: center; line-height: 1.2;">{row['ev_name']}</div>
                <div style="font-size:1.8rem; font-weight:900; color:#0077B6; font-family:\'Orbitron\',sans-serif; text-shadow:0 0 12px rgba(0,119,182,0.26); margin-bottom:0.1rem;">{score_pct}%</div>
                <div style="font-size:0.75rem; color:#52677A; margin-bottom:0.8rem; text-transform:uppercase; letter-spacing:0.5px;">Match Score</div>
                <div style="display:flex; justify-content:center; gap:6px; margin-bottom:0.8rem; flex-wrap:wrap;">
                    <span style="background:rgba(0, 119, 182, 0.08); color:#0077B6; padding:1px 6px; border-radius:10px; font-size:0.7rem; font-weight:700; border:1px solid rgba(0, 119, 182, 0.15);">⚙️ {drivetrain_val}</span>
                    <span style="background:rgba(245, 158, 11, 0.10); color:#B45309; padding:1px 6px; border-radius:10px; font-size:0.7rem; font-weight:700; border:1px solid rgba(245, 158, 11, 0.22);">🚗 {body_val}</span>
                </div>
                <div style="font-size:0.8rem; color:#52677A; border-top:1px solid rgba(0,61,124,0.10); padding-top:0.8rem; display:flex; justify-content:space-around;">
                    <span>💶 {format_price(row.get('price_germany_eur'))}</span>
                    <span>🛣️ {format_metric(row.get('range_km'), ' km')}</span>
                </div>
            </div>
            """
            st.markdown(clean_html(html_content), unsafe_allow_html=True)

def render_rank_card(row: pd.Series, rank: int, criteria_keys: list[str]):
    if rank == 1:
        badge_cls = "rank-badge-1"
        medal = "🥇"
    elif rank == 2:
        badge_cls = "rank-badge-2"
        medal = "🥈"
    elif rank == 3:
        badge_cls = "rank-badge-3"
        medal = "🥉"
    else:
        badge_cls = "rank-badge"
        medal = str(rank)
        
    score_pct = int(round(row["topsis_score"] * 100))
    specs = (
        f"💶 {format_price(row.get('price_germany_eur'))} &nbsp;|&nbsp; "
        f"🛣️ {format_metric(row.get('range_km'), ' km')} &nbsp;|&nbsp; "
        f"⚡ {format_metric(row.get('efficiency_wh_per_km'), ' Wh/km')} &nbsp;|&nbsp; "
        f"🔋 {format_metric(row.get('battery_capacity_kWh'), ' kWh')} &nbsp;|&nbsp; "
        f"⚡ {format_metric(row.get('fast_charging_power_kw_dc'), ' kW')}"
    )
    
    # Styled badges for metadata
    drivetrain_val = row.get("drivetrain_raw", "N/A")
    body_val = row.get("car_body_type_raw", "N/A")
    segment_val = row.get("segment_raw", "N/A").split(" ")[0]
    
    badges_html = f"""
    <div style="margin-top: 6px; display: flex; gap: 8px; flex-wrap: wrap;">
        <span style="background:rgba(0, 119, 182, 0.08); color:#0077B6; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:700; border:1px solid rgba(0, 119, 182, 0.2);">⚙️ {drivetrain_val}</span>
        <span style="background:rgba(245, 158, 11, 0.10); color:#B45309; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:700; border:1px solid rgba(245, 158, 11, 0.22);">🚗 {body_val}</span>
        <span style="background:rgba(16, 185, 129, 0.10); color:#047857; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:700; border:1px solid rgba(16, 185, 129, 0.22);">🏷️ Segmen {segment_val}</span>
    </div>
    """
    
    img_url = row.get("image_url")
    if pd.isna(img_url) or not img_url:
        img_html = '<div style="width:105px; height:70px; background:rgba(232,240,250,0.75); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#0077B6; font-size:0.65rem; font-weight:700; flex-shrink:0; border:1px solid rgba(0,61,124,0.10);">No Image</div>'
    else:
        img_html = f'<img src="{img_url}" alt="{row["ev_name"]}" />'
        
    html_content = f"""
    <div class="rank-card">
        <div class="{badge_cls}">{medal}</div>
        {img_html}
        <div class="rank-info" style="flex-grow:1">
            <div class="name" style="color:#102A43 !important; font-weight:700; font-size:1.1rem;">{row['ev_name']}</div>
            <div class="specs" style="color:#52677A !important; font-size:0.85rem; margin-top:2px;">{specs}</div>
            {badges_html}
        </div>
        <div class="rank-score">
            <div class="value">{score_pct}%</div>
            <div class="label">TOPSIS Score</div>
        </div>
    </div>
    """
    st.markdown(clean_html(html_content), unsafe_allow_html=True)

def main():
    df = load_data()
    all_indicators = indicator_columns(df)
    
    # Title with light dashboard theme
    header_html = """
    <div class="main-header">
        <div style="display:flex; align-items:center; gap:1.5rem;">
            <div style="font-size:3rem; text-shadow:0 0 18px rgba(0,119,182,0.32), 0 0 10px rgba(245,158,11,0.24);">🏎️</div>
            <div>
                <h1 style="font-family:\'Orbitron\',sans-serif; text-shadow:0 0 18px rgba(0,119,182,0.22); font-weight:900; letter-spacing:1px; margin:0; background:linear-gradient(90deg, #005A9C 0%, #2F80ED 55%, #F59E0B 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">EV INTELLIGENCE MATRIX</h1>
                <p style="margin:4px 0 0 0; color:#52677A; font-size:1.05rem;">Sistem Pendukung Keputusan Cerdas Pemilihan Mobil Listrik berbasis AHP-TOPSIS</p>
            </div>
        </div>
    </div>
    """
    st.markdown(clean_html(header_html), unsafe_allow_html=True)

    info_bar_html = f"""
    <div class="info-bar">
        <div class="info-pill"><div class="lbl">Database Alternatif</div><div class="val">{len(df)}</div></div>
        <div class="info-pill"><div class="lbl">Manufaktur / Brand</div><div class="val">{df['brand'].nunique()}</div></div>
        <div class="info-pill"><div class="lbl">Kriteria Evaluasi</div><div class="val">{len(all_indicators)}</div></div>
        <div class="info-pill"><div class="lbl">Sistem Engine</div><div class="val" style="color:#047857; text-shadow:0 0 12px rgba(16,185,129,0.26);">READY</div></div>
    </div>
    """
    st.markdown(clean_html(info_bar_html), unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎛️ Preferensi & Rekomendasi",
        "📊 Analisis AHP",
        "🔍 Detail TOPSIS",
        "📈 Eksplorasi Data"
    ])

    with tab1:
        st.markdown('<div class="section-title">1. Pilih Indikator Keputusan (Maksimal 20 Fitur)</div>', unsafe_allow_html=True)
        selected_keys = st.multiselect(
            "Pilih fitur yang ingin dilibatkan dalam keputusan pemilihan mobil:",
            options=all_indicators,
            default=DEFAULT_INDICATORS,
            format_func=multiselect_label_for,
            help="Semua kolom spesifikasi tersedia sebagai fitur keputusan, baik spesifikasi teknik, ukuran bodi, maupun kategori terenkripsi.",
        )
        
        if len(selected_keys) < 2:
            st.warning("Pilih minimal 2 indikator agar perbandingan AHP dan TOPSIS dapat dihitung.")
            st.stop()
            
        # Cost / Benefit Configuration
        indicator_types = {}
        with st.expander("⚖️ Konfigurasi Karakteristik Fitur (Benefit vs Cost)", expanded=False):
            st.caption("Benefit: Nilai semakin besar semakin baik (contoh: Jarak Tempuh, Torsi). Cost: Nilai semakin kecil semakin baik (contoh: Harga, Akselerasi).")
            type_cols = st.columns(3)
            for idx, key in enumerate(selected_keys):
                with type_cols[idx % 3]:
                    default_type = DEFAULT_TYPES.get(key, "benefit")
                    indicator_types[key] = st.radio(
                        label_for(key),
                        options=["benefit", "cost"],
                        index=0 if default_type == "benefit" else 1,
                        horizontal=True,
                        key=f"type_{key}",
                    )
                    
        criteria = build_criteria(selected_keys, indicator_types)
        filtered_df = apply_filters(df)
        
        # simplified weights vs pairwise selector
        st.markdown('<div class="section-title">2. Atur Bobot Prioritas Kriteria</div>', unsafe_allow_html=True)
        weight_mode = st.radio(
            "Metode Pembobotan Kriteria:",
            options=[
                "⭐ Rating Langsung (Simpel & Cepat - Direkomendasikan)",
                "⚖️ Perbandingan Berpasangan (Detail AHP)"
            ],
            horizontal=True,
            help="Rating Langsung: Anda memberikan skor kepentingan 1-9 untuk masing-masing kriteria secara langsung (matriks berpasangan dikonstruksi secara konsisten otomatis). Perbandingan Berpasangan: Mengatur slider AHP untuk membandingkan kriteria satu per satu."
        )
        
        slider_values = {}
        criterion_ratings = {}
        
        if weight_mode == "⭐ Rating Langsung (Simpel & Cepat - Direkomendasikan)":
            st.markdown("<small>Berikan tingkat kepentingan kriteria (1 = Sangat Tidak Penting, 9 = Sangat Penting/Mutlak). Sistem akan menghasilkan matriks AHP konsisten secara otomatis.</small>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            rating_cols = st.columns(3)
            for idx, key in enumerate(selected_keys):
                with rating_cols[idx % 3]:
                    criterion_ratings[key] = st.slider(
                        label_for(key),
                        min_value=1,
                        max_value=9,
                        value=5, # Moderate importance
                        key=f"rating_{key}"
                    )
        else:
            # Pairwise AHP Sliders
            num_comparisons = len(selected_keys) * (len(selected_keys) - 1) // 2
            if num_comparisons > 20:
                st.warning(f"Jumlah kriteria yang dipilih banyak ({len(selected_keys)} kriteria), sehingga dibutuhkan {num_comparisons} slider perbandingan berpasangan. Kami menyarankan menggunakan metode 'Rating Langsung' agar lebih ringkas.")
                
            st.markdown("<small>Sesuaikan prioritas antar kriteria. Menggeser slider ke kiri memprioritaskan kriteria kiri, ke kanan memprioritaskan kriteria kanan.</small>", unsafe_allow_html=True)
            for i in range(len(selected_keys) - 1):
                left_label = label_for(selected_keys[i])
                
                with st.expander(f"🔹 Bandingkan: {left_label} vs Kriteria Lain", expanded=(i==0)):
                    comparisons = list(range(i + 1, len(selected_keys)))
                    grid_cols = st.columns(3) if len(comparisons) > 2 else st.columns(len(comparisons))
                    
                    for c_idx, j in enumerate(comparisons):
                        col = grid_cols[c_idx % len(grid_cols)]
                        right_label = label_for(selected_keys[j])
                        with col:
                            st.markdown(
                                f'<div class="slider-label"><span>{left_label}</span><span style="color:#aaa;">vs</span><span>{right_label}</span></div>',
                                unsafe_allow_html=True,
                            )
                            slider_values[f"{i}_{j}"] = st.slider(
                                "",
                                min_value=-8,
                                max_value=8,
                                value=0, # Default: equal importance (0)
                                key=f"pair_{i}_{j}",
                                label_visibility="collapsed",
                            )
                            st.markdown("<br>", unsafe_allow_html=True)

        # -------------------------------------------------------------------------
        # REAL-TIME DECISION CALCULATIONS (REACTIVE)
        # -------------------------------------------------------------------------
        if filtered_df.empty:
            st.error("Tidak ada EV yang memenuhi filter. Silakan ubah filter alternatif Anda.")
        else:
            if weight_mode == "⭐ Rating Langsung (Simpel & Cepat - Direkomendasikan)":
                mat = build_pairwise_matrix_from_ratings(criterion_ratings, selected_keys)
            else:
                mat = build_pairwise_matrix(slider_values, len(selected_keys))
                
            weights, lmax, ci, cr = compute_ahp(mat)
            results = run_topsis(filtered_df, criteria, weights)
            
            # Save variables into session state for cross-tab availability
            st.session_state["ahp_matrix"] = mat
            st.session_state["ahp_weights"] = weights
            st.session_state["ahp_lmax"] = lmax
            st.session_state["ahp_ci"] = ci
            st.session_state["ahp_cr"] = cr
            st.session_state["criteria"] = criteria
            st.session_state["criteria_keys"] = selected_keys
            st.session_state["results"] = results
            st.session_state["filtered_df"] = filtered_df

        st.markdown("---") 

        # Display output reactively
        if "results" in st.session_state:
            criteria = st.session_state["criteria"]
            selected_keys = st.session_state["criteria_keys"]
            results = st.session_state["results"]
            weights = st.session_state["ahp_weights"]
            cr = st.session_state["ahp_cr"]
            
            # Horizontal layout displaying results
            out_col1, out_col2 = st.columns([1, 1.5], gap="large")
            
            with out_col1:
                st.markdown('<div class="section-title">Status Konsistensi AHP</div>', unsafe_allow_html=True)
                if cr < 0.1:
                    html_cr = f'<span class="cr-ok">CR = {cr:.4f} - Konsisten (Valid)</span>'
                else:
                    html_cr = f'<span class="cr-bad">CR = {cr:.4f} - Tidak Konsisten (Harap setel ulang)</span>'
                st.markdown(clean_html(html_cr), unsafe_allow_html=True)
                    
                st.markdown('<div class="section-title">Bobot Prioritas Kriteria</div>', unsafe_allow_html=True)
                fig_w = go.Figure(
                    go.Bar(
                        x=[criteria[k]["code"] for k in selected_keys],
                        y=weights,
                        marker_color=["#0077B6" if criteria[k]["type"] == "cost" else "#F59E0B" for k in selected_keys],
                        text=[f"{value:.3f}" for value in weights],
                        textposition="outside",
                        textfont=dict(color="#243044"),
                        hovertemplate="Kriteria: %{customdata}<br>Bobot: %{y:.4f}<extra></extra>",
                        customdata=[criteria[k]["label"] for k in selected_keys]
                    )
                )
                fig_w.update_layout(
                    height=260, margin=dict(t=20, b=10, l=0, r=0),
                    yaxis_title="Bobot", showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(range=[0, max(weights) * 1.3], gridcolor="rgba(16,42,67,0.10)", tickfont=dict(color="#52677A")),
                    xaxis=dict(tickfont=dict(color="#52677A"))
                )
                st.plotly_chart(fig_w, use_container_width=True)
                
            with out_col2:
                st.markdown('<div class="section-title">Rekomendasi Alternatif EV</div>', unsafe_allow_html=True)
                # Render results rank cards
                for idx, row in results.head(5).iterrows():
                    render_rank_card(row, int(row["rank"]), selected_keys)
                    
            # Render Top 3 horizontal gallery with images!
            st.write("")
            render_gallery(results)
            
            # Interactive Comparison Section
            st.markdown('<div class="section-title">🔍 Bandingkan Kendaraan Pilihan Anda</div>', unsafe_allow_html=True)
            with st.expander("Bandingkan Mobil Pilihan Secara Detail (Maksimal 3 Mobil)", expanded=False):
                compare_options = results["ev_name"].tolist()
                selected_compare = st.multiselect(
                    "Pilih mobil dari daftar untuk dibandingkan secara berdampingan:",
                    options=compare_options,
                    max_selections=3,
                    key="compare_select"
                )
                if selected_compare:
                    compare_df = results[results["ev_name"].isin(selected_compare)]
                    comp_cols = st.columns(len(selected_compare))
                    for idx, (_, c_row) in enumerate(compare_df.iterrows()):
                        with comp_cols[idx]:
                            c_img = c_row.get("image_url")
                            c_img_html = f'<img src="{c_img}" style="width:100%; height:130px; object-fit:cover; border-radius:12px; border:1.5px solid rgba(0, 119, 182, 0.20); box-shadow:0 6px 14px rgba(15, 53, 92, 0.10), 0 0 16px rgba(0,119,182,0.14); margin-bottom:0.8rem;" />' if pd.notna(c_img) and c_img else '<div style="width:100%; height:130px; background:rgba(232,240,250,0.75); border-radius:12px; display:flex; align-items:center; justify-content:center; color:#0077B6; font-weight:700; margin-bottom:0.8rem; border:1px solid rgba(0,61,124,0.10); box-shadow:0 0 14px rgba(0,119,182,0.10);">No Image</div>'
                            
                            # Calculate simple progress indicators for key specs
                            max_price = df["price_germany_eur"].max()
                            max_range = df["range_km"].max()
                            max_efficiency = df["efficiency_wh_per_km"].max()
                            
                            def bar_html(val, max_val, color="#0077B6"):
                                if pd.isna(val) or pd.isna(max_val) or max_val == 0:
                                    return ""
                                pct = min(100, int((val / max_val) * 100))
                                return f"""
                                <div style="width:100%; background:rgba(232,240,250,0.95); height:5px; border-radius:3px; margin:2px 0 8px 0; overflow:hidden; border:1px solid rgba(0,61,124,0.08);">
                                    <div style="width:{pct}%; background:linear-gradient(90deg, {color} 0%, #2F80ED 100%); height:100%; border-radius:3px; box-shadow:0 0 10px {color};"></div>
                                </div>
                                """
                            
                            price_bar = bar_html(c_row.get("price_germany_eur"), max_price, "#DC2626")
                            range_bar = bar_html(c_row.get("range_km"), max_range, "#10B981")
                            eff_bar = bar_html(c_row.get("efficiency_wh_per_km"), max_efficiency, "#0077B6")
                            
                            html_comp = f"""
                            <div style="background:linear-gradient(180deg, #FFFFFF 0%, #F3FAFF 100%); border:1px solid rgba(0, 119, 182, 0.14); border-radius:16px; padding:1.2rem; box-shadow:0 8px 20px rgba(15,53,92,0.08), 0 0 20px rgba(0,119,182,0.10); text-align:center;">
                                {c_img_html}
                                <h4 style="color:#102A43; font-weight:800; margin:0 0 0.5rem; height:40px; display:flex; align-items:center; justify-content:center; font-size:1rem; line-height:1.2;">{c_row['ev_name']}</h4>
                                <div style="background:linear-gradient(90deg, #0077B6 0%, #2F80ED 100%); color:white; font-weight:800; padding:2px 10px; border-radius:12px; font-size:0.75rem; display:inline-block; margin-bottom:0.8rem; text-shadow:0 0 8px rgba(255,255,255,0.35); box-shadow:0 0 14px rgba(0,119,182,0.22);">Peringkat {c_row['rank']}</div>
                                <div style="text-align:left; font-size:0.82rem; line-height:1.5; border-top:1px solid rgba(0,61,124,0.10); padding-top:0.8rem; color:#243044;">
                                    <b>Harga:</b> {format_price(c_row.get('price_germany_eur'))}
                                    {price_bar}
                                    <b>Jarak Tempuh:</b> {format_metric(c_row.get('range_km'), ' km')}
                                    {range_bar}
                                    <b>Efisiensi:</b> {format_metric(c_row.get('efficiency_wh_per_km'), ' Wh/km')}
                                    {eff_bar}
                                    <b>Akselerasi:</b> {format_metric(c_row.get('acceleration_0_100_s'), ' detik')}<br/>
                                    <b>Baterai:</b> {format_metric(c_row.get('battery_capacity_kWh'), ' kWh')}<br/>
                                    <b>Fast Charging:</b> {format_metric(c_row.get('fast_charging_power_kw_dc'), ' kW')}<br/>
                                    <b>Penggerak:</b> {c_row.get('drivetrain_raw', 'N/A')}<br/>
                                    <b>Bodi:</b> {c_row.get('car_body_type_raw', 'N/A')}<br/>
                                    <div style="text-align:center; margin-top:0.8rem; font-weight:800; font-size:1.15rem; color:#0077B6; font-family:\'Orbitron\',sans-serif; text-shadow:0 0 12px rgba(0,119,182,0.24);">Kecocokan: {int(round(c_row['topsis_score']*100))}%</div>
                                </div>
                            </div>
                            """
                            st.markdown(clean_html(html_comp), unsafe_allow_html=True)
                else:
                    st.caption("Pilih 1 s.d. 3 mobil di atas untuk menampilkan perbandingan komprehensif.")

            # Radar Match Analysis of Top #1 Car in layout with image
            st.markdown('<div class="section-title">Analisis Kesesuaian Kriteria Mobil Terbaik (#1)</div>', unsafe_allow_html=True)
            top1 = results.iloc[0]
            df_ref = st.session_state["filtered_df"]
            
            top1_col1, top1_col2 = st.columns([1, 1.3], gap="large")
            
            with top1_col1:
                t1_img = top1.get("image_url")
                if pd.notna(t1_img) and t1_img:
                    html_top1 = f"""
                    <div style="background:linear-gradient(180deg, #FFFFFF 0%, #F3FAFF 100%); padding:1.2rem; border-radius:16px; border:1px solid rgba(0,119,182,0.16); box-shadow:0 8px 20px rgba(15,53,92,0.08), 0 0 24px rgba(0,119,182,0.13); text-align:center;">
                        <img src="{t1_img}" alt="{top1['ev_name']}" style="width:100%; max-height:220px; object-fit:cover; border-radius:12px; margin-bottom:1rem; border:1.5px solid rgba(0,119,182,0.20); box-shadow:0 6px 14px rgba(15,53,92,0.10), 0 0 18px rgba(0,119,182,0.16);" />
                        <h3 style="color:#102A43; margin-bottom:0.5rem; font-weight:800; font-family:\'Orbitron\',sans-serif;">{top1['ev_name']}</h3>
                        <span style="background:linear-gradient(90deg, #F59E0B 0%, #FCD34D 100%); color:white; padding:0.3rem 1.2rem; border-radius:20px; font-weight:700; font-size:0.9rem; font-family:\'Orbitron\',sans-serif; text-shadow:0 0 8px rgba(255,255,255,0.42); box-shadow:0 0 16px rgba(245,158,11,0.30);">MATCH: {int(round(top1['topsis_score']*100))}%</span>
                    </div>
                    """
                    st.markdown(clean_html(html_top1), unsafe_allow_html=True)
                else:
                    st.info("Gambar mobil terbaik tidak tersedia.")
                
                # Dynamic Spec Details Table
                st.markdown("<br>", unsafe_allow_html=True)
                specs_data = {
                    "Kriteria Utama": [label_for(k) for k in selected_keys[:5]],
                    "Nilai Spesifikasi": [format_metric(top1.get(k), f" {k.split('_')[-1]}" if '_' in k else "") for k in selected_keys[:5]]
                }
                st.table(light_table_style(pd.DataFrame(specs_data).style))
                
            with top1_col2:
                top1_norm = []
                pref_norm = []
                
                for key in selected_keys:
                    col_min = df_ref[key].min()
                    col_max = df_ref[key].max()
                    rng = col_max - col_min if col_max != col_min else 1
                    raw_norm = (top1[key] - col_min) / rng
                    if criteria[key]["type"] == "cost":
                        top1_norm.append(1 - raw_norm)
                    else:
                        top1_norm.append(raw_norm)
                    pref_norm.append(1.0)
                    
                weight_scale = weights / weights.max()
                top1_weighted = [top1_norm[i] * weight_scale[i] for i in range(len(selected_keys))]
                pref_weighted = [pref_norm[i] * weight_scale[i] for i in range(len(selected_keys))]
                radar_labels = [label_for(key) for key in selected_keys]
                
                fig_r = go.Figure()
                fig_r.add_trace(go.Scatterpolar(
                    r=pref_weighted + [pref_weighted[0]], 
                    theta=radar_labels + [radar_labels[0]], 
                    fill="toself", 
                    fillcolor="rgba(245,158,11,0.10)", 
                    line=dict(color="#F59E0B", dash="dash", width=2), 
                    name="Profil Preferensi Anda"
                ))
                fig_r.add_trace(go.Scatterpolar(
                    r=top1_weighted + [top1_weighted[0]], 
                    theta=radar_labels + [radar_labels[0]], 
                    fill="toself", 
                    fillcolor="rgba(0,119,182,0.12)", 
                    line=dict(color="#0077B6", width=2.5), 
                    name=top1["ev_name"]
                ))
                fig_r.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(16,42,67,0.12)", linecolor="rgba(16,42,67,0.12)", tickfont=dict(color="#52677A")),
                        angularaxis=dict(gridcolor="rgba(16,42,67,0.12)", linecolor="rgba(16,42,67,0.12)", tickfont=dict(color="#52677A"))
                    ),
                    showlegend=True, 
                    height=390, 
                    margin=dict(t=30, b=30, l=30, r=30), 
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(font=dict(color="#243044"))
                )
                st.plotly_chart(fig_r, use_container_width=True)

    with tab2:
        if "ahp_matrix" not in st.session_state:
            st.info("Atur preferensi di tab Preferensi & Rekomendasi terlebih dahulu.")
        else:
            criteria = st.session_state["criteria"]
            keys = st.session_state["criteria_keys"]
            mat = st.session_state["ahp_matrix"]
            weights = st.session_state["ahp_weights"]
            n = len(keys)

            st.markdown('<div class="section-title">Matriks Perbandingan Berpasangan AHP</div>', unsafe_allow_html=True)
            codes = [criteria[key]["code"] for key in keys]
            df_mat = pd.DataFrame(mat, index=[f"{c} ({criteria[k]['label']})" for c, k in zip(codes, keys)], columns=codes)
            st.dataframe(df_mat.style.format("{:.3f}").background_gradient(cmap="Blues"), use_container_width=True)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Eigenvalue Maks (λ max)", f"{st.session_state['ahp_lmax']:.4f}")
            col2.metric("Consistency Index (CI)", f"{st.session_state['ahp_ci']:.4f}")
            col3.metric("Random Consistency Index (RI)", f"{RI.get(n, 1.59):.2f}")
            col4.metric("Consistency Ratio (CR)", f"{st.session_state['ahp_cr']:.4f}")

            st.markdown('<div class="section-title">Vektor Prioritas Kriteria (Priority Vector)</div>', unsafe_allow_html=True)
            df_w = pd.DataFrame(
                {
                    "Kode": codes,
                    "Kriteria": [criteria[key]["label"] for key in keys],
                    "Tipe": [criteria[key]["type"].upper() for key in keys],
                    "Bobot": weights,
                    "Bobot (%)": weights * 100,
                }
            )
            st.dataframe(
                df_w.style.format({"Bobot": "{:.4f}", "Bobot (%)": "{:.2f}%"}).bar(
                    subset=["Bobot (%)"], color="#BFD7EA"
                ),
                use_container_width=True,
            )

            st.markdown('<div class="section-title">Matriks Ternormalisasi AHP</div>', unsafe_allow_html=True)
            norm_mat = mat / mat.sum(axis=0)
            df_norm = pd.DataFrame(norm_mat, index=codes, columns=codes)
            df_norm["Vektor Prioritas"] = weights
            st.dataframe(df_norm.style.format("{:.4f}"), use_container_width=True)

    with tab3:
        if "results" not in st.session_state:
            st.info("Atur preferensi di tab Preferensi & Rekomendasi terlebih dahulu.")
        else:
            results = st.session_state["results"]
            criteria = st.session_state["criteria"]
            keys = st.session_state["criteria_keys"]

            st.markdown('<div class="section-title">Tabel Lengkap Skor TOPSIS</div>', unsafe_allow_html=True)
            display_cols = ["rank", "ev_name"] + keys + ["topsis_score"]
            df_show = results[display_cols].copy()
            df_show.rename(
                columns={
                    "rank": "Rank",
                    "ev_name": "Kendaraan",
                    "topsis_score": "Skor TOPSIS",
                    **{key: criteria[key]["label"] for key in keys},
                },
                inplace=True,
            )
            st.dataframe(
                df_show.style.format({"Skor TOPSIS": "{:.4f}", **{criteria[k]["label"]: "{:.2f}" for k in keys if k not in ["battery_type", "fast_charge_port", "drivetrain", "segment", "car_body_type"]}}).background_gradient(
                    subset=["Skor TOPSIS"], cmap="Blues"
                ),
                use_container_width=True,
            )

            st.markdown('<div class="section-title">Distribusi Skor TOPSIS Seluruh EV</div>', unsafe_allow_html=True)
            fig_dist = px.histogram(
                results,
                x="topsis_score",
                nbins=40,
                color_discrete_sequence=["#0077B6"],
                labels={"topsis_score": "Skor TOPSIS"},
            )
            fig_dist.update_layout(
                height=280, margin=dict(t=10, b=0, l=0, r=0), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(gridcolor="rgba(16,42,67,0.10)", tickfont=dict(color="#52677A")),
                xaxis=dict(gridcolor="rgba(16,42,67,0.10)", tickfont=dict(color="#52677A"))
            )
            st.plotly_chart(fig_dist, use_container_width=True)

            st.markdown('<div class="section-title">Nilai Perbandingan Alternatif Top 10 per Indikator</div>', unsafe_allow_html=True)
            top10_long = results.head(10).melt(
                id_vars=["ev_name"], value_vars=keys, var_name="Indikator", value_name="Nilai"
            )
            top10_long["Indikator"] = top10_long["Indikator"].map(label_for)
            fig_values = px.bar(
                top10_long,
                x="ev_name",
                y="Nilai",
                color="Indikator",
                barmode="group",
                labels={"ev_name": "Kendaraan"},
            )
            fig_values.update_layout(
                height=420, xaxis_tickangle=-35, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(gridcolor="rgba(16,42,67,0.10)", tickfont=dict(color="#52677A")),
                xaxis=dict(tickfont=dict(color="#52677A")),
                legend=dict(font=dict(color="#243044"))
            )
            st.plotly_chart(fig_values, use_container_width=True)

    with tab4:
        st.markdown('<div class="section-title">Jumlah Model per Brand Kendaraan</div>', unsafe_allow_html=True)
        brand_counts = df["brand"].value_counts().reset_index()
        brand_counts.columns = ["Brand", "Jumlah"]
        fig_brand = px.bar(brand_counts, x="Brand", y="Jumlah", color="Jumlah", color_continuous_scale="Blues")
        fig_brand.update_layout(
            height=320, margin=dict(t=10, b=0, l=0, r=0), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-45,
            yaxis=dict(gridcolor="rgba(16,42,67,0.10)", tickfont=dict(color="#52677A")),
            xaxis=dict(tickfont=dict(color="#52677A"))
        )
        st.plotly_chart(fig_brand, use_container_width=True)

        st.markdown('<div class="section-title">Statistik Deskriptif Kriteria Numerik</div>', unsafe_allow_html=True)
        stats = df[all_indicators].describe().T[["count", "mean", "min", "max"]]
        stats.index = [label_for(key) for key in stats.index]
        st.dataframe(light_table_style(stats.style.format("{:.2f}")), use_container_width=True)

        st.markdown('<div class="section-title">Matriks Korelasi Antar Indikator</div>', unsafe_allow_html=True)
        corr = df[all_indicators].corr()
        fig_corr = go.Figure(
            go.Heatmap(
                z=corr.values,
                x=[label_for(key) for key in all_indicators],
                y=[label_for(key) for key in all_indicators],
                colorscale="RdBu",
                zmid=0,
                text=np.round(corr.values, 2),
                texttemplate="%{text}",
            )
        )
        fig_corr.update_layout(
            height=620, margin=dict(t=10, b=0, l=0, r=0),
            yaxis=dict(tickfont=dict(color="#243044")),
            xaxis=dict(tickfont=dict(color="#243044")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            x_axis = st.selectbox("Sumbu X Visualisasi Sebaran", all_indicators, index=all_indicators.index("range_km") if "range_km" in all_indicators else 0, format_func=label_for)
        with col_b:
            y_axis = st.selectbox(
                "Sumbu Y Visualisasi Sebaran",
                all_indicators,
                index=all_indicators.index("efficiency_wh_per_km") if "efficiency_wh_per_km" in all_indicators else min(1, len(all_indicators) - 1),
                format_func=label_for,
            )
        fig_sc = px.scatter(
            df,
            x=x_axis,
            y=y_axis,
            color="brand",
            hover_data=[col for col in ["ev_name", "segment_raw", "drivetrain_raw", "car_body_type_raw"] if col in df],
            labels={x_axis: label_for(x_axis), y_axis: label_for(y_axis)},
            opacity=0.75,
        )
        fig_sc.update_layout(
            height=420, showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="rgba(16,42,67,0.10)", tickfont=dict(color="#52677A")),
            xaxis=dict(gridcolor="rgba(16,42,67,0.10)", tickfont=dict(color="#52677A"))
        )
        st.plotly_chart(fig_sc, use_container_width=True)

if __name__ == "__main__":
    main()
