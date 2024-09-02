import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go
import plotly.express as px

# Database configuration
db_host = 'localhost'
db_name = 'postgres'
db_user = 'postgres'
db_password = 'houssem'

# Create the database connection URL
db_url = f"postgresql://{db_user}:{db_password}@{db_host}:5433/{db_name}"

# Create a database connection
engine = create_engine(db_url)

# Query the database
query = "SELECT * FROM gold_prices;"  
try:
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)  
except Exception as e:
    st.error(f"Error connecting to the database: {e}")

# Create the Streamlit app layout
st.set_page_config(page_title="Gold Price Dashboard", layout="wide")
st.title("Real-Time Gold Price Dashboard")

# Create two columns for the dashboard
col1, col2 = st.columns([0.4, 0.6])

def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['current_price'], name="Current Price"))
    fig.layout.update(title_text='Time Series Data with Rangefinder', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

# Display the current gold price
with col1:
    st.subheader("Current Gold Price")
    
    # Ensure we are working with the latest price and change
    current_price = df['current_price'].iloc[-1]  # Get the latest price
    percent_change = df["price_change"].iloc[-1]  # Get the latest price change

    # Display the current price and percentage change
    delta = "▲" if percent_change >= 0 else "▼"
    st.metric(label="Gold Price (USD)", value=f"${current_price:.2f}", delta=f"{abs(percent_change):.2f}% {delta}")

    # Display the raw data
    st.subheader('Raw Data')
    if st.checkbox("Preview"):
        st.dataframe(df)

# Plot the gold price chart
with col2:
    st.subheader("Gold Price Chart")
    fig = px.line(df, x=df['time'], y="current_price", title="Gold Price Over Time")
    st.plotly_chart(fig, use_container_width=True)

    plot_raw_data()