import sys
import os

from matplotlib.font_manager import weight_dict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
from Database import Database


def get_data() -> pd.DataFrame:
    database = Database()
    df = pd.DataFrame(database.fetch_data())
    database.conn.close()
    print(df)
    return df

#streamlit data visualization
def visualize():

    st_autorefresh(interval=3500, key="datarefresh")
    st.set_page_config(
        page_title="Password Risk Analytics Dashboard",
        page_icon="🔐",
        layout="wide"
    )
    # ------------------------------------------------
    # CUSTOM DARK CSS
    # ------------------------------------------------
    st.markdown("""
    <style>
        body {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .metric-card {
            background: linear-gradient(135deg, #141E30, #243B55);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0px 0px 20px rgba(0,255,170,0.15);
        }
        .metric-title {
            font-size: 14px;
            opacity: 0.7;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            margin-top: 5px;
        }
    </style>
    """, unsafe_allow_html=True)

    # ------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------
    def load_data():
        df = get_data()
        if df.empty:
            return df
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    df = load_data()

    st.title("🔐 Password Risk Analytics Dashboard")
    st.markdown("Real-Time Cybersecurity Risk Intelligence")

    if df.empty:
        st.warning("No data found.")
        st.stop()

    # ------------------------------------------------
    # SIDEBAR FILTERS
    # ------------------------------------------------
    st.sidebar.header("Filters")

    risk_filter = st.sidebar.multiselect(
        "Risk Levels",
        options=df["risk_status"].unique(),
        default=df["risk_status"].unique()
    )

    df = df[df["risk_status"].isin(risk_filter)]

    # ------------------------------------------------
    # KPI SECTION
    # ------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Records</div>
        <div class="metric-value">{len(df)}</div>
    </div>
    """, unsafe_allow_html=True)

    entropy = round(df["entropy"].mean(), 2)
    col2.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Average Entropy</div>
        <div class="metric-value">{entropy}</div>
    </div>
    """, unsafe_allow_html=True)

    score = round(df["score"].mean(), 2)
    col3.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Average Rule Score</div>
        <div class="metric-value">{score}</div>
    </div>
    """, unsafe_allow_html=True)

    breach_count = int(df["breach_count"].sum())
    col4.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Breaches</div>
        <div class="metric-value">{breach_count}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    col5,col6= st.columns([2,2])

    with col5:

        # ------------------------------------------------
        # RISK DISTRIBUTION PIE
        # ------------------------------------------------
        st.subheader("📊 Risk Level Distribution")

        risk_counts = df.groupby("risk_status").size().reset_index(name="count")

        fig_risk = px.pie(
            risk_counts,
            names="risk_status",
            values="count",
            hole=0.5,
            color="risk_status",
            color_discrete_map={
                "LOW": "#00FFAA",
                "MEDIUM": "#FFC300",
                "HIGH": "#FF5733",
                "CRITICAL": "#8B0000"
            }
        )
        fig_risk.update_layout(template="plotly_dark",legend=dict(font=dict(size=16)))
        fig_risk.update_traces(textfont_size=18,insidetextfont_color="black",textposition='outside',textfont_weight='bold')
        st.plotly_chart(fig_risk, use_container_width=True)
        st.divider()


        # ------------------------------------------------
        # TIME SERIES ANALYSIS
        # ------------------------------------------------
        st.subheader("📅 Use Over Time")

        time_df = df.set_index("timestamp").resample("D").size().reset_index(name="count")

        fig_time = px.line(
            time_df,
            x="timestamp",
            y="count",
            template="plotly_dark",
            markers=True  # optional but makes it cleaner
        )

        fig_time.update_layout(
            xaxis=dict(
                title=dict(text="Date", font=dict(size=20)),
                tickfont=dict(size=14)
            ),
            yaxis=dict(
                title=dict(text="Number of Evaluations", font=dict(size=20)),
                tickfont=dict(size=14)
            ),
            legend=dict(font=dict(size=16))
        )

        fig_time.update_traces(
            line=dict(width=3)  # thicker line = more professional
        )

        st.plotly_chart(fig_time, use_container_width=True)
        st.divider()

    with (col6):
        # ------------------------------------------------
        # RULE SCORE DISTRIBUTION
        # ------------------------------------------------
        st.subheader("🧮 Rule Score Distribution")

        score_counts = df.groupby("score").size().reset_index(name="count")

        fig_score = px.bar(
            score_counts,
            x="score",
            y="count",
            template="plotly_dark",
        )
        fig_score.update_layout(
            xaxis=dict(
                title=dict(font=dict(size=20)),
                tickfont=dict(size=18)
            ),
            yaxis=dict(
                title=dict(font=dict(size=20)),
                tickfont=dict(size=18)
            ),
            font=dict(size=18))

        st.plotly_chart(fig_score, use_container_width=True)
        st.divider()

        # ------------------------------------------------
        # CORRELATION HEATMAP
        # ------------------------------------------------
        st.subheader("🔥 Correlation Matrix (Security Metrics)")

        # Select numeric columns only
        corr_df = df[["entropy", "score", "breach_count"]].corr()

        fig_heatmap = px.imshow(
            corr_df,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            template="plotly_dark"
        )
        fig_heatmap.update_layout(
            xaxis=dict(
                title=dict(font=dict(size=20)),
                tickfont=dict(size=18)
            ),
            yaxis=dict(
                title=dict(font=dict(size=20)),
                tickfont=dict(size=18)
            ),
            font=dict(size=18),coloraxis_colorbar=dict(title="Correlation"))

        st.plotly_chart(fig_heatmap, use_container_width=True)
        st.divider()

visualize()







