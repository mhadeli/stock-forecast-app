## The below block of code is writtent to improve the code on main.py file. This file is not used to run the app.
# ==============================================================================================================

import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go

# Set the title of the app
st.title('Stock Price Prediction')

# Define the start date and today's date for fetching data
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

# Define the list of stocks
stocks = ('SBIN.NS', 'TCS.NS', 'TECHM.NS', 'LT.NS', 'DMART.NS')
selected_stock = st.selectbox('Select dataset for prediction', stocks)

# Define the slider for selecting the number of years for prediction
n_years = st.slider('Years of prediction:', 1, 10)
period = n_years * 365 

# Cache the data loading function to improve performance
@st.cache_data
def load_data(ticker):
    try:
        data = yf.download(ticker, START, TODAY)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load data
data_load_state = st.text('Loading data...')
data = load_data(selected_stock)
if data is not None:
    data_load_state.text('Loading data... done!')
else:
    st.stop()

# Display raw data
st.subheader('Raw data')
st.write(data.tail())

# Plot raw data
def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="Stock Open"))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="Stock Close"))
    fig.layout.update(title_text='Time Series Data with Rangeslider', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

plot_raw_data()

# Prepare data for Prophet model
df_train = data[['Date', 'Close']].rename(columns={"Date": "ds", "Close": "y"})

# Train Prophet model
m = Prophet()
with st.spinner('Training model...'):
    try:
        m.fit(df_train)
    except Exception as e:
        st.error(f"Error training model: {e}")
        st.stop()

# Make future dataframe and predict
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

# Display forecast data
st.subheader('Forecast data')
st.write(forecast.tail())

# Plot forecast
st.write(f'Forecast plot for {n_years} years')
fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)

# Plot forecast components
st.write("Forecast components")
fig2 = m.plot_components(forecast)
st.write(fig2)
