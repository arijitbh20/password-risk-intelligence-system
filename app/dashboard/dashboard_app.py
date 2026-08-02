import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import Database

RISK_COLORS = {"LOW": "#00FFAA", "MEDIUM": "#FFC300", "HIGH": "#FF5733", "CRITICAL": "#8B0000"}


# Data loading

def load_data() -> pd.DataFrame:
    """Fetch all logs from the database as a DataFrame."""
    db = Database()
    df = pd.DataFrame(db.fetch_data())
    print(df.head())  # Debugging: Print the first few rows of the DataFrame
    db.conn.close()

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df

def metric_card(column, title: str, value) -> None:
    column.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Main dashboard

def main() -> None:
    st.set_page_config(page_title="Password Risk Analytics Dashboard", page_icon="🔐", layout="wide")
    st_autorefresh(interval=3500, key="datarefresh")

    st.markdown(
        """
        <style>
            body { background-color: #0E1117; color: #FAFAFA; }
            .metric-card {
                background: linear-gradient(135deg, #141E30, #243B55);
                padding: 20px; border-radius: 15px; text-align: center;
                box-shadow: 0px 0px 20px rgba(0,255,170,0.15);
            }
            .metric-title { font-size: 14px; opacity: 0.7; }
            .metric-value { font-size: 28px; font-weight: bold; margin-top: 5px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("🔐 Password Risk Analytics Dashboard")
    st.markdown("Real-Time Cybersecurity Risk Intelligence")

    df = load_data()
    if df.empty:
        st.warning("No data found.")
        st.stop()

    #  Sidebar filter 
    st.sidebar.header("Filters")
    risk_filter = st.sidebar.multiselect(
        "Risk Levels", options=df["risk_status"].unique(), default=df["risk_status"].unique()
    )
    df = df[df["risk_status"].isin(risk_filter)]

    #  KPI row 
    kpis = [
        ("Total Records", len(df)),
        ("Average Entropy", round(df["entropy"].mean(), 2)),
        ("Average Rule Score", round(df["score"].mean(), 2)),
        ("Total Breaches", int(df["breach_count"].sum())),
    ]
    columns = st.columns(4)
    for column, (title, value) in zip(columns, kpis):
        metric_card(column, title, value)

    st.divider()
    left, right = st.columns(2)

    #  Risk distribution pie 
    with left:
        st.subheader("📊 Risk Level Distribution")
        risk_counts = df.groupby("risk_status").size().reset_index(name="count")
        fig = px.pie(
            risk_counts, names="risk_status", values="count", hole=0.5,
            color="risk_status", color_discrete_map=RISK_COLORS,
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

        # Time series 
        st.subheader("📅 Use Over Time")
        time_df = df.set_index("timestamp").resample("D").size().reset_index(name="count")
        fig = px.line(time_df, x="timestamp", y="count", template="plotly_dark", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

    #  Rule score bar + correlation heatmap 
    with right:
        st.subheader("🧮 Rule Score Distribution")
        score_counts = df.groupby("score").size().reset_index(name="count")
        fig = px.bar(score_counts, x="score", y="count", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

        st.subheader("🔥 Correlation Matrix (Security Metrics)")
        corr_df = df[["entropy", "score", "breach_count"]].corr()
        fig = px.imshow(corr_df, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        st.divider()


if __name__ == "__main__":
    main()
