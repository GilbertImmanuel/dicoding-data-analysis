import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib

class DataAnalyzer:
    def __init__(self, df):
        self.df = df

    def create_daily_orders_df(self):
        daily_orders_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "order_id": "nunique",
            "payment_value": "sum"
        }).reset_index().rename(columns={
            "order_id": "order_count",
            "payment_value": "revenue"
        })
        
        return daily_orders_df
    
    def create_sum_spend_df(self):
        sum_spend_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "payment_value": "sum"
        }).reset_index().rename(columns={
            "payment_value": "total_spend"
        })

        return sum_spend_df

    def create_sum_order_items_df(self):
        sum_order_items_df = self.df.groupby("product_category_name_english")["product_id"].count().reset_index()
        sum_order_items_df.rename(columns={"product_id": "product_count"}, inplace=True)
        sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

        return sum_order_items_df

    def create_bystate_df(self):
        bystate_df = self.df.groupby(by="customer_state").customer_id.nunique().reset_index()
        bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
        most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
        bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

        return bystate_df, most_common_state
    
class BrazilMapPlotter:
    def __init__(self, data, plt, mpimg, urllib, st):
        self.data = data
        self.plt = plt
        self.mpimg = mpimg
        self.urllib = urllib
        self.st = st

    def plot(self):
        brazil = self.mpimg.imread(self.urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'),'jpg')
        ax = self.data.plot(kind="scatter", x="geolocation_lng", y="geolocation_lat", figsize=(10,10), alpha=0.3,s=0.3,c='green')
        self.plt.axis('off')
        self.plt.imshow(brazil, extent=[-73.98283055, -33.8,-33.75116944,5.4])
        self.st.pyplot()

sns.set(style='whitegrid')
st.set_option('deprecation.showPyplotGlobalUse', False)

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("https://raw.githubusercontent.com/GilbertImmanuel/dicoding-data-analysis/main/data/all_df.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Geolocation Dataset
geolocation = pd.read_csv('https://raw.githubusercontent.com/GilbertImmanuel/dicoding-data-analysis/main/data/geolocation.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>Brazil E-Commerce</h1>", unsafe_allow_html=True)
    st.image('https://raw.githubusercontent.com/GilbertImmanuel/dicoding-data-analysis/main/dashboard/logo.png')

    # Date Range
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
state, most_common_state = function.create_bystate_df()

# Title
st.header("Brazil E-Commerce Public Data Analysis")

# Daily Orders
st.subheader("Daily Orders")
col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = daily_orders_df["revenue"].sum()
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Customer Spend Money
st.subheader("Customer Spend Money")
col1, col2 = st.columns(2)

with col1:
    total_spend = sum_spend_df["total_spend"].sum()
    st.markdown(f"Total Spend: **{total_spend}**")

with col2:
    avg_spend = sum_spend_df["total_spend"].mean()
    st.markdown(f"Average Spend: **{avg_spend}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    data=sum_spend_df,
    x="order_approved_at",
    y="total_spend",
    marker="o",
    linewidth=2,
    color="#90CAF9"
)

ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Order Items
st.subheader("Order Items")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette="pastel", ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=65)
ax[0].set_title("Most sold products", loc="center", fontsize=60)
ax[0].tick_params(axis ='y', labelsize=55)
ax[0].tick_params(axis ='x', labelsize=40)

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette="pastel", ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=65)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Fewest products sold", loc="center", fontsize=60)
ax[1].tick_params(axis='y', labelsize=55)
ax[1].tick_params(axis='x', labelsize=40)

st.pyplot(fig)

# Customer Demographic
st.subheader("Customer Demographic")
tab1, tab2 = st.tabs(["State", "Geolocation"])

with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"Most Common State: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values, 
                data=state,
                palette="pastel"
                    )

    plt.title("Number customers from State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

    with st.expander("See Explanation"):
        st.write("""
                 The graph above shows the number of customers from each state. The state with the most customers is São Paulo (SP), followed by Maranhão (MA) in second, and Amapá (AP) in third.
                 """)

with tab2:
    map_plot.plot()

    with st.expander("See Explanation"):
        st.write("""
                 The graph above shows the distribution of customers in Brazil. The green dots represent the location of the customers.
                 
                The map shows that most customers are located in the southeast and south of Brazil. Many of which resides in the main cities such as São Paulo, Rio de Janeiro, Porto Alegre, and others.
                 """)
        
st.caption('Copyright (C) Gilbert Immanuel 2024')