import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import streamlit as st
import pandas as pd
import data

st.title("Dashboard E-Commerce created by : Tri Ramdhany")
with st.sidebar: 
    st.image('logo.png')

min_date = pd.to_datetime("2016-09-04")
max_date = pd.to_datetime("2018-10-17")

dataset_base_path = "E-Commerce Public Dataset/"
df_dict: dict[str, pd.DataFrame] = {}
with st.sidebar:
    try:
        start_date, end_date = st.date_input(
            label="Date Range (Order Purchase Date)",
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date],
        )
    except ValueError:
        st.error("Invalid Date Input")
        st.stop()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Total Orders")
    st.write(f"{data.get_total_orders(start_date, end_date)}")
with col2:
    st.subheader("Total Revenue")
    st.write(f"{round(data.get_total_revenue(start_date, end_date), 2)} USD")

st.plotly_chart(
    data.get_top_5_products(start_date, end_date), use_container_width=True
)

st.plotly_chart(
    data.get_purchase_history(start_date, end_date), use_container_width=True
)

st.plotly_chart(
    data.get_customer_chart(start_date, end_date), use_container_width=True
)

fig_freq, fig_monetary, fig_recency = data.get_rfm_chart(start_date, end_date)
rfm1, rfm2, rfm3 = st.tabs(["Frequency", "Monetary", "Recency"])
with rfm1:
    st.plotly_chart(fig_freq, use_container_width=True)
with rfm2:
    st.plotly_chart(fig_monetary, use_container_width=True)
with rfm3:
    st.plotly_chart(fig_recency, use_container_width=True)



