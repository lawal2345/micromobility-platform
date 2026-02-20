import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_URL = "https://micromobility-api-115910154602.europe-west2.run.app"

st.set_page_config(
    page_title="MobiCommand — Toyota Micro-Mobility",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    font-size: 16px;
}

section[data-testid="stSidebar"] {
    background-color: #0D0D14;
    border-right: 1px solid #1E1E2E;
}

section[data-testid="stSidebar"] .stSelectbox label {
    color: #9999BB;
    font-size: 13px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

[data-testid="metric-container"] {
    background: #13131A;
    border: 1px solid #1E1E2E;
    border-top: 2px solid #00D4FF;
    padding: 20px 24px;
    border-radius: 2px;
}

[data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 2.4rem !important;
    color: #00D4FF !important;
}

[data-testid="stMetricLabel"] {
    font-size: 13px !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #9999BB !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #1E1E2E;
}

h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2.2rem !important;
    letter-spacing: -0.02em;
    color: #E8E8F0 !important;
    border-bottom: 1px solid #1E1E2E;
    padding-bottom: 16px;
    margin-bottom: 32px !important;
}

.sidebar-logo {
    font-family: 'Space Mono', monospace;
    font-size: 14px;
    color: #00D4FF;
    letter-spacing: 0.1em;
    padding: 8px 0 32px 0;
    border-bottom: 1px solid #1E1E2E;
    margin-bottom: 24px;
}

.sidebar-logo span {
    color: #9999BB;
    font-size: 11px;
    display: block;
    margin-top: 4px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        MOBICOMMAND
        <span>University of Derby</span>
    </div>
    """, unsafe_allow_html=True)

    page = st.selectbox("SECTION", [
        "Overview",
        "Vehicles",
        "Trips",
        "Demand Analytics"
    ])

# ── Page 1: Overview ──────────────────────────────────────────────────────────
if page == "Overview":
    st.title("Platform Overview")

    data = requests.get(f"{API_URL}/analytics/summary").json()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trips", f"{data['total_trips']:,}")
    col2.metric("Avg Duration", f"{data['avg_duration_minutes']} min")
    col3.metric("Avg Speed", f"{data['avg_speed_kmh']} km/h")
    col4.metric("Avg Battery Used", f"{data['avg_battery_consumed_pct']}%")

    st.markdown("<br>", unsafe_allow_html=True)

    vehicles = requests.get(f"{API_URL}/vehicles").json()
    df_v = pd.DataFrame(vehicles)
    type_counts = df_v["vehicle_type"].value_counts().reset_index()
    type_counts.columns = ["vehicle_type", "count"]

    fig = go.Figure(go.Pie(
        labels=type_counts["vehicle_type"],
        values=type_counts["count"],
        hole=0.6,
        marker=dict(colors=["#00D4FF", "#0066FF"]),
        textfont=dict(family="Space Mono", size=14, color="#E8E8F0")
    ))
    fig.update_layout(
        title="Fleet Composition",
        paper_bgcolor="#0A0A0F",
        plot_bgcolor="#0A0A0F",
        font=dict(family="Space Mono", color="#9999BB", size=13),
        title_font=dict(family="Syne", color="#E8E8F0", size=18),
        legend=dict(font=dict(color="#E8E8F0", size=13)),
        margin=dict(t=48, b=40, l=40, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Page 2: Vehicles ──────────────────────────────────────────────────────────
elif page == "Vehicles":
    st.title("Fleet Status")

    data = requests.get(f"{API_URL}/vehicles").json()
    df = pd.DataFrame(data)

    total = len(df)
    scooters = len(df[df["vehicle_type"] == "e-scooter"])
    bikes = len(df[df["vehicle_type"] == "e-bike"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Vehicles", total)
    c2.metric("E-Scooters", scooters)
    c3.metric("E-Bikes", bikes)

    st.markdown("<br>", unsafe_allow_html=True)

    fig = px.histogram(
        df, x="current_battery_pct", nbins=20,
        title="Battery Level Distribution",
        labels={"current_battery_pct": "Battery (%)"},
        color_discrete_sequence=["#00D4FF"]
    )
    fig.update_layout(
        paper_bgcolor="#0A0A0F",
        plot_bgcolor="#0A0A0F",
        font=dict(family="Space Mono", color="#9999BB", size=13),
        title_font=dict(family="Syne", color="#E8E8F0", size=18),
        bargap=0.05,
        margin=dict(t=48, b=40, l=40, r=20),
        xaxis=dict(gridcolor="#1E1E2E"),
        yaxis=dict(gridcolor="#1E1E2E")
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True, hide_index=True)

# ── Page 3: Trips ─────────────────────────────────────────────────────────────
elif page == "Trips":
    st.title("Trip History")

    data = requests.get(f"{API_URL}/trips").json()
    df = pd.DataFrame(data)

    c1, c2, c3 = st.columns(3)
    c1.metric("Trips Shown", len(df))
    c2.metric("Avg Duration", f"{round(df['duration_minutes'].mean(), 1)} min")
    c3.metric("Avg Speed", f"{round(df['avg_speed_kmh'].mean(), 1)} km/h")

    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── Page 4: Demand Analytics ──────────────────────────────────────────────────
elif page == "Demand Analytics":
    st.title("Demand Analytics")

    data = requests.get(f"{API_URL}/analytics/demand").json()
    df = pd.DataFrame(data)
    df["hour_label"] = df["hour_of_day"].apply(lambda h: f"{int(h):02d}:00")

    peak_hour = df.loc[df["trip_count"].idxmax(), "hour_of_day"]
    peak_trips = df["trip_count"].max()
    total_trips = df["trip_count"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Peak Hour", f"{int(peak_hour):02d}:00")
    c2.metric("Peak Trips", peak_trips)
    c3.metric("Total Trips", f"{total_trips:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["hour_label"],
        y=df["trip_count"],
        marker=dict(
            color=df["trip_count"],
            colorscale=[[0, "#1E1E2E"], [1, "#00D4FF"]],
            line_width=0
        )
    ))
    fig.update_layout(
        title="Trips by Hour of Day",
        paper_bgcolor="#0A0A0F",
        plot_bgcolor="#0A0A0F",
        font=dict(family="Space Mono", color="#9999BB", size=13),
        title_font=dict(family="Syne", color="#E8E8F0", size=18),
        xaxis=dict(title="Hour", gridcolor="#1E1E2E", type="category"),
        yaxis=dict(title="Trips", gridcolor="#1E1E2E"),
        margin=dict(t=48, b=40, l=40, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("More hours will appear as data is collected across the day.")