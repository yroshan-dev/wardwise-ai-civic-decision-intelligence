import streamlit as st
import pandas as pd
import plotly.express as px
import os
import datetime
import base64
from dotenv import load_dotenv

# Set page config
st.set_page_config(
    page_title="WardWise AI - Civic Decision Intelligence",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables dynamically based on file location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "wardwise_logo.png")

security_env_path = os.path.join(BASE_DIR, "security.env")
if os.path.exists(security_env_path):
    load_dotenv(security_env_path, override=True)
else:
    load_dotenv(override=True)

# Helper to fetch configuration from environment variables or Streamlit secrets
def get_env_or_secret(key, default=""):
    val = os.getenv(key)
    if val is not None:
        return val
    try:
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default

GEMINI_API_KEY = get_env_or_secret("GEMINI_API_KEY", "").strip()

# BigQuery configuration
USE_BIGQUERY_VAL = get_env_or_secret("USE_BIGQUERY", "false")
USE_BIGQUERY = USE_BIGQUERY_VAL.lower() == "true"
GOOGLE_CLOUD_PROJECT = get_env_or_secret("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0853737784")
BIGQUERY_DATASET = get_env_or_secret("BIGQUERY_DATASET", "wardwise_ai")
BIGQUERY_TABLE = get_env_or_secret("BIGQUERY_TABLE", "civic_complaints")

# Custom CSS for clean layout spacing and subtle improvements
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    /* Global font family */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Subtle container formatting */
    .insight-card {
        border-left: 4px solid #0284c7;
        border-top: 1px solid rgba(128, 128, 128, 0.2);
        border-right: 1px solid rgba(128, 128, 128, 0.2);
        border-bottom: 1px solid rgba(128, 128, 128, 0.2);
        padding: 16px;
        border-radius: 8px;
        margin-top: 15px;
        margin-bottom: 25px;
        background-color: rgba(2, 132, 199, 0.05); /* Transparent tint matching accent color */
    }



    /* Table adjustments */
    .stDataFrame {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to generate styled metric cards
def make_metric_card(title, value, subtitle=None):
    sub_html = f"<div style='font-size:11.5px; opacity: 0.8; margin-top:4px; line-height: 1.2;'>{subtitle}</div>" if subtitle else ""
    # Theme-adaptive layout by using semi-transparent background and border colors
    card_html = f'<div style="background-color: rgba(128, 128, 128, 0.05); border-radius: 12px; padding: 20px; border: 1px solid rgba(128, 128, 128, 0.2); text-align: center; margin-bottom: 15px; min-height: 130px; display: flex; flex-direction: column; justify-content: center; align-items: center;"><div style="font-size: 12px; color: #0284c7; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; min-height: 24px; display: flex; align-items: center; justify-content: center;">{title}</div><div style="font-size: 26px; font-weight: 700; margin-top: 8px; line-height: 1.1;">{value}</div>{sub_html}</div>'
    st.markdown(card_html, unsafe_allow_html=True)

# Helper function for custom Plotly layout styling
def apply_plotly_theme(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="'Outfit', sans-serif",
        title_font_family="'Outfit', sans-serif",
        title_font_size=15,
        title_x=0.0,
        legend=dict(
            bgcolor='rgba(128, 128, 128, 0.05)',
            bordercolor='rgba(128, 128, 128, 0.2)',
            borderwidth=1,
            font=dict(size=11)
        ),
        xaxis=dict(
            showgrid=False, 
            linecolor='rgba(128, 128, 128, 0.2)',
            tickfont=dict(size=11),
            title=dict(font=dict(size=12))
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(128, 128, 128, 0.1)', 
            linecolor='rgba(128, 128, 128, 0.2)',
            tickfont=dict(size=11),
            title=dict(font=dict(size=12))
        ),
        margin=dict(l=30, r=20, t=40, b=30),
        height=320
    )
    # Hide color scale bars automatically
    fig.update_coloraxes(showscale=False)
    # Clean bar chart border lines
    fig.update_traces(marker_line_color='rgba(0,0,0,0)', selector=dict(type='bar'))
    return fig

# Reusable helper function to render unified header across all pages
def render_page_header(badge_text, subtitle_text):
    # Header Component (Visual Branding with Logo) - preserved from V1 logo implementation
    logo_html = ""
    if os.path.exists(LOGO_PATH):
        try:
            with open(LOGO_PATH, "rb") as img_file:
                logo_base64 = base64.b64encode(img_file.read()).decode()
            # Larger logo filling the space better
            logo_html = f'<div style="background: white; padding: 3px; border-radius: 8px; display: flex; align-items: center; justify-content: center; height: 55px; width: 90px; min-width: 90px;"><img src="data:image/png;base64,{logo_base64}" style="max-height: 49px; max-width: 84px; object-fit: contain;"></div>'
        except Exception:
            logo_html = ""

    page_chip = f'<span style="background-color: rgba(2, 132, 199, 0.1); color: #0284c7; border: 1px solid rgba(2, 132, 199, 0.3); padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">{badge_text}</span>'

    hero_html = f'<div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(128, 128, 128, 0.2);">{logo_html}<div><div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;"><h1 style="margin: 0; font-size: 28px; font-weight: 800; letter-spacing: -0.025em; line-height: 1.1;">WardWise AI</h1>{page_chip}</div><p style="margin: 5px 0 0 0; font-size: 13.5px; opacity: 0.8; line-height: 1.3;">{subtitle_text}</p></div></div>'

    st.markdown(hero_html, unsafe_allow_html=True)

# --- BigQuery or CSV Data Loading Pipeline (Cached) ---
@st.cache_data(ttl=600, show_spinner="Loading civic complaint data...")
def load_data_cached(use_bq, project, dataset, table, base_dir):
    source = "CSV fallback"
    err_msg = None
    df_raw_loc = None
    
    if use_bq:
        try:
            from google.cloud import bigquery
            # Create BigQuery client. Uses Application Default Credentials (ADC)
            bq_client = bigquery.Client(project=project)
            
            # Build query targeting the BigQuery table
            query = f"SELECT * FROM `{project}.{dataset}.{table}`"
            
            # Execute query and load results into a pandas DataFrame
            df_raw_loc = bq_client.query(query).to_dataframe()
            source = "BigQuery"
        except Exception as e:
            err_msg = str(e)
            source = "CSV fallback"
    else:
        source = "CSV fallback"

    # Fallback to local CSV if BigQuery is disabled or if the query failed
    if source == "CSV fallback":
        csv_path = os.path.join(base_dir, "data", "civic_complaints.csv")
        if not os.path.exists(csv_path):
            return None, source, f"Missing local CSV at {csv_path}", None
        try:
            df_raw_loc = pd.read_csv(csv_path)
        except Exception as csv_err:
            return None, source, f"CSV loading failed: {csv_err}", None
            
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df_raw_loc, source, err_msg, timestamp

# Run the cached load function
df_raw, data_source, bq_error_msg, load_timestamp = load_data_cached(
    USE_BIGQUERY, GOOGLE_CLOUD_PROJECT, BIGQUERY_DATASET, BIGQUERY_TABLE, BASE_DIR
)

if df_raw is None:
    st.error(f"⚠️ Critical error loading dataset: {bq_error_msg}")
    st.stop()

# --- Data Processing and Scoring Pipeline ---
df = df_raw.copy()

# 1. Severity points: High=50, Medium=30, Low=10
severity_points_map = {'High': 50, 'Medium': 30, 'Low': 10}
df['severity_points'] = df['severity'].map(severity_points_map).fillna(10)

# 2. Repeated ward-category issue: +5 points per complaint in same ward and category
group_counts = df.groupby(['ward', 'category']).size().reset_index(name='repeat_count')
df = df.merge(group_counts, on=['ward', 'category'], how='left')
df['repeat_points'] = df['repeat_count'] * 5

# 3. Response delay points: delay >= 24 hours = +20 points, below 24 hours = +5 points
df['delay_points'] = df['response_time_hours'].apply(lambda x: 20 if x >= 24 else 5)

# Calculate total priority score
df['priority_score'] = df['severity_points'] + df['repeat_points'] + df['delay_points']

# Categorize level: Critical if >= 85, High if >= 65, Medium otherwise
def get_priority_level(score):
    if score >= 85:
        return 'Critical'
    elif score >= 65:
        return 'High'
    else:
        return 'Medium'

df['priority_level'] = df['priority_score'].apply(get_priority_level)

# Suggested action logic
action_map = {
    'Waste': 'Assign extra collection vehicle and inspect missed pickup route.',
    'Drainage': 'Send maintenance team for blockage inspection and cleaning.',
    'Water': 'Check supply line and update affected residents.',
    'Transport': 'Review peak-hour route frequency and crowding points.',
    'Streetlights': 'Schedule electrical repair team for night safety risk.',
    'Healthcare': 'Review clinic load and arrange temporary support if needed.',
    'Safety': 'Escalate to local safety team for area inspection.'
}
df['suggested_action'] = df['category'].map(action_map).fillna('Schedule inspection and follow up.')


# --- SIDEBAR NAV & SYSTEM INFO ---
if os.path.exists(LOGO_PATH):
    try:
        with open(LOGO_PATH, "rb") as img_file:
            sidebar_logo_base64 = base64.b64encode(img_file.read()).decode()
        # White container box for logo readability in dark sidebar
        st.sidebar.markdown(f'<div style="background: white; padding: 8px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px;"><img src="data:image/png;base64,{sidebar_logo_base64}" style="max-height: 70px; max-width: 100%; object-fit: contain;"></div>', unsafe_allow_html=True)
    except Exception:
        st.sidebar.image(LOGO_PATH, use_container_width=True)
    st.sidebar.markdown("""
    <div style="text-align: center; padding-bottom: 20px; margin-top: -5px; border-bottom: 1px solid rgba(128, 128, 128, 0.2);">
        <span style="font-size: 11px; opacity: 0.75; font-weight:500; letter-spacing:0.05em; text-transform:uppercase;">Decision Intelligence</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div style="margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(128, 128, 128, 0.2);">
        <h3 style="margin: 0; font-size: 20px; font-weight: 800; letter-spacing: -0.01em; line-height: 1.2;">WardWise AI</h3>
        <span style="font-size: 9.5px; opacity: 0.75; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-top: 2px;">Civic Assistant</span>
    </div>
    """, unsafe_allow_html=True)

# Sidebar Navigation
page = st.sidebar.radio(
    "Navigate Platform:",
    ["Dashboard", "Hotspot Analysis", "Priority Triage", "AI Decision Brief"]
)

# Data Source Status Badge with Cache Timestamp
if data_source == "BigQuery":
    badge_html = f'<div style="background-color: rgba(6, 78, 59, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; text-align: center; margin-top: 15px; margin-bottom: 2px;">🟢 BigQuery Source</div><div style="font-size: 10px; opacity: 0.8; text-align: center; margin-bottom: 15px;">Loaded: {load_timestamp}</div>'
    st.sidebar.markdown(badge_html, unsafe_allow_html=True)
else:
    badge_html = f'<div style="background-color: rgba(69, 26, 3, 0.15); color: #fcd34d; border: 1px solid rgba(252, 211, 77, 0.3); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; text-align: center; margin-top: 15px; margin-bottom: 2px;">🟡 CSV Fallback Source</div><div style="font-size: 10px; opacity: 0.8; text-align: center; margin-bottom: 15px;">Loaded: {load_timestamp}</div>'
    st.sidebar.markdown(badge_html, unsafe_allow_html=True)

# Demo Mode Info Box inside expander
with st.sidebar.expander("⚙️ System Demo Mode"):
    st.markdown("""
    This prototype uses sample civic complaint data to demonstrate how AI can support civic decision-making. 
    In production, the data layer can be connected to BigQuery and public-service systems.
    """)

# Prototype Information
with st.sidebar.expander("📋 Prototype Information"):
    st.markdown("""
    **System Purpose:**
    This evaluation checklist demonstrates key platform capabilities:
    
    **1. Real User:**
    - City officer, ward administrator, or NGO coordinator who prioritizes civic resources.
    
    **2. Decision Bottleneck:**
    - Manually reading hundreds of unstructured complaints; lack of clear hotspot identification or priority rankings.
    
    **3. Data Pipeline:**
    - BigQuery / CSV fallback -> Loading & Clean -> Priority Scoring -> Hotspot Analytics -> Gemini AI Brief.
    
    **4. Useful Output:**
    - Automated severity priority score, immediate recommended actions, and structured briefs.
    
    **5. Acceleration Proof:**
    - Replaces slow, manual inspection with prioritized issue triage and auto-briefing, reducing review time from hours to seconds.
    """)

# Show BigQuery loading failure warning banner if applicable
if USE_BIGQUERY and data_source == "CSV fallback" and bq_error_msg:
    st.warning(f"⚠️ BigQuery loading failed. Falling back to local CSV. Error details: {bq_error_msg}")


# --- 1. DASHBOARD PAGE ---
if page == "Dashboard":
    render_page_header("DASHBOARD", "Civic Decision Intelligence Platform — prioritize ward complaints, detect hotspots, and generate action insights.")
    # Workflow Strip
    st.markdown("""
    <div style="
        background-color: rgba(128, 128, 128, 0.05); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 8px; 
        padding: 10px 16px; 
        margin-bottom: 25px; 
        display: flex; 
        justify-content: space-between; 
        align-items: center;
    ">
        <div style="font-size: 12px; font-weight: 700; color: #0284c7; text-transform: uppercase; letter-spacing: 0.05em;">🔄 Operations Pipeline:</div>
        <div style="display: flex; align-items: center; gap: 8px; font-size: 12.5px; font-weight: 500;">
            <span style="background-color: rgba(128, 128, 128, 0.1); padding: 3px 10px; border-radius: 12px; font-weight: 600; border: 1px solid rgba(128, 128, 128, 0.2);">Complaint Intake</span>
            <span style="opacity: 0.5; font-weight: bold;">➔</span>
            <span style="background-color: rgba(128, 128, 128, 0.1); padding: 3px 10px; border-radius: 12px; font-weight: 600; border: 1px solid rgba(128, 128, 128, 0.2);">AI Cleaning</span>
            <span style="opacity: 0.5; font-weight: bold;">➔</span>
            <span style="background-color: rgba(128, 128, 128, 0.1); padding: 3px 10px; border-radius: 12px; font-weight: 600; border: 1px solid rgba(128, 128, 128, 0.2);">Priority Scoring</span>
            <span style="opacity: 0.5; font-weight: bold;">➔</span>
            <span style="background-color: rgba(128, 128, 128, 0.1); padding: 3px 10px; border-radius: 12px; font-weight: 600; border: 1px solid rgba(128, 128, 128, 0.2);">Officer Action</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("Welcome to the platform coordinator dashboard. Below is the summarized view of current community complaints, triage metrics, and operational performance.")

    # Calculate key metrics
    total_complaints = len(df)
    high_critical_count = len(df[df['priority_level'].isin(['Critical', 'High'])])
    most_affected_ward = df['ward'].value_counts().idxmax()
    most_affected_ward_count = df['ward'].value_counts().max()
    top_category = df['category'].value_counts().idxmax()
    top_category_count = df['category'].value_counts().max()
    avg_delay = df['response_time_hours'].mean()

    # Metric Cards Columns (4 columns as requested)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        make_metric_card("Total Complaints", f"{total_complaints}", "Total logged in period")
    with m_col2:
        make_metric_card("High Priority", f"{high_critical_count}", f"{high_critical_count/total_complaints*100:.1f}% of total cases")
    with m_col3:
        pending_review = len(df[df['status'].isin(['Open', 'In Progress'])])
        make_metric_card("Pending Review", f"{pending_review}", "Awaiting dispatch action")
    with m_col4:
        top_category_count = df['category'].value_counts().max()
        make_metric_card("Top Issue Category", f"{top_category}", f"{top_category_count} reported cases")

    # "What this means" narrative block (adaptive styling)
    st.markdown(f"""
    <div class="insight-card">
        <div style="font-weight: 700; color: #0284c7; font-size: 15px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">💡 Civic Insight Summary</div>
        <div style="font-size: 13.5px; line-height: 1.8; margin: 0;">
            <div style="margin-bottom: 8px;">• Total active complaints logged in period: <strong>{total_complaints}</strong></div>
            <div style="margin-bottom: 8px;">• Triage cases categorized as High/Critical: <strong style="color: #0284c7;">{high_critical_count}</strong> ({high_critical_count/total_complaints*100:.1f}%)</div>
            <div style="margin-bottom: 8px;">• Main geographic hotspot detected: <strong>{most_affected_ward}</strong></div>
            <div style="margin-bottom: 8px;">• Leading issue category across wards: <strong>{top_category}</strong></div>
            <div>• Average response action latency: <strong>{avg_delay:.1f} hours</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mini Table of Recent Critical Complaints
    st.subheader("⚠️ Top 5 Urgent Complaints Requiring Attention")
    critical_df = df[df['priority_level'] == 'Critical'].sort_values(by='priority_score', ascending=False).head(5)
    
    st.dataframe(
        critical_df[['complaint_id', 'ward', 'category', 'description', 'severity', 'response_time_hours', 'priority_score', 'suggested_action']],
        column_config={
            "complaint_id": "ID",
            "ward": "Ward",
            "category": "Category",
            "description": "Description",
            "severity": "Severity",
            "response_time_hours": "Delay (hrs)",
            "priority_score": "Score",
            "suggested_action": "Recommended Immediate Action"
        },
        hide_index=True,
        use_container_width=True
    )


# --- 2. HOTSPOT ANALYSIS PAGE ---
elif page == "Hotspot Analysis":
    render_page_header("HOTSPOT ANALYSIS", "Identify ward-level complaint clusters, recurring issue zones, and geographic pressure points.")

    # 2x2 Columns for Charts
    c_col1, c_col2 = st.columns(2)

    with c_col1:
        # Chart 1: Complaints by Ward
        ward_counts = df['ward'].value_counts().reset_index(name='count')
        fig_ward = px.bar(
            ward_counts, 
            x='ward', 
            y='count', 
            title='Total Complaints by Ward',
            labels={'ward': 'Ward ID', 'count': 'Complaints'},
            color_discrete_sequence=['#38bdf8']
        )
        fig_ward.update_xaxes(tickangle=0)
        st.plotly_chart(apply_plotly_theme(fig_ward), use_container_width=True)

    with c_col2:
        # Chart 2: Complaints by Category (sorted ascending so horizontal bars order correctly)
        cat_counts = df['category'].value_counts().reset_index(name='count')
        fig_cat = px.bar(
            cat_counts, 
            x='count', 
            y='category', 
            title='Complaints by Category',
            orientation='h',
            labels={'category': 'Category', 'count': 'Complaints'},
            color_discrete_sequence=['#0ea5e9']
        )
        fig_cat.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(apply_plotly_theme(fig_cat), use_container_width=True)

    c_col3, c_col4 = st.columns(2)

    with c_col3:
        # Chart 3: Severity Distribution (Donut style with explicit mapped colors)
        sev_counts = df['severity'].value_counts().reset_index(name='count')
        fig_sev = px.pie(
            sev_counts, 
            values='count', 
            names='severity', 
            title='Severity Distribution',
            hole=0.5,
            color='severity',
            color_discrete_map={'High': '#ef4444', 'Medium': '#f59e0b', 'Low': '#3b82f6'}
        )
        st.plotly_chart(apply_plotly_theme(fig_sev), use_container_width=True)

    with c_col4:
        # Chart 4: Average Response Delay by Ward
        delay_ward = df.groupby('ward')['response_time_hours'].mean().reset_index(name='avg_delay')
        fig_delay = px.bar(
            delay_ward, 
            x='ward', 
            y='avg_delay', 
            title='Average Response Delay by Ward (Hours)',
            labels={'ward': 'Ward ID', 'avg_delay': 'Avg Delay (Hours)'},
            color_discrete_sequence=['#6366f1']
        )
        fig_delay.update_xaxes(tickangle=0)
        st.plotly_chart(apply_plotly_theme(fig_delay), use_container_width=True)

    # Narrative Interpretation Cards
    st.subheader("📊 Hotspot Interpretation")
    i_col1, i_col2, i_col3 = st.columns(3)
    
    # Calculate values for interpretation cards
    most_affected_ward = df['ward'].value_counts().idxmax()
    most_affected_ward_count = df['ward'].value_counts().max()
    top_category = df['category'].value_counts().idxmax()
    top_category_count = df['category'].value_counts().max()
    
    delay_ward_series = df.groupby('ward')['response_time_hours'].mean()
    highest_delay_ward = delay_ward_series.idxmax()
    highest_delay_value = delay_ward_series.max()

    with i_col1:
        st.markdown(f"""
        <div class="insight-card" style="border-left-color: #38bdf8; margin: 0; min-height: 120px;">
            <div style="font-weight: 700; color: #38bdf8; font-size: 13.5px; margin-bottom: 4px;">📍 Main Hotspot Ward</div>
            <div style="font-size: 18px; font-weight: 700; margin-bottom: 2px;">{most_affected_ward}</div>
            <div style="opacity: 0.75; font-size: 11.5px;">{most_affected_ward_count} complaints logged in this region.</div>
        </div>
        """, unsafe_allow_html=True)

    with i_col2:
        st.markdown(f"""
        <div class="insight-card" style="border-left-color: #0ea5e9; margin: 0; min-height: 120px;">
            <div style="font-weight: 700; color: #0ea5e9; font-size: 13.5px; margin-bottom: 4px;">🏷️ Top Issue Category</div>
            <div style="font-size: 18px; font-weight: 700; margin-bottom: 2px;">{top_category}</div>
            <div style="opacity: 0.75; font-size: 11.5px;">{top_category_count} reported cases across all wards.</div>
        </div>
        """, unsafe_allow_html=True)

    with i_col3:
        st.markdown(f"""
        <div class="insight-card" style="border-left-color: #6366f1; margin: 0; min-height: 120px;">
            <div style="font-weight: 700; color: #6366f1; font-size: 13.5px; margin-bottom: 4px;">⏳ Highest Average Delay</div>
            <div style="font-size: 18px; font-weight: 700; margin-bottom: 2px;">{highest_delay_ward}</div>
            <div style="opacity: 0.75; font-size: 11.5px;">Average dispatch latency of {highest_delay_value:.1f} hours.</div>
        </div>
        """, unsafe_allow_html=True)


# --- 3. PRIORITY TRIAGE PAGE ---
elif page == "Priority Triage":
    render_page_header("PRIORITY TRIAGE", "Rank civic complaints by urgency, severity, and operational action priority.")

    # Scoring Rule Explainer
    with st.expander("ℹ️ How the Priority Score is Calculated", expanded=False):
        st.markdown("""
        To make prioritization transparent and explainable, we calculate a score for each complaint based on three pillars:
        1. **Severity Points:**
           - `High` severity: **50 points**
           - `Medium` severity: **30 points**
           - `Low` severity: **10 points**
        2. **Repeated Issue Penalty:**
           - **+5 points** for *each* complaint in the database sharing the same Ward and Category (e.g. if Ward 6 has 10 Waste complaints, each gets +50 points).
        3. **Response Time Delay Penalty:**
           - Response delay is greater than or equal to 24 hours: **+20 points**
           - Response delay is less than 24 hours: **+5 points**
        
        **Priority Levels:**
        - **Critical Priority:** Score $\ge$ 85
        - **High Priority:** Score $\ge$ 65
        - **Medium Priority:** Score < 65
        """)

    # Interactive Filters
    st.subheader("Filter and Inspect Complaints")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        wards = sorted(df['ward'].unique())
        selected_wards = st.multiselect("Select Wards:", options=wards, default=wards)
    with f_col2:
        categories = sorted(df['category'].unique())
        selected_categories = st.multiselect("Select Categories:", options=categories, default=categories)
    with f_col3:
        levels = ['Critical', 'High', 'Medium']
        selected_levels = st.multiselect("Select Priority Levels:", options=levels, default=levels)

    # Filter dataframe
    filtered_df = df[
        (df['ward'].isin(selected_wards)) &
        (df['category'].isin(selected_categories)) &
        (df['priority_level'].isin(selected_levels))
    ].sort_values(by='priority_score', ascending=False)

    # Render table
    st.write(f"Showing **{len(filtered_df)}** complaints matching current filters:")
    
    st.dataframe(
        filtered_df[[
            'complaint_id', 'ward', 'category', 'description', 'date', 
            'severity', 'response_time_hours', 'priority_score', 
            'priority_level', 'suggested_action'
        ]],
        column_config={
            "complaint_id": "ID",
            "ward": "Ward",
            "category": "Category",
            "description": st.column_config.TextColumn("Description", width="medium"),
            "date": "Date",
            "severity": "Severity",
            "response_time_hours": st.column_config.NumberColumn("Delay (hrs)", format="%d"),
            "priority_score": st.column_config.ProgressColumn("Priority Score", min_value=0, max_value=130, format="%d"),
            "priority_level": st.column_config.SelectboxColumn("Priority Level"),
            "suggested_action": st.column_config.TextColumn("Suggested Action", width="large")
        },
        hide_index=True,
        use_container_width=True
    )


# --- 4. AI DECISION BRIEF PAGE ---
elif page == "AI Decision Brief":
    render_page_header("AI DECISION BRIEF", "Generate officer-ready summaries, local risk insights, and civic action recommendations.")
    col_left, col_mid, col_right = st.columns([1, 6, 1])
    with col_mid:
        # Check for GEMINI_API_KEY
        if not GEMINI_API_KEY:
            st.markdown("""
            <div style="
                background-color: #1e1b1b;
                color: #fca5a5;
                border: 1px solid #7f1d1d;
                padding: 16px;
                border-radius: 8px;
                margin-top: 10px;
                margin-bottom: 25px;
                font-size: 13.5px;
                line-height: 1.5;
            ">
                <strong>⚠️ Gemini API Key Missing</strong><br>
                The dashboard and hotspot analysis pages remain fully functional. 
                To enable AI briefs, please create a local <code>security.env</code> file and add <code>GEMINI_API_KEY=your_actual_key_here</code>.
            </div>
            """, unsafe_allow_html=True)
        else:
            # Non-sensitive status message showing key length for debugging
            st.markdown(f"""
            <div style="font-size: 11.5px; opacity: 0.75; margin-top: -10px; margin-bottom: 20px; text-align: center;">
                ⚡ Gemini Service Status: <strong>Ready</strong> | Key Length: <strong>{len(GEMINI_API_KEY)} chars</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Centered assistant prompts and inquiry panel
            
            # Preset Prompts as buttons
            st.write("💡 **Suggested Prompts:**")
            p_col1, p_col2 = st.columns(2)
            query_to_run = None
            
            with p_col1:
                if st.button("📋 Generate a decision brief for the city officer", use_container_width=True):
                    query_to_run = "Generate a decision brief for the city officer."
                if st.button("🚨 Which ward needs the most urgent attention today?", use_container_width=True):
                    query_to_run = "Which ward needs the most urgent attention today?"
            with p_col2:
                if st.button("📊 What are the top 3 civic issues?", use_container_width=True):
                    query_to_run = "What are the top 3 civic issues?"
                if st.button("⚠️ Which issue may get worse if ignored?", use_container_width=True):
                    query_to_run = "Which issue may get worse if ignored?"
            
            # Text area for custom question and action button
            st.write("💬 **Custom Inquiry:**")
            custom_question = st.text_area("Type your question below...", height=100, label_visibility="collapsed", placeholder="Ask a custom question about the complaints...")
            
            if st.button("🚀 Generate AI Brief", use_container_width=True):
                if not custom_question.strip():
                    st.error("Please enter a question first.")
                else:
                    query_to_run = custom_question.strip()
            
            # Generate Data Summary Text for Gemini Context
            def generate_data_summary(dataframe):
                total_cases = len(dataframe)
                ward_distribution = dataframe['ward'].value_counts().to_dict()
                category_distribution = dataframe['category'].value_counts().to_dict()
                critical_cases = len(dataframe[dataframe['priority_level'] == 'Critical'])
                high_cases = len(dataframe[dataframe['priority_level'] == 'High'])
                avg_response_time = dataframe['response_time_hours'].mean()

                # Top 6 most urgent complaints
                urgent_rows = dataframe.sort_values(by='priority_score', ascending=False).head(6)
                urgent_str_list = []
                for _, r in urgent_rows.iterrows():
                    urgent_str_list.append(
                        f"- ID: {r['complaint_id']} | Ward: {r['ward']} | Category: {r['category']} | Severity: {r['severity']} | Response Delay: {r['response_time_hours']} hrs | Score: {r['priority_score']} | Desc: {r['description']}"
                    )
                urgent_text_summary = "\n".join(urgent_str_list)

                return f"""
                Civic Complaint Data Statistics:
                - Total Complaints Logged: {total_cases}
                - Complaints by Ward: {ward_distribution}
                - Complaints by Category: {category_distribution}
                - Critical Level Cases: {critical_cases}
                - High Level Cases: {high_cases}
                - Average Response Delay: {avg_response_time:.1f} hours

                Top 6 Most Urgent Complaints (Highest Priority Scores):
                {urgent_text_summary}
                """

            # Run query if set
            if query_to_run:
                # Display query in user style block
                with st.chat_message("user"):
                    st.markdown(f"**{query_to_run}**")
                
                # Display response in assistant message container
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing complaints and drafting AI decision brief..."):
                        data_summary = generate_data_summary(df)
                        
                        system_instructions = """You are WardWise AI, a civic decision intelligence assistant.
Use only the complaint data summary provided.
Do not invent exact facts outside the data.
Give practical, decision-focused advice for city officials or community teams.

Every answer should include:
- Situation summary
- Evidence from data
- Recommended action
- Expected impact
- Risk if ignored

The AI output should be formatted cleanly with headings and short paragraphs."""

                        prompt_content = f"""
{system_instructions}

---
CONTEXT COMPLAINT DATA SUMMARY:
{data_summary}
---

USER QUESTION: {query_to_run}
"""
                        try:
                            from google import genai
                            api_key = os.getenv("GEMINI_API_KEY", "").strip()
                            client = genai.Client(api_key=api_key)
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=prompt_content,
                            )
                            # Render output
                            st.success("Brief generated successfully!")
                            st.markdown(response.text)
                        except Exception as err:
                            st.error(f"Failed to communicate with Gemini API: {err}")
                            st.info("Check your API key validity, network connectivity, and project credentials.")
