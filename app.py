import streamlit as st
import pandas as pd
import openai
import os
import plotly.express as px
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

def get_secret(key_name):
    """Safely fetch secret from environment variables (.env) or Streamlit secrets without throwing StreamlitSecretNotFoundError."""
    val = os.getenv(key_name)
    if val:
        return val
    try:
        return st.secrets.get(key_name)
    except Exception:
        return None

# --- PAGE CONFIGURATION ---
icon_path = "icon.png" if os.path.exists("icon.png") else "📊"
st.set_page_config(page_title="STAT AI", page_icon=icon_path, layout="wide")

# --- DARK GREEN FLAT THEME CSS ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }}
    
    /* Solid Page Background */
    .stApp {{
        background-color: #f4fbf7;
    }}
    
    /* Hero Header Banner - SOLID DARK GREEN (NO GRADIENTS) */
    .hero-banner {{
        background-color: #064e3b;
        border-radius: 14px;
        padding: 2.25rem 2rem;
        color: #ffffff;
        margin-bottom: 2rem;
        border: 1px solid #047857;
    }}
    
    .hero-title {{
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 0.5rem 0;
        line-height: 1.25;
    }}
    
    .hero-subtitle {{
        font-size: 1.05rem;
        color: #a7f3d0;
        max-width: 680px;
        margin: 0;
        line-height: 1.5;
    }}
    
    /* Stat Metric Cards - SOLID FLAT COLORS */
    .stat-card {{
        background-color: #ffffff;
        border: 1px solid #a7f3d0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        transition: all 0.2s ease;
    }}
    
    .stat-card:hover {{
        border-color: #059669;
    }}
    
    .stat-label {{
        font-size: 1.3rem;
        font-weight: 600;
        color: #047857;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    
    .stat-val {{
        font-size: 1.9rem;
        font-weight: 700;
        color: #064e3b;
        margin-top: 0.25rem;
        line-height: 1.1;
    }}
    
    .stat-sub {{
        font-size: 1rem;
        color: #059669;
        font-weight: 500;
        margin-top: 0.4rem;
    }}
    
    /* File Uploader Container Styling */
    [data-testid="stFileUploader"] {{
        border-radius: 12px;
        padding: 0.5rem;
        background-color: #ffffff;
        border: 1px solid #a7f3d0;
    }}

    /* Buttons - SOLID DARK GREEN (NO GRADIENTS) */
    .stButton>button {{
        background-color: #064e3b;
        color: #ffffff;
        font-weight: 600;
        font-size: 0.95rem;
        border-radius: 10px;
        padding: 0.65rem 1.75rem;
        border: 1px solid #047857;
        transition: all 0.2s ease;
    }}
    
    .stButton>button:hover {{
        background-color: #047857;
        color: #ffffff;
        border-color: #10b981;
    }}

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        border-bottom: 2px solid #a7f3d0;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 54px;
        border-radius: 8px 8px 0 0;
        font-weight: 700;
        font-size: 1.2rem;
        color: #064e3b;
        padding: 0 1.5rem;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: #064e3b !important;
        border-bottom: 3px solid #047857 !important;
        background-color: #ecfdf5;
    }}

    /* Footer Styling */
    .footer-container {{
        margin-top: 6rem;
        padding: 2.5rem 2rem 0.5rem 2rem;
        background-color: #064e3b;
        border-radius: 16px 16px 16px 16px;
        color: #ffffff;
        text-align: center;
        width: 100%;
    }}
    
    .footer-heading {{
        font-size: 5rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0 auto 0.75rem auto;
        text-align: center;
        letter-spacing: 0.025em;
    }}
    
    .footer-copyright {{
        font-size: 1.1rem;
        color: #a7f3d0;
        font-weight: 500;
        text-align: center;
        line-height: 1.6;
    }}

    .footer-copyright a {{
        color: #6ee7b7;
        font-weight: 500;
        text-decoration: none;
        transition: color 0.2s ease;
    }}

    .footer-copyright a:hover {{
        color: #ffffff;
    }}
    /* Selectbox & Radio — larger labels and option text */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stRadio"] label {{
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        color: #064e3b !important;
    }}

    div[data-testid="stSelectbox"] [data-baseweb="select"] span,
    div[data-testid="stSelectbox"] [data-baseweb="select"] div {{
        font-size: 1.05rem !important;
    }}

    [data-baseweb="menu"] li,
    [data-baseweb="menu"] [role="option"] {{
        font-size: 1.05rem !important;
    }}

    div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p,
    div[data-testid="stRadio"] span {{
        font-size: 1.05rem !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- HERO HEADER ---
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">AI-Powered Data Analysis for NGOs</div>
    <div class="hero-subtitle">Upload survey data from field studies or Google Forms to instantly surface key community bottlenecks, cross-analyzed trends, and strategic intervention plans.</div>
</div>
""", unsafe_allow_html=True)

# --- DATA UPLOAD SECTION ---
uploaded_file = st.file_uploader(
    "Upload Field Survey CSV File (Google Forms Export)",
    type=["csv"],
    help="Upload a CSV file that contains your survey data."
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        columns = df.columns.tolist()
        total_rows = len(df)
        total_cols = len(columns)
        
        # --- EXECUTIVE SUMMARY METRICS GRID ---
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total Responses</div>
                <div class="stat-val">{total_rows:,}</div>
                <div class="stat-sub">Completed Surveys</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Survey Variables</div>
                <div class="stat-val">{total_cols}</div>
                <div class="stat-sub">Questions Analyzed</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Analysis Status</div>
                <div class="stat-val">Ready</div>
                <div class="stat-sub">Dashboard Active</div>
            </div>
            """, unsafe_allow_html=True)
            
        # --- TABBED DASHBOARD ---
        tab_explorer, tab_crosstab, tab_ai = st.tabs([
            "📊 Data Explorer", 
            "🔀 Comparing Questions", 
            "💡 Strategic AI Insights"
        ])
        
        # TAB 1: DATA EXPLORER
        with tab_explorer:
            st.markdown("<p style='font-size:2rem; font-weight:700; color:#1a1a1a; margin-bottom:0.25rem;'>Community Response Breakdown</p>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:1.1rem; color:#555; margin-top:0; margin-bottom:1rem;'>Select any question from your survey to explore distribution metrics.</p>", unsafe_allow_html=True)
            
            c_sel, c_view = st.columns([3, 1])
            with c_sel:
                selected_question = st.selectbox("Select Survey Question:", columns, index=0)
            with c_view:
                chart_type = st.radio("Display Format:", ["Bar Chart", "Data Table"], horizontal=True)
                
            if selected_question:
                counts = df[selected_question].value_counts(dropna=False)
                pcts = (counts / len(df) * 100).round(1)
                breakdown_df = pd.DataFrame({"Count": counts, "Percentage (%)": pcts})
                
                if chart_type == "Bar Chart":
                    chart_df = pd.DataFrame({
                        "Response": counts.index.astype(str),
                        "Count": counts.values,
                        "Percentage": pcts.values
                    })
                    fig = px.bar(
                        chart_df,
                        x="Response",
                        y="Count",
                        custom_data=["Percentage"],
                        color_discrete_sequence=["#047857"]
                    )
                    fig.update_traces(
                        hovertemplate=(
                            "<b style='font-size:15px'>%{x}</b><br>"
                            "<span style='font-size:14px'>Count: <b>%{y}</b></span><br>"
                            "<span style='font-size:14px'>Share: <b>%{customdata[0]}%</b></span>"
                            "<extra></extra>"
                        ),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=14,
                            font_family="Plus Jakarta Sans, sans-serif",
                            bordercolor="#a7f3d0",
                            font_color="#000000"
                        )
                    )
                    fig.update_layout(
                        margin=dict(l=70, r=40, t=30, b=70),
                        plot_bgcolor="#f4fbf7",
                        paper_bgcolor="#f4fbf7",
                        xaxis=dict(
                            title=dict(text=selected_question, font=dict(size=18, color="#000000", family="Plus Jakarta Sans")),
                            tickfont=dict(size=15, color="#000000", family="Plus Jakarta Sans"),
                            tickangle=0,
                            automargin=True,
                            showgrid=False,
                            linecolor="#000000",
                            linewidth= 3
                        ),
                        yaxis=dict(
                            title=dict(text="Number of Responses", font=dict(size=18, color="#000000", family="Plus Jakarta Sans")),
                            tickfont=dict(size=15, color="#000000", family="Plus Jakarta Sans"),
                            gridcolor="#a5b5ac",
                            gridwidth=1,
                            linecolor="#000000",
                            linewidth= 3
                        ),
                        height=440,
                        bargap=0.3
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(breakdown_df, use_container_width=True)
                    
                st.markdown("<p style='font-size:2rem; font-weight:700; color:#064e3b; margin-top:0.75rem;'>Quick Insights:</p>", unsafe_allow_html=True)
                top_response = counts.index[0] if len(counts) > 0 else "N/A"
                top_pct = pcts.iloc[0] if len(pcts) > 0 else 0
                st.info(f"**Top Finding:** Most frequent response for '{selected_question}' is **{top_response}** which is {top_pct}% of the total participants.")

        # TAB 2: CROSS ANALYSIS MATRIX
        with tab_crosstab:
            st.markdown("<p style='font-size:2rem; font-weight:700; color:#1a1a1a; margin-bottom:0.1rem;'>Comparing Variables</p>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:1.1rem; color:#555; margin-top:0; margin-bottom:1rem;'>Compare two survey questions to discover hidden trends</p>", unsafe_allow_html=True)
            
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                question_1 = st.selectbox("Select Question:", columns, index=0, key="q1_cross")
            with col_q2:
                question_2 = st.selectbox("Compare with:", columns, index=1 if len(columns) > 1 else 0, key="q2_cross")
                
            if question_1 and question_2 and question_1 != question_2:
                crosstab = pd.crosstab(df[question_1], df[question_2], margins=True, margins_name="Total")
                st.markdown(f"**Cross-Tabulation: `{question_1}` vs `{question_2}`**")
                st.dataframe(crosstab, use_container_width=True)
            elif question_1 == question_2:
                st.warning("Please select two distinct questions for cross-analysis.")

        # TAB 3: AI Insights
        with tab_ai:
            st.markdown("<p style='font-size:2rem; font-weight:700; color:#1a1a1a; margin-bottom:0.1rem;'>Strategic AI Insights</p>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:1.1rem; color:#555; margin-top:0; margin-bottom:1rem;'>Generate a detailed survey analysis and targeted NGO intervention plan based on the uploaded data.</p>", unsafe_allow_html=True)
            
            # Fetch server API key
            active_key = get_secret("GROQ_API_KEY")
            
            if st.button("Generate AI Insights Report"):
                if not active_key:
                    st.error("⚠️ No active API Key found on server. Please configure your `.env` file or environment variables.")
                else:
                    with st.spinner("Processing field data & generating AI briefing..."):
                        clean_key = active_key.strip()
                        
                        # Build summary
                        col_summaries = []
                        for col in columns[:6]:
                            top_vals = df[col].value_counts(dropna=False).head(5).to_dict()
                            col_summaries.append(f"- Column '{col}': {top_vals}")
                        
                        data_summary = f"""
Total Community Responses: {len(df)}
Survey Questions/Variables ({len(df.columns)}): {list(df.columns)}
Key Response Distributions:
""" + "\n".join(col_summaries)
                        
                        prompt = f"""
You are a senior humanitarian data analyst working for an international non-governmental organization (NGO).
Analyze the following community assessment survey data summary and write a clear, professional Executive Briefing Report formatted in Markdown.

Data Summary:
{data_summary}

Please structure your output into these 3 sections:
1. Strategic Summary & Key Insights: Highlight the 2 most critical systemic issues or community bottlenecks evident in the data.
2. Impactful NGO Intervention: Propose 1 specific, high-leverage field intervention that an NGO can immediately launch to address these bottlenecks. Include key success metrics.
3. Resource Managment Guidance: Provide 2 practical tips on how field teams should allocate resources.
"""
                        ai_insights = None
                        error_detail = None
                        
                        # 1. Groq Route (gsk_)
                        if clean_key.startswith("gsk_"):
                            try:
                                client = openai.OpenAI(api_key=clean_key, base_url="https://api.groq.com/openai/v1")
                                for model_name in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]:
                                    try:
                                        res = client.chat.completions.create(
                                            model=model_name,
                                            messages=[{"role": "system", "content": "You are a professional NGO data analyst."}, {"role": "user", "content": prompt}]
                                        )
                                        ai_insights = res.choices[0].message.content
                                        break
                                    except Exception as err:
                                        error_detail = str(err)
                            except Exception as e:
                                error_detail = str(e)
                        
                        if ai_insights:
                            st.success("AI Analysis Generated Successfully!")
                            st.divider()
                            st.markdown(ai_insights)
                            st.divider()
                        else:
                            st.error("❌ Analysis generation failed.")
                            if error_detail:
                                st.warning(f"Error Details: {error_detail}")

    except Exception as e:
        st.error(f"Error loading survey file: {e}")

else:
    st.error("Please upload a survey CSV file above to launch your interactive dashboard and AI insights.")

# --- FOOTER ---
st.markdown("""
<div class="footer-container">
    <div class="footer-heading">welcome to STAT AI</div>
    <div class="footer-copyright">
        © 2026 STAT AI. All rights reserved. Developed by <a href="https://github.com/real-Nemo1215" target="_blank" rel="noopener noreferrer">@real-Nemo1215</a>
    </div>
</div>
""", unsafe_allow_html=True)