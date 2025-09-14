import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
# import datetime as dt
# from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Marketing Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

if not hasattr(np, "typeDict"):
    np.typeDict = np.sctypeDict
if not hasattr(np, "int"):
    np.int = int
if not hasattr(np, "float"):
    np.float = float
if not hasattr(np, "bool"):
    np.bool = bool
if not hasattr(np, "typeDict"):
    np.typeDict = np.sctypeDict


# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .kpi-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    marketing_df = pd.read_csv('data/marketing_data_processed.csv')
    business_df = pd.read_csv('data/business_data_processed.csv')
    daily_marketing = pd.read_csv('data/daily_marketing.csv')
    daily_total_marketing = pd.read_csv('data/daily_total_marketing.csv')
    platform_summary = pd.read_csv('data/platform_summary.csv')
    tactic_summary = pd.read_csv('data/tactic_summary.csv')
    business_marketing_combined = pd.read_csv('data/business_marketing_combined.csv')

    # Convert dates
    for df in [marketing_df, business_df, daily_marketing, daily_total_marketing, business_marketing_combined]:
        df['date'] = pd.to_datetime(df['date'])

    return {
        'marketing_df': marketing_df,
        'business_df': business_df,
        'daily_marketing': daily_marketing,
        'daily_total_marketing': daily_total_marketing,
        'platform_summary': platform_summary,
        'tactic_summary': tactic_summary,
        'business_marketing_combined': business_marketing_combined
    }

# Load all data
data = load_data()

# Sidebar for navigation and filters
st.sidebar.title("🎯 Marketing Intelligence")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.selectbox(
    "Navigate to:",
    ["📊 Executive Dashboard", "🚀 Platform Performance", "🎯 Campaign Analysis", 
     "💼 Business Impact", "🔄 Attribution Analysis"]
)

# Date filter
st.sidebar.markdown("### 📅 Date Range Filter")
min_date = data['marketing_df']['date'].min().date()
max_date = data['marketing_df']['date'].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Platform filter
st.sidebar.markdown("### 📱 Platform Filter")
platforms = ['All'] + list(data['marketing_df']['platform'].unique())
selected_platforms = st.sidebar.multiselect(
    "Select Platforms:",
    platforms,
    default=['All']
)

# Apply filters
def filter_data(df, date_col='date'):
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df[date_col] >= pd.to_datetime(start_date)) & 
                (df[date_col] <= pd.to_datetime(end_date))]

    if 'platform' in df.columns and 'All' not in selected_platforms and selected_platforms:
        df = df[df['platform'].isin(selected_platforms)]

    return df

# Helper function for KPI cards
def display_kpi(label, value, delta=None, format_str="${:,.0f}"):
    if delta:
        st.metric(label=label, value=format_str.format(value), delta=f"{delta:+.1f}%")
    else:
        st.metric(label=label, value=format_str.format(value))

# PAGE 1: EXECUTIVE DASHBOARD
if page == "📊 Executive Dashboard":
    st.title("📊 Marketing Intelligence Dashboard")
    st.markdown("### Executive Summary & Key Performance Indicators")

    # Filter data
    filtered_marketing = filter_data(data['daily_total_marketing'])
    filtered_business = filter_data(data['business_df'])

    # Key Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        total_spend = filtered_marketing['spend'].sum()
        display_kpi("Total Ad Spend", total_spend)

    with col2:
        total_revenue = filtered_marketing['attributed revenue'].sum()
        display_kpi("Attributed Revenue", total_revenue)

    with col3:
        avg_roas = total_revenue / total_spend if total_spend > 0 else 0
        display_kpi("Overall ROAS", avg_roas, format_str="{:.2f}x")

    with col4:
        total_business_revenue = filtered_business['total revenue'].sum()
        display_kpi("Total Business Revenue", total_business_revenue)

    with col5:
        attribution_rate = (total_revenue / total_business_revenue * 100) if total_business_revenue > 0 else 0
        display_kpi("Attribution Rate", attribution_rate, format_str="{:.1f}%")

    st.markdown("---")

    # Charts Row 1
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Daily Marketing Performance")
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=filtered_marketing['date'], y=filtered_marketing['spend'],
                      name="Ad Spend", line=dict(color='#ff7f0e')),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=filtered_marketing['date'], y=filtered_marketing['attributed revenue'],
                      name="Attributed Revenue", line=dict(color='#2ca02c')),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=filtered_marketing['date'], y=filtered_marketing['ROAS'],
                      name="ROAS", line=dict(color='#d62728')),
            secondary_y=True,
        )

        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Revenue & Spend ($)", secondary_y=False)
        fig.update_yaxes(title_text="ROAS", secondary_y=True)
        fig.update_layout(height=400, showlegend=True)

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🏢 Business Performance Trends")

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=filtered_business['date'], y=filtered_business['total revenue'],
                      name="Total Revenue", line=dict(color='#1f77b4')),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=filtered_business['date'], y=filtered_business['# of orders'],
                      name="Orders", line=dict(color='#ff7f0e')),
            secondary_y=True,
        )

        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
        fig.update_yaxes(title_text="Orders", secondary_y=True)
        fig.update_layout(height=400, showlegend=True)

        st.plotly_chart(fig, use_container_width=True)

    # Charts Row 2
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Platform Performance")
        filtered_platform_data = filter_data(data['daily_marketing'])
        platform_agg = filtered_platform_data.groupby('platform').agg({
            'spend': 'sum',
            'attributed revenue': 'sum'
        }).reset_index()
        platform_agg['ROAS'] = platform_agg['attributed revenue'] / platform_agg['spend']

        fig = px.bar(platform_agg, x='platform', y='ROAS', 
                     title="ROAS by Platform",
                     color='ROAS', color_continuous_scale='Viridis')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("💰 Revenue Attribution")

        fig = px.pie(platform_agg, values='attributed revenue', names='platform',
                     title="Revenue Share by Platform")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

# PAGE 2: PLATFORM PERFORMANCE
elif page == "🚀 Platform Performance":
    st.title("🚀 Platform Performance Analysis")
    st.markdown("### Deep dive into Facebook, Google, and TikTok performance")

    # Filter data
    filtered_marketing = filter_data(data['marketing_df'])
    filtered_daily = filter_data(data['daily_marketing'])

    # Platform comparison metrics
    platform_metrics = filtered_marketing.groupby('platform').agg({
        'impression': 'sum',
        'clicks': 'sum',
        'spend': 'sum',
        'attributed revenue': 'sum'
    }).reset_index()

    platform_metrics['ROAS'] = platform_metrics['attributed revenue'] / platform_metrics['spend']
    platform_metrics['CTR'] = (platform_metrics['clicks'] / platform_metrics['impression']) * 100
    platform_metrics['CPC'] = platform_metrics['spend'] / platform_metrics['clicks']

    # Display platform comparison table
    st.subheader("📊 Platform Comparison")

    # Format the dataframe for display
    display_df = platform_metrics.copy()
    display_df['spend'] = display_df['spend'].apply(lambda x: f"${x:,.0f}")
    display_df['attributed revenue'] = display_df['attributed revenue'].apply(lambda x: f"${x:,.0f}")
    display_df['ROAS'] = display_df['ROAS'].apply(lambda x: f"{x:.2f}x")
    display_df['CTR'] = display_df['CTR'].apply(lambda x: f"{x:.2f}%")
    display_df['CPC'] = display_df['CPC'].apply(lambda x: f"${x:.2f}")
    display_df['impression'] = display_df['impression'].apply(lambda x: f"{x:,}")
    display_df['clicks'] = display_df['clicks'].apply(lambda x: f"{x:,}")

    #st.dataframe(display_df, use_container_width=True)
    
    plot_columns = [
    "impression",
    "clicks",
    "spend",
    "attributed revenue",
    "ROAS",
    "CTR",
    "CPC"
    ]
    
    # Display labels for user-friendly dropdown
    plot_labels = {
        "impression": "Impressions",
        "clicks": "Clicks",
        "spend": "Spend",
        "attributed revenue": "Attributed Revenue",
        "ROAS": "ROAS",
        "CTR": "CTR (%)",
        "CPC": "CPC"
    }

    # # Sidebar widget for metric selection
    # selected_label = st.selectbox("Select Metric to Visualize", [plot_labels[col] for col in plot_columns])
    # selected_col = [col for col in plot_columns if plot_labels[col] == selected_label][0]

    # # Dynamic Bar Plot
    # st.subheader(f"Bar Plot: {selected_label}")
    # fig, ax = plt.subplots()
    # ax.bar(platform_metrics["platform"], platform_metrics[selected_col], color=["#0077B6", "#43AA8B", "#FF7F51"])
    # ax.set_xlabel("Platform")
    # ax.set_ylabel(selected_label)
    # st.pyplot(fig)
    
    tabs = st.tabs([plot_labels[col] for col in plot_columns])

    for i, tab in enumerate(tabs):
        with tab:
            selected_col = plot_columns[i]
            selected_label = plot_labels[selected_col]
            fig = px.bar(
                platform_metrics,
                x="platform",
                y=selected_col,
                color="platform",
                color_discrete_map={
                    "Facebook": "#0077B6",
                    "Google": "#43AA8B",
                    "TikTok": "#FF7F51"
                },
                template="plotly_dark"
            )
            fig.update_layout(
                width=820, height=400
            )
            st.plotly_chart(fig, use_container_width=False)
    
    # st.subheader(f"Bar Plot: {selected_label}")

    # fig = px.bar(
    #     platform_metrics,
    #     x="platform",
    #     y=selected_col,
    #     color="platform",
    #     color_discrete_map={
    #         "Facebook": "#0077B6",
    #         "Google": "#43AA8B",
    #         "TikTok": "#FF7F51"
    #     },
    #     template="plotly_dark",                   # Matches dark dashboard background
    # )

    # fig.update_layout(
    #     plot_bgcolor="#181A20",                   # Custom background to match your UI
    #     paper_bgcolor="#181A20",
    #     font_color="white",
    #     width=420, height=250                     # Controls size
    # )

    # st.plotly_chart(fig, use_container_width=False)

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Platform Trends Over Time")

        metrics = ["ROAS", "spend", "attributed revenue", "CTR"]
        tabs = st.tabs(metrics)

        for i, tab in enumerate(tabs):
            with tab:
                metric = metrics[i]
                fig = px.line(
                    filtered_daily,
                    x='date',
                    y=metric,
                    color='platform'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)


    with col2:
        st.subheader("🎯 Efficiency Metrics")

        fig = px.scatter(platform_metrics, x='CPC', y='ROAS', 
                        size='spend', color='platform',
                        title="Efficiency: CPC vs ROAS (bubble size = spend)",
                        hover_data=['CTR'])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# PAGE 3: CAMPAIGN ANALYSIS  
elif page == "🎯 Campaign Analysis":
    st.title("🎯 Campaign Analysis")
    st.markdown("### Tactical performance and campaign optimization insights")

    # Filter data
    filtered_marketing = filter_data(data['marketing_df'])

    # Campaign performance by tactic
    tactic_metrics = filtered_marketing.groupby(['platform', 'tactic']).agg({
        'impression': 'sum',
        'clicks': 'sum', 
        'spend': 'sum',
        'attributed revenue': 'sum'
    }).reset_index()

    tactic_metrics['ROAS'] = tactic_metrics['attributed revenue'] / tactic_metrics['spend']
    tactic_metrics['CTR'] = (tactic_metrics['clicks'] / tactic_metrics['impression']) * 100

    st.subheader("📊 Tactic Performance")

    # Tactic comparison
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(tactic_metrics, x='tactic', y='ROAS', color='platform',
                     title="ROAS by Tactic and Platform",
                     barmode='group')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(tactic_metrics, x='spend', y='attributed revenue',
                        color='platform', size='ROAS',
                        hover_data=['tactic', 'CTR'],
                        title="Spend vs Revenue (bubble size = ROAS)")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Individual campaign performance
    st.subheader("🎪 Individual Campaign Performance")

    campaign_metrics = filtered_marketing.groupby(['platform', 'campaign']).agg({
        'spend': 'sum',
        'attributed revenue': 'sum'
    }).reset_index()
    campaign_metrics['ROAS'] = campaign_metrics['attributed revenue'] / campaign_metrics['spend']

    # Top and bottom performers
    col1, col2 = st.columns(2)

    with col1:
        st.write("**🏆 Top 10 Campaigns by ROAS**")
        top_campaigns = campaign_metrics.nlargest(10, 'ROAS')[['campaign', 'ROAS', 'spend', 'attributed revenue']]
        st.dataframe(top_campaigns, use_container_width=True)

    with col2:
        st.write("**⚠️ Bottom 10 Campaigns by ROAS**")
        bottom_campaigns = campaign_metrics.nsmallest(10, 'ROAS')[['campaign', 'ROAS', 'spend', 'attributed revenue']]
        st.dataframe(bottom_campaigns, use_container_width=True)

# PAGE 4: BUSINESS IMPACT
elif page == "💼 Business Impact":
    st.title("💼 Business Impact Analysis")
    st.markdown("### Understanding how marketing drives business outcomes")

    # Filter data
    filtered_combined = filter_data(data['business_marketing_combined'])
    filtered_business = filter_data(data['business_df'])

    # Correlation analysis
    st.subheader("📈 Marketing vs Business Performance")

    col1, col2 = st.columns(2)

    with col1:
        # Scatter plot: Marketing spend vs Business revenue
        fig = px.scatter(filtered_combined, 
                        x='spend', y='total revenue',
                        title="Marketing Spend vs Total Business Revenue",
                        trendline="ols",
                        hover_data=['date', 'ROAS'])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Attribution rate over time
        filtered_combined['attribution_rate'] = (filtered_combined['attributed revenue'] / 
                                                filtered_combined['total revenue'] * 100)

        fig = px.line(filtered_combined, x='date', y='attribution_rate',
                      title="Marketing Attribution Rate Over Time (%)")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Business metrics deep dive
    st.subheader("🏢 Business Metrics Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=filtered_business['date'], y=filtered_business['AOV'],
                      name="AOV", line=dict(color='#1f77b4')),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=filtered_business['date'], y=filtered_business['new_customer_rate'],
                      name="New Customer Rate (%)", line=dict(color='#ff7f0e')),
            secondary_y=True,
        )

        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="AOV ($)", secondary_y=False)
        fig.update_yaxes(title_text="New Customer Rate (%)", secondary_y=True)
        fig.update_layout(height=400, title="AOV vs New Customer Acquisition")

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.line(filtered_business, x='date', y='gross_margin_pct',
                      title="Gross Margin Percentage Over Time")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Key insights
    st.subheader("🔍 Key Business Insights")

    total_marketing_spend = filtered_combined['spend'].sum()
    total_business_revenue = filtered_combined['total revenue'].sum()
    avg_attribution_rate = (filtered_combined['attributed revenue'].sum() / 
                           total_business_revenue * 100)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Marketing Investment", f"${total_marketing_spend:,.0f}")
        st.metric("Business Revenue", f"${total_business_revenue:,.0f}")

    with col2:
        blended_roas = total_business_revenue / total_marketing_spend
        st.metric("Blended ROAS", f"{blended_roas:.2f}x")
        st.metric("Attribution Rate", f"{avg_attribution_rate:.1f}%")

    with col3:
        avg_aov = filtered_business['AOV'].mean()
        avg_margin = filtered_business['gross_margin_pct'].mean()
        st.metric("Average AOV", f"${avg_aov:.2f}")
        st.metric("Average Margin", f"{avg_margin:.1f}%")

# PAGE 5: ATTRIBUTION ANALYSIS
elif page == "🔄 Attribution Analysis":
    st.title("🔄 Attribution Analysis")
    st.markdown("### Marketing attribution and optimization opportunities")

    # Filter data
    filtered_marketing = filter_data(data['marketing_df'])
    filtered_daily = filter_data(data['daily_marketing'])

    # Attribution breakdown
    st.subheader("🎯 Attribution Breakdown")

    attribution_summary = filtered_marketing.groupby(['platform', 'tactic']).agg({
        'spend': 'sum',
        'attributed revenue': 'sum',
        'clicks': 'sum',
        'impression': 'sum'
    }).reset_index()

    attribution_summary['ROAS'] = attribution_summary['attributed revenue'] / attribution_summary['spend']
    attribution_summary['Revenue Share %'] = (attribution_summary['attributed revenue'] / 
                                             attribution_summary['attributed revenue'].sum() * 100)
    attribution_summary['Spend Share %'] = (attribution_summary['spend'] / 
                                           attribution_summary['spend'].sum() * 100)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
        attribution_summary,
        x="tactic",
        y="attributed revenue",
        labels={
        "tactic": "Marketing Tactic",  
        "attributed revenue": "Revenue Generated($)"
        },
        color="platform",
        barmode="group",
        text="attributed revenue",
        color_discrete_map={
            "Facebook": "deepskyblue",
            "Google": "dodgerblue",
            "TikTok": "lightpink"
        },
        title="Attributed Revenue by Tactic and Platform"
        )
        fig.update_layout(
            height=400
        )
        fig.update_traces(texttemplate='$%{text:,}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(attribution_summary, 
                        x='Spend Share %', y='Revenue Share %',
                        size='ROAS', color='platform',
                        hover_data=['tactic'],
                        title="Spend Share vs Revenue Share")
        # Add diagonal line for reference
        fig.add_shape(type="line", x0=0, y0=0, x1=100, y1=100,
                     line=dict(dash="dash", color="gray"))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Optimization opportunities
    st.subheader("🚀 Optimization Opportunities")

    # Calculate efficiency scores
    attribution_summary['Efficiency Score'] = attribution_summary['Revenue Share %'] / attribution_summary['Spend Share %']

    col1, col2 = st.columns(2)

    with col1:
        st.write("**🎯 Underperforming Tactics (Efficiency Score < 1.0)**")
        underperforming = attribution_summary[attribution_summary['Efficiency Score'] < 1.0].sort_values('Efficiency Score')
        underperforming_display = underperforming[['platform', 'tactic', 'Efficiency Score', 'ROAS']].copy()
        underperforming_display['Efficiency Score'] = underperforming_display['Efficiency Score'].round(2)
        underperforming_display['ROAS'] = underperforming_display['ROAS'].round(2)
        st.dataframe(underperforming_display, use_container_width=True)

    with col2:
        st.write("**🏆 High-Performing Tactics (Efficiency Score > 1.0)**")
        overperforming = attribution_summary[attribution_summary['Efficiency Score'] > 1.0].sort_values('Efficiency Score', ascending=False)
        overperforming_display = overperforming[['platform', 'tactic', 'Efficiency Score', 'ROAS']].copy()
        overperforming_display['Efficiency Score'] = overperforming_display['Efficiency Score'].round(2)
        overperforming_display['ROAS'] = overperforming_display['ROAS'].round(2)
        st.dataframe(overperforming_display, use_container_width=True)

    # Monthly trends
    st.subheader("📅 Monthly Attribution Trends")

    filtered_daily['month'] = filtered_daily['date'].dt.to_period('M')
    monthly_trends = filtered_daily.groupby(['month', 'platform']).agg({
        'spend': 'sum',
        'attributed revenue': 'sum'
    }).reset_index()
    monthly_trends['ROAS'] = monthly_trends['attributed revenue'] / monthly_trends['spend']
    monthly_trends['month'] = monthly_trends['month'].astype(str)

    fig = px.line(monthly_trends, x='month', y='ROAS', color='platform',
                  title="Monthly ROAS Trends by Platform")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Dashboard Info**")
st.sidebar.info(f"""
**Data Period:** {min_date} to {max_date}  
**Total Days:** {(max_date - min_date).days + 1}  
**Platforms:** Facebook, Google, TikTok  
**Business Metrics:** Revenue, Orders, Customers, Profitability
""")

st.sidebar.markdown("---")
st.sidebar.markdown("*Built with Streamlit & Plotly*")