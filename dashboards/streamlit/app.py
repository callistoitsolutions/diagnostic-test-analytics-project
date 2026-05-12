import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Diagnostic Analytics Dashboard - Enhanced",
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
    padding: 20px;
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
.card h3 { margin:0; font-size:28px; }
.card p { margin:0; font-size:13px; margin-top:8px; }
.section-header {
    color: #00CED1;
    font-size: 22px;
    font-weight: bold;
    margin-top: 30px;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 3px solid #00CED1;
}
</style>
""", unsafe_allow_html=True)

st.title("🏥 Diagnostic Analytics Dashboard - Enhanced")
st.markdown("*Comprehensive Patient & Test Analytics with Geographic & Demographic Insights*")

# --- Sidebar: File Upload + Filters ---
st.sidebar.header("📁 Upload & Filters")

# --- File Upload (Direct Processing) ---
file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])

# Initialize DataFrame
df = pd.DataFrame()

if file:
    try:
        # Read Excel file directly
        df = pd.read_excel(file)
        
        # Standardize column names to lowercase with underscores
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        st.sidebar.success("✓ Data uploaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {str(e)}")
        st.stop()
else:
    st.info("📌 Please upload an Excel file in the sidebar to begin.")
    st.stop()

if df.empty:
    st.info("No data available. Please upload a valid Excel file.")
    st.stop()

# --- Safe date parsing ---
try:
    df['test_date'] = pd.to_datetime(df['test_date'], errors='coerce')
    df = df.dropna(subset=['test_date'])
except KeyError:
    st.error("Error: The 'Test_Date' column is missing from your file.")
    st.stop()

# Check for required columns
required_columns = ['test_date', 'test_category', 'test_name', 'test_price_inr', 'revenue_inr', 'age', 'gender', 'city']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.stop()

# Rename columns for easier reference
df = df.rename(columns={
    'test_price_inr': 'test_price',
    'revenue_inr': 'revenue'
})

# --- Sidebar Filters ---
st.sidebar.subheader("🔍 Filter Options")

# Test Category Filter
categories = sorted(df['test_category'].unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Select Test Category",
    options=categories,
    default=categories
)

# City Filter
cities = sorted(df['city'].unique().tolist())
selected_cities = st.sidebar.multiselect(
    "Select City",
    options=cities,
    default=cities
)

# Gender Filter
genders = sorted(df['gender'].unique().tolist())
selected_genders = st.sidebar.multiselect(
    "Select Gender",
    options=genders,
    default=genders
)

# Age Range Filter
min_age = int(df['age'].min())
max_age = int(df['age'].max())
age_range = st.sidebar.slider(
    "Age Range",
    min_value=min_age,
    max_value=max_age,
    value=(min_age, max_age)
)

# Date Range Filter
min_date = df['test_date'].min().date()
max_date = df['test_date'].max().date()
start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

# Apply all filters
df_filtered = df[
    (df['test_category'].isin(selected_categories)) &
    (df['city'].isin(selected_cities)) &
    (df['gender'].isin(selected_genders)) &
    (df['age'] >= age_range[0]) &
    (df['age'] <= age_range[1]) &
    (df['test_date'].dt.date >= start_date) &
    (df['test_date'].dt.date <= end_date)
]

# --- Calculate KPIs ---
total_tests = len(df_filtered)
total_revenue = df_filtered['revenue'].sum()
avg_price = df_filtered['test_price'].mean()
total_patients = df_filtered['patient_id'].nunique()
avg_revenue_per_patient = total_revenue / total_patients if total_patients > 0 else 0
avg_age = df_filtered['age'].mean()
top_category = df_filtered['test_category'].value_counts().index[0] if len(df_filtered) > 0 else "N/A"
top_city = df_filtered['city'].value_counts().index[0] if len(df_filtered) > 0 else "N/A"
revenue_per_test = total_revenue / total_tests if total_tests > 0 else 0
male_count = len(df_filtered[df_filtered['gender'].str.lower() == 'm'])
female_count = len(df_filtered[df_filtered['gender'].str.lower() == 'f'])

# --- KPIs Section ---
st.markdown('<div class="section-header">📊 Key Performance Indicators (Extended)</div>', unsafe_allow_html=True)

# Row 1 - Core Metrics
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f'<div class="card"><h3>{total_tests}</h3><p>Total Tests Conducted</p></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="card"><h3>₹{total_revenue:,.0f}</h3><p>Total Revenue</p></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="card"><h3>{total_patients}</h3><p>Unique Patients</p></div>', unsafe_allow_html=True)
col4.markdown(f'<div class="card"><h3>₹{avg_price:.0f}</h3><p>Average Test Price</p></div>', unsafe_allow_html=True)

# Row 2 - Additional Metrics
col5, col6, col7, col8 = st.columns(4)
col5.markdown(f'<div class="card"><h3>₹{revenue_per_test:.0f}</h3><p>Revenue per Test</p></div>', unsafe_allow_html=True)
col6.markdown(f'<div class="card"><h3>₹{avg_revenue_per_patient:,.0f}</h3><p>Revenue per Patient</p></div>', unsafe_allow_html=True)
col7.markdown(f'<div class="card"><h3>{avg_age:.1f} yrs</h3><p>Average Patient Age</p></div>', unsafe_allow_html=True)
col8.markdown(f'<div class="card"><h3>{len(selected_cities)}</h3><p>Cities Covered</p></div>', unsafe_allow_html=True)

# Row 3 - Business Intelligence
col9, col10, col11, col12 = st.columns(4)
col9.markdown(f'<div class="card"><h3>{top_category}</h3><p>Top Test Category</p></div>', unsafe_allow_html=True)
col10.markdown(f'<div class="card"><h3>{top_city}</h3><p>Top City</p></div>', unsafe_allow_html=True)
col11.markdown(f'<div class="card"><h3>{male_count}</h3><p>Male Patients</p></div>', unsafe_allow_html=True)
col12.markdown(f'<div class="card"><h3>{female_count}</h3><p>Female Patients</p></div>', unsafe_allow_html=True)

st.markdown("---")

# --- SECTION 1: TEST CATEGORY ANALYSIS ---
st.markdown('<div class="section-header">1️⃣ Test Category Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Chart 1: Test Demand by Category
demand_chart = df_filtered.groupby("test_category").size().reset_index(name="Total Tests")
fig1 = px.bar(
    demand_chart,
    x="test_category",
    y="Total Tests",
    color="test_category",
    color_discrete_sequence=px.colors.sequential.Teal,
    title="Test Demand by Category"
)
fig1.update_layout(
    title={'text': "Test Demand by Category", 'x':0.5, 'xanchor':'center'},
    title_font=dict(size=20, color="#E5E5E5", family="Roboto"),
    plot_bgcolor="#0D1B2A",
    paper_bgcolor="#0D1B2A",
    font_color="#E5E5E5",
    xaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5")),
    yaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5"))
)
fig1.update_traces(
    marker=dict(line=dict(width=2, color='white')),
    opacity=0.9,
    hovertemplate="<b>%{x}</b><br>Total Tests: %{y}<extra></extra>"
)
col1.plotly_chart(fig1, use_container_width=True)

# Chart 2: Revenue Contribution
revenue_chart = df_filtered.groupby("test_category")['revenue'].sum().reset_index()
fig2 = px.pie(
    revenue_chart,
    names="test_category",
    values="revenue",
    color="test_category",
    color_discrete_sequence=px.colors.sequential.Teal,
    title="Revenue Contribution by Category"
)
fig2.update_traces(
    textinfo="percent+label",
    pull=[0.05]*len(revenue_chart),
    hoverinfo="label+percent+value"
)
fig2.update_layout(
    title={'text': "Revenue Contribution by Category", 'x':0.5, 'xanchor':'center'},
    title_font=dict(size=20, color="#E5E5E5", family="Roboto"),
    plot_bgcolor="#0D1B2A",
    paper_bgcolor="#0D1B2A",
    font_color="#E5E5E5"
)
col2.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# --- SECTION 2: GEOGRAPHIC ANALYSIS ---
st.markdown('<div class="section-header">🗺️ Geographic Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Chart 3: City-wise Revenue
city_revenue = df_filtered.groupby("city")['revenue'].sum().sort_values(ascending=False).head(15).reset_index()
fig3 = px.bar(
    city_revenue,
    x="revenue",
    y="city",
    orientation="h",
    color="revenue",
    color_continuous_scale="Teal",
    title="Top 15 Cities by Revenue"
)
fig3.update_layout(
    title={'text': "Top 15 Cities by Revenue", 'x':0.5, 'xanchor':'center'},
    title_font=dict(size=20, color="#E5E5E5", family="Roboto"),
    plot_bgcolor="#0D1B2A",
    paper_bgcolor="#0D1B2A",
    font_color="#E5E5E5",
    xaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5")),
    yaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5"))
)
fig3.update_traces(
    hovertemplate="<b>%{y}</b><br>Revenue: ₹%{x:,.0f}<extra></extra>"
)
col1.plotly_chart(fig3, use_container_width=True)

# Chart 4: City-wise Test Demand
city_tests = df_filtered.groupby("city").size().sort_values(ascending=False).head(15).reset_index(name="Test Count")
fig4 = px.bar(
    city_tests,
    x="Test Count",
    y="city",
    orientation="h",
    color="Test Count",
    color_continuous_scale="Blues",
    title="Top 15 Cities by Test Demand"
)
fig4.update_layout(
    title={'text': "Top 15 Cities by Test Demand", 'x':0.5, 'xanchor':'center'},
    title_font=dict(size=20, color="#E5E5E5", family="Roboto"),
    plot_bgcolor="#0D1B2A",
    paper_bgcolor="#0D1B2A",
    font_color="#E5E5E5",
    xaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5")),
    yaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5"))
)
fig4.update_traces(
    hovertemplate="<b>%{y}</b><br>Tests: %{x}<extra></extra>"
)
col2.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# --- SECTION 3: PATIENT DEMOGRAPHICS ---
st.markdown('<div class="section-header">👥 Patient Demographics Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Chart 5: Age Distribution
age_bins = [0, 18, 30, 40, 50, 60, 100]
age_labels = ['0-18', '18-30', '30-40', '40-50', '50-60', '60+']
df_filtered['age_group'] = pd.cut(df_filtered['age'], bins=age_bins, labels=age_labels, right=False)
age_dist = df_filtered['age_group'].value_counts().sort_index().reset_index(name="Count")
age_dist.columns = ['age_group', 'Count']

fig5 = px.bar(
    age_dist,
    x="age_group",
    y="Count",
    color="age_group",
    color_discrete_sequence=px.colors.sequential.Viridis,
    title="Patient Distribution by Age Group"
)
fig5.update_layout(
    title={'text': "Patient Distribution by Age Group", 'x':0.5, 'xanchor':'center'},
    title_font=dict(size=20, color="#E5E5E5", family="Roboto"),
    plot_bgcolor="#0D1B2A",
    paper_bgcolor="#0D1B2A",
    font_color="#E5E5E5",
    xaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5")),
    yaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5")),
    showlegend=False
)
fig5.update_traces(
    hovertemplate="<b>%{x}</b><br>Patients: %{y}<extra></extra>"
)
col1.plotly_chart(fig5, use_container_width=True)

# Chart 6: Gender Distribution
gender_dist = df_filtered['gender'].value_counts().reset_index(name="Count")
gender_dist.columns = ['gender', 'Count']

fig6 = px.pie(
    gender_dist,
    names="gender",
    values="Count",
    color="gender",
    color_discrete_sequence=['#FF6B9D', '#4DB6AC'],
    title="Patient Distribution by Gender"
)
fig6.update_traces(
    textinfo="percent+label",
    pull=[0.1, 0.1],
    hoverinfo="label+percent+value"
)
fig6.update_layout(
    title={'text': "Patient Distribution by Gender", 'x':0.5, 'xanchor':'center'},
    title_font=dict(size=20, color="#E5E5E5", family="Roboto"),
    plot_bgcolor="#0D1B2A",
    paper_bgcolor="#0D1B2A",
    font_color="#E5E5E5"
)
col2.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# --- SECTION 4: CITY-WISE PERFORMANCE & PATIENT PROFILES ---
st.markdown('<div class="section-header">🏙️ City-wise Performance & Patient Profiles</div>', unsafe_allow_html=True)

# Chart 7: Top Cities with Average Age
city_profile = df_filtered.groupby("city").agg({
    'patient_id': 'count',
    'revenue': 'sum',
    'age': 'mean',
    'test_name': 'count'
}).reset_index()
city_profile.columns = ['city', 'patient_count', 'total_revenue', 'avg_age', 'test_count']
city_profile = city_profile.sort_values('total_revenue', ascending=False).head(10)

fig7 = px.scatter(
    city_profile,
    x="avg_age",
    y="total_revenue",
    size="patient_count",
    color="patient_count",
    hover_name="city",
    color_continuous_scale="Teal",
    title="Top 10 Cities: Revenue vs Average Patient Age"
)
fig7.update_layout(
    title={'text': "Top 10 Cities: Revenue vs Average Patient Age", 'x':0.5, 'xanchor':'center'},
    title_font=dict(size=20, color="#E5E5E5", family="Roboto"),
    plot_bgcolor="#0D1B2A",
    paper_bgcolor="#0D1B2A",
    font_color="#E5E5E5",
    xaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5")),
    yaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5"))
)
st.plotly_chart(fig7, use_container_width=True)

# Chart 8: Popular Tests by Top Cities
st.subheader("Popular Tests by Top 5 Cities")
top_5_cities = df_filtered['city'].value_counts().head(5).index.tolist()
city_test_data = df_filtered[df_filtered['city'].isin(top_5_cities)].groupby(['city', 'test_category']).size().reset_index(name="count")
city_test_data = city_test_data.sort_values(['city', 'count'], ascending=[True, False])

fig8 = px.bar(
    city_test_data,
    x="city",
    y="count",
    color="test_category",
    title="Test Category Distribution by Top 5 Cities",
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig8.update_layout(
    title={'text': "Test Category Distribution by Top 5 Cities", 'x':0.5, 'xanchor':'center'},
    title_font=dict(size=20, color="#E5E5E5", family="Roboto"),
    plot_bgcolor="#0D1B2A",
    paper_bgcolor="#0D1B2A",
    font_color="#E5E5E5",
    xaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5")),
    yaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5"))
)
st.plotly_chart(fig8, use_container_width=True)

st.markdown("---")

# --- SECTION 5: PATIENT SEGMENTATION ---
st.markdown('<div class="section-header">🎯 Patient Segmentation Analysis</div>', unsafe_allow_html=True)

# Chart 9: High-Value Patients by Age & Gender
age_gender_segment = df_filtered.groupby(['age_group', 'gender']).agg({
    'patient_id': 'count',
    'revenue': ['sum', 'mean']
}).reset_index()
age_gender_segment.columns = ['age_group', 'gender', 'patient_count', 'total_revenue', 'avg_revenue']
age_gender_segment = age_gender_segment.sort_values('total_revenue', ascending=False)

fig9 = px.bar(
    age_gender_segment,
    x="age_group",
    y="total_revenue",
    color="gender",
    barmode='group',
    color_discrete_sequence=['#FF6B9D', '#4DB6AC'],
    title="Total Revenue by Age Group & Gender"
)
fig9.update_layout(
    title={'text': "Total Revenue by Age Group & Gender", 'x':0.5, 'xanchor':'center'},
    title_font=dict(size=20, color="#E5E5E5", family="Roboto"),
    plot_bgcolor="#0D1B2A",
    paper_bgcolor="#0D1B2A",
    font_color="#E5E5E5",
    xaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5")),
    yaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5"))
)
st.plotly_chart(fig9, use_container_width=True)

# Chart 10: Patient Value Segmentation
col1, col2 = st.columns(2)

# Revenue by Age Group
revenue_by_age = df_filtered.groupby('age_group')['revenue'].sum().reset_index()
fig10 = px.pie(
    revenue_by_age,
    names="age_group",
    values="revenue",
    color="age_group",
    color_discrete_sequence=px.colors.sequential.Viridis,
    title="Revenue Contribution by Age Group"
)
fig10.update_traces(
    textinfo="percent+label",
    pull=[0.05]*len(revenue_by_age),
    hoverinfo="label+percent+value"
)
fig10.update_layout(
    title={'text': "Revenue Contribution by Age Group", 'x':0.5, 'xanchor':'center'},
    title_font=dict(size=20, color="#E5E5E5", family="Roboto"),
    plot_bgcolor="#0D1B2A",
    paper_bgcolor="#0D1B2A",
    font_color="#E5E5E5"
)
col1.plotly_chart(fig10, use_container_width=True)

# Tests by Age Group
tests_by_age = df_filtered.groupby('age_group').size().reset_index(name="count")
fig11 = px.bar(
    tests_by_age,
    x="age_group",
    y="count",
    color="age_group",
    color_discrete_sequence=px.colors.sequential.Viridis,
    title="Test Count by Age Group"
)
fig11.update_layout(
    title={'text': "Test Count by Age Group", 'x':0.5, 'xanchor':'center'},
    title_font=dict(size=20, color="#E5E5E5", family="Roboto"),
    plot_bgcolor="#0D1B2A",
    paper_bgcolor="#0D1B2A",
    font_color="#E5E5E5",
    xaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5")),
    yaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5")),
    showlegend=False
)
col2.plotly_chart(fig11, use_container_width=True)

st.markdown("---")

# --- SECTION 6: TRENDS & ADDITIONAL INSIGHTS ---
st.markdown('<div class="section-header">📈 Monthly Trends</div>', unsafe_allow_html=True)

# Chart 12: Monthly Test Demand Trend
monthly_trend = df_filtered.groupby(df_filtered['test_date'].dt.to_period("M")).size().reset_index(name="Total Tests")
monthly_trend['test_date'] = monthly_trend['test_date'].dt.to_timestamp()

fig12 = px.line(
    monthly_trend,
    x="test_date",
    y="Total Tests",
    markers=True,
    color_discrete_sequence=["#00CED1"],
    title="Monthly Test Demand Trend"
)
fig12.update_traces(
    line=dict(width=4),
    marker=dict(size=10, color="#00CED1", line=dict(width=2, color="white")),
    hovertemplate="<b>%{x|%b %Y}</b><br>Total Tests: %{y}<extra></extra>"
)
fig12.update_layout(
    title={'text': "Monthly Test Demand Trend", 'x':0.5, 'xanchor':'center'},
    title_font=dict(size=20, color="#E5E5E5", family="Roboto"),
    plot_bgcolor="#0D1B2A",
    paper_bgcolor="#0D1B2A",
    font_color="#E5E5E5",
    xaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5")),
    yaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5"))
)
st.plotly_chart(fig12, use_container_width=True)

st.markdown("---")

# --- SECTION 7: TOP REVENUE TESTS ---
st.markdown('<div class="section-header">💰 Top Revenue Generating Tests</div>', unsafe_allow_html=True)

top_tests = df_filtered.groupby("test_name")['revenue'].sum().sort_values(ascending=False).head(10).reset_index()
fig13 = px.bar(
    top_tests,
    x="revenue",
    y="test_name",
    orientation="h",
    color="test_name",
    color_discrete_sequence=px.colors.sequential.Agsunset,
    title="Top 10 Revenue Generating Tests"
)
fig13.update_layout(
    title={'text': "Top 10 Revenue Generating Tests", 'x':0.5, 'xanchor':'center'},
    title_font=dict(size=20, color="#E5E5E5", family="Roboto"),
    yaxis={'categoryorder':'total ascending'},
    plot_bgcolor="#0D1B2A",
    paper_bgcolor="#0D1B2A",
    font_color="#E5E5E5",
    xaxis=dict(title_font=dict(color="#E5E5E5"), tickfont=dict(color="#E5E5E5")),
    yaxis_tickfont=dict(color="#E5E5E5")
)
fig13.update_traces(
    marker=dict(line=dict(width=1, color='white')),
    opacity=0.9,
    hovertemplate="<b>%{y}</b><br>Revenue: ₹%{x:,.0f}<extra></extra>"
)
st.plotly_chart(fig13, use_container_width=True)

st.markdown("---")

# --- RAW DATA & DOWNLOAD ---
st.markdown('<div class="section-header">📋 Raw Data</div>', unsafe_allow_html=True)
st.dataframe(df_filtered, use_container_width=True)

csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name="diagnostic_analytics_filtered.csv",
    mime="text/csv"
)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #00CED1;'><b>Dashboard Generated Successfully ✓</b></p>", unsafe_allow_html=True)
