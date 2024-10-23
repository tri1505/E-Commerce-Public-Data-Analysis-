import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import matplotlib.ticker as mtick
import datetime as dt
sns.set(style='dark')

# menyiapkan data all_data
all_df = pd.read_csv('streamlit_data.csv')

# menyiapkan produk yang paling banyak dan sedikit dijual
def create_product_count_df(df):
    product_counts = df.groupby('product_category_name_english')['product_id'].count().reset_index()
    sorted_df = product_counts.sort_values(by='product_id', ascending=False)
    return sorted_df

# menyiapkan tingkat kepuasan pembeli
def create_rating_service(df):
    rating_service = df['review_score'].value_counts().sort_values(ascending=False)
    max_score = rating_service.idxmax()
    return (rating_service, max_score)

# menyiapkan kota yang memiliki seller dan customer paling banyak
def create_city_customer_df(df):
    city_customer = all_df.customer_city.value_counts().sort_values(ascending=False).rename_axis('City').reset_index(name='Number of Customers') 
    return city_customer
def create_city_seller_df(df):
    city_seller = all_df.seller_city.value_counts().sort_values(ascending=False).rename_axis('City').reset_index(name='Number of Sellers')
    return city_seller

# menyiapkan metode pembayaran
def create_total_payment_type(df):
    total_payment_type = all_df.groupby('payment_type')['payment_value'].sum().reset_index()
    return total_payment_type

# menyiapkan RFM
def create_rfm_df(df):
    today=dt.datetime(2018,10,20)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    recency = (today - df.groupby('customer_id')['order_purchase_timestamp'].max()).dt.days
    frequency = df.groupby('customer_id')['order_id'].count()
    monetary = df.groupby('customer_id')['price'].sum()

    rfm_df = pd.DataFrame({
        'customer_id': recency.index,
        'Recency': recency.values,
        'Frequency': frequency.values,
        'Monetary': monetary.values
    })

    column_list = ['customer_id','Recency','Frequency','Monetary']
    rfm_df.columns = column_list
    return rfm_df

# menyiapkan komponen filter
min_date = pd.to_datetime(all_df['order_approved_at']).dt.date.min()
max_date = pd.to_datetime(all_df['order_approved_at']).dt.date.max()

# menyiapkan side bar
st.title("Dashboard E-Commerce created by : Tri Ramdhany")
with st.sidebar: 
    st.image('logo.png')
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Time Span',
        min_value= min_date,
        max_value= max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) &
                (all_df["order_approved_at"] <= str(end_date))]

# menyiapkan berbagai dataframe
product_count_df = create_product_count_df(main_df)
rating_service_df,max_score = create_rating_service(main_df)
city_customer_df = create_city_customer_df(main_df)
city_seller_df = create_city_seller_df(main_df)
total_payment_type_df = create_total_payment_type(main_df)
rfm_df = create_rfm_df(main_df)




# Membuat dashboard secara lengkap


# Membuat produk yang paling banyak dan sedikit terjual
st.header('Most & Least Product')
col1, col2 = st.columns(2)
with col1:
    most = product_count_df['product_id'].max()
    st.metric('Highest orders', value=most)
with col2:
    low = product_count_df['product_id'].min()
    st.metric('Lowest Order', value=low )

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_id", y="product_category_name_english", hue="product_category_name_english", data=product_count_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=35)
ax[0].set_title("Products with the highest sales", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)

sns.barplot(x="product_id", y="product_category_name_english", hue="product_category_name_english", data=product_count_df.sort_values(by="product_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=35)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Products with the lowest sales", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)

plt.suptitle("Most and Least Sold Products", fontsize=58)
st.pyplot(fig)

# Membuat tingkat kepuasan pelanggan
st.header("Rating Customer By Service")
plt.figure(figsize=(16, 8))
sns.barplot(
            x=rating_service_df.index, 
            y=rating_service_df.values, 
            order=rating_service_df.index,
            palette=["#90CAF9" if score == max_score else "#D3D3D3" for score in rating_service_df.index],
            )

plt.title("Rating customers for service", fontsize=30)
plt.xlabel("Rating", fontsize=18)
plt.ylabel("Customer", fontsize=18)
plt.xticks(fontsize=15)
st.pyplot(plt)

# Membuat kota dengan customer & seller terbanyak
st.header('City With Most Customers and Sellers.')
tab1, tab2 = st.tabs(['Customer', 'Sellers'])
with tab1:
    st.subheader('Most Customers City')
    top_5_cities_customer = city_customer_df.head(5)
    plt.figure(figsize=(10, 6))
    colors = ["#72BCD4" if city == top_5_cities_customer['City'].iloc[0] else "#D3D3D3" for city in top_5_cities_customer['City']]
    sns.barplot(x="Number of Customers", y="City", data=top_5_cities_customer, hue=top_5_cities_customer['City'], palette=colors, legend=False)
    plt.xlabel('Number of Customers')
    plt.ylabel('City')
    plt.title('Top 5 Cities with the Most Customers', fontsize=20)
    st.pyplot(plt)
with tab2:
    st.subheader('Most Sellers City')
    top_5_cities = city_seller_df.head(5)
    plt.figure(figsize=(10, 6))
    colors = ["#72BCD4" if city == top_5_cities['City'].iloc[0] else "#D3D3D3" for city in top_5_cities['City']]
    sns.barplot(x="Number of Sellers", y="City", data=top_5_cities, hue=top_5_cities['City'], palette=colors, legend=False)
    plt.xlabel('Number of Sellers')
    plt.ylabel('City')
    plt.title('Top 5 Cities with the Most Sellers', fontsize=20)
    st.pyplot(plt)

# Membuat metode pembayaran
st.header('Payment Value by Type')
total_payment_type_df['payment_value_million'] = total_payment_type_df['payment_value'] / 1e6
plt.figure(figsize=(10, 6))
sns.barplot(x="payment_type", y="payment_value_million", data=total_payment_type_df, palette="Blues_d")
plt.xlabel('Payment Type')
plt.ylabel('Total Payment Value (Million)')
plt.title('Total Payment Value by Payment Type', fontsize=20)
fmt = '{x:,.0f}M'
tick = mtick.StrMethodFormatter(fmt)
plt.gca().yaxis.set_major_formatter(tick)
st.pyplot(plt)

# Membuat RFM
st.header("RFM Best Value")
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 10))
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

# Visualisasi berdasarkan Recency
sns.barplot(y="Recency", x="customer_id", data=rfm_df.sort_values(by="Recency", ascending=True).head(5), ax=ax[0], color=colors[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id")
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)
ax[0].set_xticks([])

# Visualisasi berdasarkan Frequency
sns.barplot(y="Frequency", x="customer_id", data=rfm_df.sort_values(by="Frequency", ascending=False).head(5), ax=ax[1], color=colors[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel('customer_id')
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)
ax[1].set_xticks([])

# Visualisasi berdasarkan Monetary
sns.barplot(y="Monetary", x="customer_id", data=rfm_df.sort_values(by="Monetary", ascending=False).head(5), ax=ax[2], color=colors[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel('customer_id')
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)
ax[2].set_xticks([])

plt.suptitle("Best Customer Based on RFM Parameters (customer_id)", fontsize=20)
st.pyplot(plt)