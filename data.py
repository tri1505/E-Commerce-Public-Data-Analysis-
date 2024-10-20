from plotly import graph_objects as go
import plotly.express as px
import pandas as pd


def get_dataframe(min_date, max_date) -> pd.DataFrame:
    all_df = pd.read_csv("streamlit_data.csv")

    order_approved_date = pd.to_datetime(all_df["order_approved_at"]).dt.date

    all_df = all_df[
        (order_approved_date >= min_date) & (order_approved_date <= max_date)
    ]

    return all_df


def get_total_orders(min_date, max_date):
    all_df = get_dataframe(min_date, max_date)
    total_orders = all_df.groupby("order_id").size().count()
    return total_orders


def get_total_revenue(min_date, max_date):
    all_df = get_dataframe(min_date, max_date)
    total_revenue = all_df.groupby("order_id")["payment_value"].sum().sum()
    return total_revenue


def get_top_5_products(min_date, max_date):
    all_df = get_dataframe(min_date, max_date)

    product_sold_df = (
        all_df.groupby("product_category_name_english")["order_item_id"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    product_sold_df.rename(
        columns={
            "product_category_name_english": "product_name",
            "order_item_id": "total_sold",
        },
        inplace=True,
    )

    top_5_high = product_sold_df.head()
    top_5_low = product_sold_df.tail()

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=top_5_high["total_sold"],
            y=top_5_high["product_name"],
            orientation="h",
            name="Top 5 Highest Sold",
            marker=dict(color="skyblue"),
        )
    )

    fig.add_trace(
        go.Bar(
            x=top_5_low["total_sold"],
            y=top_5_low["product_name"],
            orientation="h",
            name="Top 5 Lowest Sold",
            marker=dict(color="salmon"),
        )
    )

    fig.update_layout(
        title="Top 5 Highest and Lowest Sold Products",
        xaxis=dict(title="Total Sold"),
        yaxis=dict(title="Product Name"),
        barmode="group",
    )

    return fig


def get_purchase_history(min_date, max_date):
    all_df = get_dataframe(min_date, max_date)

    all_df["order_purchase_timestamp"] = pd.to_datetime(
        all_df["order_purchase_timestamp"]
    ).dt.strftime("%Y-%m-%d")

    grouped_data = (
        all_df.groupby("order_purchase_timestamp")["order_id"].count().reset_index()
    )
    grouped_data.rename(columns={"order_id": "total_order"}, inplace=True)

    fig = px.line(
        grouped_data,
        x="order_purchase_timestamp",
        y="total_order",
        title="Number of Orders Over Time",
    )
    return fig


def get_customer_chart(min_date, max_date):
    all_df = get_dataframe(min_date, max_date)

    customer_state_df = (
        all_df.groupby(by="customer_state")["customer_id"].nunique().reset_index()
    )
    customer_state_df.rename(columns={"customer_id": "total_customer"}, inplace=True)

    customer_state_df_sorted = customer_state_df.sort_values(
        by="total_customer", ascending=False
    )
    top_5_states = customer_state_df_sorted.head(5)
    other_states_count = customer_state_df.iloc[5:]
    others_total = other_states_count["total_customer"].sum()
    top_5_states = pd.concat(
        [
            top_5_states,
            pd.DataFrame(
                {"customer_state": ["Others"], "total_customer": [others_total]}
            ),
        ]
    )
    top_5_states.reset_index(inplace=True, drop=True)

    fig = px.pie(
        top_5_states,
        values="total_customer",
        names="customer_state",
        title="Total Customers per State",
    )
    return fig


def get_rfm_chart(min_date, max_date):
    all_df = get_dataframe(min_date, max_date)
    all_df["order_approved_at"] = pd.to_datetime(all_df["order_approved_at"])

    rfm_df = all_df.groupby(by="customer_unique_id", as_index=False).agg(
        {"order_approved_at": "max", "order_id": "nunique", "payment_value": "sum"}
    )
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = all_df["order_approved_at"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(
        lambda x: (recent_date - x).days
    )

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    df_sorted_freq = rfm_df.sort_values(by="frequency", ascending=False).head(5)
    df_sorted_monetary = rfm_df.sort_values(by="monetary", ascending=False).head(5)
    df_sorted_recency = rfm_df.sort_values(by="recency", ascending=True).head(5)

    fig_freq = go.Figure(
        data=[go.Bar(x=df_sorted_freq["customer_id"], y=df_sorted_freq["frequency"])]
    )
    fig_freq.update_layout(
        title="Top 5 Customers by Frequency",
        xaxis_title="Customer ID",
        yaxis_title="Frequency",
    )

    fig_monetary = go.Figure(
        data=[
            go.Bar(
                x=df_sorted_monetary["customer_id"], y=df_sorted_monetary["monetary"]
            )
        ]
    )
    fig_monetary.update_layout(
        title="Top 5 Customers by Monetary",
        xaxis_title="Customer ID",
        yaxis_title="Monetary",
    )

    fig_recency = go.Figure(
        data=[
            go.Bar(x=df_sorted_recency["customer_id"], y=df_sorted_recency["recency"])
        ]
    )
    fig_recency.update_layout(
        title="Top 5 Customers by Recency",
        xaxis_title="Customer ID",
        yaxis_title="Recency",
    )

    return fig_freq, fig_monetary, fig_recency



