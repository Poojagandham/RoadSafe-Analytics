import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="RoadSafe Analytics Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    file_path = r'D:\RoadSafe_Analytics\data\US_Accidents_Cleaned_Final.csv'
    df = pd.read_csv(file_path)

    df['Start_Time'] = pd.to_datetime(df['Start_Time'], errors='coerce')
    df['Date'] = df['Start_Time'].dt.date
    df['Hour'] = df['Start_Time'].dt.hour
    df['Weekday'] = df['Start_Time'].dt.day_name()

    # ====== VISIBILITY CATEGORY ======
    if 'Visibility(mi)' in df.columns:
        df['Visibility(mi)'] = pd.to_numeric(df['Visibility(mi)'], errors='coerce')
        df['Visibility_Level'] = df['Visibility(mi)'].apply(
            lambda x: 'Clear' if pd.notnull(x) and x >= 5 else 'Unclear'
        )
    else:
        df['Visibility_Level'] = 'Unknown'

    # ====== ROAD CONDITION CATEGORY ======
    def road_condition(row):
        if 'Junction' in df.columns and row.get('Junction') == True:
            return 'Junction'
        elif 'Crossing' in df.columns and row.get('Crossing') == True:
            return 'Crossing'
        elif 'Roundabout' in df.columns and row.get('Roundabout') == True:
            return 'Roundabout'
        elif 'Bump' in df.columns and row.get('Bump') == True:
            return 'Bump'
        else:
            return 'Straight Road'

    df['Road_Condition'] = df.apply(road_condition, axis=1)

    df = df.dropna(subset=[
        'Start_Lat','Start_Lng','Severity',
        'State','Weather_Condition','Date'
    ])

    return df

df = load_data()

# ====================== SIDEBAR NAVIGATION ======================
st.sidebar.title("🎛️ Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📊 Dashboard"])

# -------- DEFAULTS --------
start_date = df['Date'].min()
end_date = df['Date'].max()
filtered_df = df.copy()

# ============================================================
# ================= DASHBOARD FILTERS (ONLY DASHBOARD) =======
# ============================================================
if page == "📊 Dashboard":

    st.sidebar.markdown("---")
    st.sidebar.title("🎛️ Dashboard Filters")

    # ---- STATE FILTER ----
    states = sorted(df['State'].unique())
    selected_states = st.sidebar.multiselect(
        "📍 Select State(s)",
        states,
        default=states
    )

    st.sidebar.markdown("---")

    # ---- WEATHER FILTER ----
    weather_options = sorted(df['Weather_Condition'].dropna().unique())
    selected_weather = st.sidebar.multiselect(
        "☁️ Weather Condition",
        weather_options,
        default=weather_options
    )

    st.sidebar.markdown("---")

    # ---- SEVERITY FILTER ----
    severity_levels = sorted(df['Severity'].unique())
    selected_severity = st.sidebar.multiselect(
        "⚠️ Severity Level",
        severity_levels,
        default=severity_levels
    )

    st.sidebar.markdown("---")

    # ---- VISIBILITY FILTER ----
    visibility_options = ['Clear', 'Unclear']
    selected_visibility = st.sidebar.multiselect(
        "👁️ Visibility",
        visibility_options,
        default=visibility_options
    )

    st.sidebar.markdown("---")

    # ---- ROAD CONDITION FILTER ----
    road_options = sorted(df['Road_Condition'].unique())
    selected_road = st.sidebar.multiselect(
        "🛣️ Road Condition",
        road_options,
        default=road_options
    )

    st.sidebar.markdown("---")

    # ---- DATE FILTER ----
    selected_date_range = st.sidebar.date_input(
        "📅 Date Range",
        value=(start_date, end_date),
        min_value=start_date,
        max_value=end_date
    )

    # -------- SMART FILTER LOGIC --------
    if isinstance(selected_date_range, tuple):
        start_date, end_date = selected_date_range

        mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)

        if set(selected_states) != set(states):
            mask &= df['State'].isin(selected_states)

        if set(selected_weather) != set(weather_options):
            mask &= df['Weather_Condition'].isin(selected_weather)

        if set(selected_severity) != set(severity_levels):
            mask &= df['Severity'].isin(selected_severity)

        if set(selected_visibility) != set(visibility_options):
            mask &= df['Visibility_Level'].isin(selected_visibility)

        if set(selected_road) != set(road_options):
            mask &= df['Road_Condition'].isin(selected_road)

        filtered_df = df[mask]

# ============================================================
# ============================ HOME ==========================
# ============================================================
if page == "🏠 Home":

    st.subheader("🚦 Project: RoadSafe Analytics")
    st.markdown("---")

    st.header("📘 Project Overview")
    st.markdown("""
    **RoadSafe Analytics** analyzes road accident patterns across the United States.
    """)

    st.success(f"✅ Total Records: **{len(df):,}**")
    st.markdown("---")

    col_map, col_stats = st.columns([2.2, 1])

    with col_map:
        st.subheader("📍 Accident Hotspot Map")
        sample = df.sample(n=min(20000, len(df)))
        fig = px.scatter_map(
            sample, lat="Start_Lat", lon="Start_Lng",
            color="Severity", zoom=3,
            map_style="carto-positron"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_stats:
        st.subheader("⚠️ Severity Statistics")
        st.metric("Total Accidents", f"{len(df):,}")
        st.metric("Fatal (4)", f"{len(df[df['Severity']==4]):,}")
        st.metric("Severe (3)", f"{len(df[df['Severity']==3]):,}")
        st.metric("Slight (2)", f"{len(df[df['Severity']==2]):,}")

# ============================================================
# ========================= DASHBOARD ========================
# ============================================================
else:

    st.title("🚦 ROADSAFE ANALYTICS DASHBOARD")
    st.write(f"Analyzing data from **{start_date} to {end_date}**")
    st.markdown("---")

    # KPIs (UNCHANGED)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Accidents", f"{len(filtered_df):,}")
    c2.metric("Fatal (4)", f"{len(filtered_df[filtered_df['Severity']==4]):,}")
    c3.metric("Severe (3)", f"{len(filtered_df[filtered_df['Severity']==3]):,}")
    c4.metric("Slight (2)", f"{len(filtered_df[filtered_df['Severity']==2]):,}")

    st.markdown("---")

    # ================= MAP + PIE (UNCHANGED) =================
    col_map, col_side = st.columns([2.2, 1])

    with col_map:
        st.subheader("📍 Accident Hotspots Map")
        if not filtered_df.empty:
            sample = filtered_df.sample(n=min(20000, len(filtered_df)))
            fig = px.scatter_map(
                sample, lat="Start_Lat", lon="Start_Lng",
                color="Severity", zoom=3,
                map_style="carto-positron"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_side:
        st.subheader("📊 Severity Distribution")
        if not filtered_df.empty:
            fig = px.pie(filtered_df, names="Severity")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ============================================================
    # TIME & SEVERITY ANALYSIS (CLEAN TITLES)
    # ============================================================

    st.subheader("⏱️ Accident Patterns Over Time")

    st.markdown("### 📈 Accident Frequency by Hour")
    hourly_counts = filtered_df['Hour'].value_counts().sort_index().reset_index()
    hourly_counts.columns = ["Hour","Accidents"]

    fig1 = px.line(hourly_counts, x="Hour", y="Accidents")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### ⚠️ Severity by Hour")
    sev_hour = filtered_df.groupby(['Hour','Severity']).size().reset_index(name='Count')

    fig2 = px.area(
        sev_hour,
        x="Hour",
        y="Count",
        color="Severity"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ============================================================
    # ENVIRONMENT & INFRASTRUCTURE ANALYSIS (CLEAN TITLES)
    # ============================================================

    st.subheader("🌍 Road & Environment Analysis")

    st.markdown("### 🛣️ Road Features vs Accidents")
    road_counts = filtered_df['Road_Condition'].value_counts().reset_index()
    road_counts.columns = ["Road_Feature","Accidents"]

    fig3 = px.bar(road_counts, x="Road_Feature", y="Accidents")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### 🌦️ Weather Impact (Top 5 Conditions)")
    weather_counts = filtered_df['Weather_Condition'].value_counts().head(5).reset_index()
    weather_counts.columns = ["Weather","Accidents"]

    fig4 = px.bar(weather_counts, x="Weather", y="Accidents")
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # ============================================================
    # GEOSPATIAL FINGERPRINT (CLEAN TITLE)
    # ============================================================

    st.subheader("🗺️ National Accident Hotspots (Geospatial Fingerprint)")

    fig5 = px.scatter_map(
        filtered_df,
        lat="Start_Lat",
        lon="Start_Lng",
        color="Severity",
        zoom=3,
        opacity=0.3,
        map_style="carto-positron"
    )

    st.plotly_chart(fig5, use_container_width=True)

st.success("Dashboard Loaded Successfully!")
