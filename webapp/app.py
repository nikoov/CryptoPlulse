import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import glob
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="CryptoPulse Dashboard", page_icon="📈", layout="wide")

# Helper functions
def load_latest_current_prices():
    files = glob.glob('data/prices_current_*.json')
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return json.load(f)

def load_historical_prices(crypto_id):
    files = glob.glob(f'data/prices_historical_{crypto_id}_*.csv')
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return pd.read_csv(latest_file)

def load_sentiment_data():
    files = glob.glob('data/sentiment/reddit/sentiment_*.json')
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return json.load(f)

st.sidebar.title("CryptoPulse")
st.sidebar.markdown("---")
selected_page = st.sidebar.radio(
    "Navigation",
    ["Market Overview", "Price Analysis", "Historical Trends", "Sentiment Analysis"]
)

current_prices = load_latest_current_prices()
if current_prices is None:
    st.error("No price data available. Please run the data collector first.")
    st.stop()

if selected_page == "Market Overview":
    st.title("📊 Cryptocurrency Market Overview")
    col1, col2, col3 = st.columns(3)
    total_market_cap = sum(data.get('usd_market_cap', 0) for data in current_prices.values())
    total_volume = sum(data.get('usd_24h_vol', 0) for data in current_prices.values())
    avg_change = sum(data.get('usd_24h_change', 0) for data in current_prices.values()) / len(current_prices)
    with col1:
        st.metric("Total Market Cap", f"${total_market_cap:,.0f}")
    with col2:
        st.metric("24h Trading Volume", f"${total_volume:,.0f}")
    with col3:
        st.metric("Average 24h Change", f"{avg_change:.2f}%", delta=f"{avg_change:.2f}%")
    st.subheader("Price Overview")
    price_data = []
    for crypto_id, data in current_prices.items():
        price = data.get('usd', 0)
        change = data.get('usd_24h_change', 0)
        market_cap = data.get('usd_market_cap', 0)
        volume = data.get('usd_24h_vol', 0)
        price_data.append({
            "Cryptocurrency": crypto_id.title(),
            "Price (USD)": price,
            "24h Change": change,
            "Market Cap": market_cap,
            "24h Volume": volume
        })
    df = pd.DataFrame(price_data)
    styled_df = df.copy()
    numerical_changes = df["24h Change"].copy()
    styled_df["Price (USD)"] = styled_df["Price (USD)"].apply(lambda x: f"${x:,.2f}")
    styled_df["24h Change"] = styled_df["24h Change"].apply(lambda x: f"{x:.2f}%")
    styled_df["Market Cap"] = styled_df["Market Cap"].apply(lambda x: f"${x:,.0f}")
    styled_df["24h Volume"] = styled_df["24h Volume"].apply(lambda x: f"${x:,.0f}")
    st.dataframe(
        styled_df.style.background_gradient(
            subset=["24h Change"],
            cmap='RdYlGn',
            gmap=numerical_changes
        ),
        use_container_width=True
    )

elif selected_page == "Price Analysis":
    st.title("💹 Price Analysis")
    selected_crypto = st.selectbox(
        "Select Cryptocurrency",
        options=list(current_prices.keys()),
        format_func=lambda x: x.title()
    )
    historical_data = load_historical_prices(selected_crypto)
    if historical_data is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=historical_data['timestamp'] if 'timestamp' in historical_data else historical_data.index,
            y=historical_data['price'],
            name='Price',
            line=dict(color='#00ff88', width=2)
        ))
        fig.update_layout(
            title=f"{selected_crypto.title()} Price History",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        fig_volume = px.bar(
            historical_data,
            x='timestamp' if 'timestamp' in historical_data else historical_data.index,
            y='volume',
            title=f"{selected_crypto.title()} Trading Volume"
        )
        fig_volume.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_volume, use_container_width=True)

elif selected_page == "Historical Trends":
    st.title("📈 Historical Trends")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    selected_cryptos = st.multiselect(
        "Select Cryptocurrencies to Compare",
        options=list(current_prices.keys()),
        default=list(current_prices.keys())[:3],
        format_func=lambda x: x.title()
    )
    if selected_cryptos:
        fig = go.Figure()
        for crypto in selected_cryptos:
            historical_data = load_historical_prices(crypto)
            if historical_data is not None:
                first_price = historical_data['price'].iloc[0]
                normalized_prices = (historical_data['price'] - first_price) / first_price * 100
                fig.add_trace(go.Scatter(
                    x=historical_data['timestamp'] if 'timestamp' in historical_data else historical_data.index,
                    y=normalized_prices,
                    name=crypto.title(),
                    mode='lines'
                ))
        fig.update_layout(
            title="Comparative Price Performance (%)",
            xaxis_title="Date",
            yaxis_title="Price Change (%)",
            template="plotly_dark",
            height=600,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)

elif selected_page == "Sentiment Analysis":
    st.title("🎭 Sentiment Analysis")
    sentiment_data = load_sentiment_data()
    if sentiment_data is None:
        st.error("No sentiment data available. Please run the sentiment analyzer first.")
    else:
        crypto_sentiments = {}
        for post in sentiment_data:
            crypto_id = post.get('crypto_id', 'unknown')
            if crypto_id not in crypto_sentiments:
                crypto_sentiments[crypto_id] = []
            crypto_sentiments[crypto_id].append(post)
        selected_crypto = st.selectbox(
            "Select Cryptocurrency",
            options=list(crypto_sentiments.keys()),
            format_func=lambda x: x.title()
        )
        if selected_crypto:
            posts = crypto_sentiments[selected_crypto]
            st.subheader("Recent Posts and Sentiments")
            for post in posts:
                with st.expander(f"{post.get('title', 'No Title')}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("**Content:**")
                        st.write(post.get('text', ''))
                        st.write(f"**Posted in:** r/{post.get('subreddit', 'unknown')}")
                        st.write(f"**Score:** {post.get('score', 0)}")
                    with col2:
                        sentiment = post.get('sentiment_analysis', {'sentiment': 'neutral', 'confidence': 0.0})
                        sentiment_color = {
                            'positive': 'green',
                            'neutral': 'gray',
                            'negative': 'red'
                        }.get(sentiment['sentiment'], 'gray')
                        st.markdown(f"""
                            <div style='background-color: {sentiment_color}20; padding: 10px; border-radius: 5px;'>
                                <h4 style='color: {sentiment_color}; margin: 0;'>
                                    {sentiment['sentiment'].title()}
                                </h4>
                                <p style='margin: 5px 0;'>
                                    Confidence: {sentiment['confidence']:.2%}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown("---") 