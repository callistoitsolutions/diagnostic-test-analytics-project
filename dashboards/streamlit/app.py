import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

# --- Project path setup ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_ROOT)

from analytics.data_cleaning import process_file
from database.db_connection import engine

st.set_page_config(
    page_title="Diagnostic Analytics Dashboard",
    layout="wide"
)

# --- Custom CSS for professional dashboard ---
st.markdown("""
<style>
body, .css-18e3th9 {
    font-family: 'Roboto', sans-serif;
    background-color: #0D1B2A;  
    color: #E5E5E5;
}
.css-1v3fvcr {
    background-color: #0B1524; 
    color: #E5E5E5;
}
.card {
    background: linear-gradient(135deg, #008080, #4DB6AC);
    border-radius: 16px;
    padding: 25px;
    color: white;
    text-align: center;
    font-weight: 700;
    box-shadow: 0 8px 20px rgba(0,0,0,0.5);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.7);
}
.card h3 { margin:0; font-size:32px; }
.card p { margin:0; font-size:16px; }
</style>
""", unsafe_allow_html=True)

st.title("Diagnostic Analytics Dashboard")

# --- Sidebar: File Upload + Filters ---
st.sidebar.header("Upload & Filters")

# File Upload
file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])
if file:
    path = f"{PROJECT_ROOT}/data/raw/{file.name}"
    with open(path, "wb") as f:
        f.write(file.getbuffer())
    process_file(path)
    st.sidebar.success("Data uploaded & stored in database!")

# Load data from DB
query = text("SELECT * FROM test_transactions")
df = pd.read_sql(query, engine)

if df.empty:
    st.info("No data available yet. Please upload an Excel file in the sidebar.")
    st.stop()

df['test_date'] = pd.to_datetime(df['test_date'])

# --- Sidebar Filters ---
categories = df['test_category'].unique().tolist()
selected_categories = st.sidebar.multiselect(
    "Select Test Category",
    options=categories,
    default=categories
)
min_date = df['test_date'].min().date()
max_date = df['test_date'].max().date()
start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

# Apply filters
df_filtered = df[
    (df['test_category'].isin(selected_categories)) &
    (df['test_date'].dt.date >= start_date) &
    (df['test_date'].dt.date <= end_date)
]

# Session state for chart filtering
if "selected_chart_categories" not in st.session_state:
    st.session_state.selected_chart_categories = selected_categories

df_final = df_filtered[df_filtered['test_category'].isin(st.session_state.selected_chart_categories)]

# --- KPIs ---
total_tests = len(df_final)
total_revenue = df_final['revenue'].sum()
avg_price = df_final['test_price'].mean()

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.markdown(f'<div class="card"><h3>{total_tests}</h3><p>Total Tests Conducted</p></div>', unsafe_allow_html=True)
kpi2.markdown(f'<div class="card"><h3>₹{total_revenue:,.2f}</h3><p>Total Revenue</p></div>', unsafe_allow_html=True)
kpi3.markdown(f'<div class="card"><h3>₹{avg_price:.2f}</h3><p>Average Test Price</p></div>', unsafe_allow_html=True)

st.markdown("---")

# --- Charts ---
col1, col2 = st.columns(2)
chart_bg_color = "#0D1B2A"

# --- Chart 1: Test Demand by Category ---
demand_chart = df_filtered.groupby("test_category").size().reset_index(name="Total Tests")
fig1 = px.bar(
    demand_chart,
    x="test_category",
    y="Total Tests",
    color="test_category",
    template="plotly_dark",
    color_discrete_sequence=px.colors.sequential.Teal,
    hover_data=["test_category", "Total Tests"]
)
fig1.update_layout(
    title={'text': "Test Demand by Category", 'x':0.5, 'xanchor':'center', 'y':0.95, 'yanchor':'top'},
    title_font=dict(size=24, color="#E5E5E5", family="Roboto"),
    showlegend=True,
    legend=dict(title="Test Category", font=dict(color="#E5E5E5", size=14),
                bgcolor="#0B1524", bordercolor="#4DB6AC", borderwidth=1),
    plot_bgcolor=chart_bg_color,
    paper_bgcolor=chart_bg_color,
    font_color="#E5E5E5"
)
fig1.update_traces(
    marker=dict(line=dict(width=2, color='white')),
    opacity=0.9,
    hovertemplate="<b>%{x}</b><br>Total Tests: %{y}<extra></extra>",
    hoverlabel=dict(bgcolor="#00FFCC", font_size=16, font_color="#000000", font_family="Roboto")
)
col1.plotly_chart(fig1, use_container_width=True)

# --- Chart 2: Revenue Contribution ---
revenue_chart = df_filtered.groupby("test_category")['revenue'].sum().reset_index()
fig2 = px.pie(
    revenue_chart,
    names="test_category",
    values="revenue",
    color="test_category",
    template="plotly_dark",
    color_discrete_sequence=px.colors.sequential.Teal,
    hover_data=["revenue"]
)
fig2.update_traces(
    textinfo="percent+label",
    pull=[0.05]*len(revenue_chart),
    hoverinfo="label+percent+value",
    hoverlabel=dict(bgcolor="#FFB84D", font_size=16, font_color="#000000", font_family="Roboto")
)
fig2.update_layout(
    title={'text': "Revenue Contribution by Category", 'x':0.5, 'xanchor':'center', 'y':0.95, 'yanchor':'top'},
    title_font=dict(size=24, color="#E5E5E5", family="Roboto"),
    showlegend=True,
    legend=dict(title="Test Category", font=dict(color="#E5E5E5", size=14),
                bgcolor="#0B1524", bordercolor="#4DB6AC", borderwidth=1),
    plot_bgcolor=chart_bg_color,
    paper_bgcolor=chart_bg_color,
    font_color="#E5E5E5"
)
col2.plotly_chart(fig2, use_container_width=True)

# --- Chart 3: Top 10 Revenue Generating Tests ---
top_tests = df_final.groupby("test_name")['revenue'].sum().sort_values(ascending=False).head(10).reset_index()
fig3 = px.bar(
    top_tests,
    x="revenue",
    y="test_name",
    orientation="h",
    color="test_name",
    template="plotly_dark",
    color_discrete_sequence=px.colors.sequential.Agsunset,
    hover_data=["revenue"]
)
fig3.update_layout(
    title={'text': "Top 10 Revenue Generating Tests", 'x':0.5, 'xanchor':'center', 'y':0.95, 'yanchor':'top'},
    title_font=dict(size=24, color="#E5E5E5", family="Roboto"),
    showlegend=True,
    legend=dict(title="Test Name", font=dict(color="#E5E5E5", size=12),
                bgcolor="#0B1524", bordercolor="#4DB6AC", borderwidth=1),
    yaxis={'categoryorder':'total ascending'},
    plot_bgcolor=chart_bg_color,
    paper_bgcolor=chart_bg_color,
    font_color="#E5E5E5"
)
fig3.update_traces(
    marker=dict(line=dict(width=1, color='white')),
    opacity=0.9,
    hovertemplate="<b>%{y}</b><br>Revenue: ₹%{x:,.2f}<extra></extra>",
    hoverlabel=dict(bgcolor="#FF6F61", font_size=16, font_color="#FFFFFF", font_family="Roboto")
)
st.plotly_chart(fig3, use_container_width=True)

# --- Chart 4: Monthly Test Demand Trend ---
monthly_trend = df_final.groupby(df_final['test_date'].dt.to_period("M")).size().reset_index(name="Total Tests")
monthly_trend['test_date'] = monthly_trend['test_date'].dt.to_timestamp()
fig4 = px.line(
    monthly_trend,
    x="test_date",
    y="Total Tests",
    markers=True,
    template="plotly_dark",
    color_discrete_sequence=["#00CED1"],
    hover_data=["Total Tests"]
)
fig4.update_traces(
    line=dict(width=4),
    marker=dict(size=10, color="#00CED1", line=dict(width=2, color="white")),
    hovertemplate="<b>%{x|%b %Y}</b><br>Total Tests: %{y}<extra></extra>",
    hoverlabel=dict(bgcolor="#00FFFF", font_size=16, font_color="#000000", font_family="Roboto")
)
fig4.update_layout(
    title={'text': "Monthly Test Demand Trend", 'x':0.5, 'xanchor':'center', 'y':0.95, 'yanchor':'top'},
    title_font=dict(size=24, color="#E5E5E5", family="Roboto"),
    showlegend=True,
    legend=dict(title="Month", font=dict(color="#E5E5E5", size=12),
                bgcolor="#0B1524", bordercolor="#4DB6AC", borderwidth=1),
    plot_bgcolor=chart_bg_color,
    paper_bgcolor=chart_bg_color,
    font_color="#E5E5E5"
)
st.plotly_chart(fig4, use_container_width=True)

# --- Raw Data & Download ---
st.subheader("Raw Data")
st.dataframe(df_final, use_container_width=True)
csv = df_final.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_data.csv",
    mime="text/csv"
)
