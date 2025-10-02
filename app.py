import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="📈 Stock Big Move Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("⚙️ Settings")

uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

default_ticker = st.sidebar.text_input("Stock Ticker Symbol", "AAPL")
big_move_threshold = st.sidebar.slider(
    "Big Move Threshold (%)", min_value=5, max_value=50, value=15, step=1
)

st.sidebar.markdown("---")
st.sidebar.info("Upload stock price data (CSV) with Date & Close columns.")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values("Date").reset_index(drop=True)
    return df

if uploaded_file:
    df = load_data(uploaded_file)
else:
    df = pd.read_csv("data/AAPL_sample.csv")
    df['Date'] = pd.to_datetime(df['Date'])

# -----------------------------
# Detect Big Moves
# -----------------------------
def detect_big_moves(df, threshold):
    moves = []
    for i in range(1, len(df)):
        pct_change = (df['Close'][i] - df['Close'][i-1]) / df['Close'][i-1] * 100
        if abs(pct_change) >= threshold:
            moves.append({
                "Date": df['Date'][i],
                "Price": df['Close'][i],
                "PctChange": pct_change,
                "Type": "Upside" if pct_change > 0 else "Downside"
            })
    return pd.DataFrame(moves)

big_moves_df = detect_big_moves(df, big_move_threshold)

# -----------------------------
# Dashboard Layout
# -----------------------------
st.title(f"📊 Big Move Analyzer for {default_ticker}")

tab1, tab2, tab3 = st.tabs(["📈 Price Chart", "📋 Big Moves Table", "📊 Statistics"])

# --- Tab 1: Chart ---
with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], mode="lines", name="Close Price"))
    if not big_moves_df.empty:
        fig.add_trace(go.Scatter(
            x=big_moves_df["Date"], y=big_moves_df["Price"],
            mode="markers", name="Big Moves",
            marker=dict(size=10, color=np.where(big_moves_df["Type"]=="Upside","green","red"))
        ))
    fig.update_layout(title="Stock Price with Big Moves", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Table ---
with tab2:
    st.subheader("📋 Detected Big Moves")
    st.dataframe(big_moves_df, use_container_width=True)

# --- Tab 3: Stats ---
with tab3:
    st.subheader("📊 Summary Statistics")
    total_moves = len(big_moves_df)
    upside_moves = len(big_moves_df[big_moves_df["Type"] == "Upside"])
    downside_moves = len(big_moves_df[big_moves_df["Type"] == "Downside"])
    st.metric("Total Big Moves", total_moves)
    st.metric("Upside Moves", upside_moves)
    st.metric("Downside Moves", downside_moves)

    if not big_moves_df.empty:
        fig2 = px.histogram(big_moves_df, x="PctChange", color="Type", nbins=20,
                            title="Distribution of Big Moves (%)")
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.caption("🚀 Built with Streamlit | Ahmed’s Stock Analyzer")
