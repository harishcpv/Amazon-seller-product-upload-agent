"""Custom CSS and Amazon Seller Central styling for Amazon AutoList Studio."""

import streamlit as st


def apply_custom_styles():
    """Injects custom CSS styling mimicking Amazon Seller Central."""
    st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Top Navigation Banner */
    .seller-header {
        background: linear-gradient(135deg, #131921 0%, #232F3E 100%);
        color: #FFFFFF;
        padding: 1.25rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .seller-header h1 {
        color: #FFFFFF;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .seller-header .brand-pill {
        background: #FF9900;
        color: #111111;
        font-weight: 700;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Amazon Seller Central Card */
    .amazon-card {
        background: #FFFFFF;
        border: 1px solid #D5D9D9;
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .amazon-card:hover {
        border-color: #A6C8E0;
        box-shadow: 0 3px 8px rgba(0,0,0,0.08);
    }
    .amazon-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #EAEAEA;
        padding-bottom: 0.75rem;
        margin-bottom: 1rem;
    }
    .amazon-card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F1111;
        margin: 0;
    }

    /* Status Badges */
    .badge-success {
        background-color: #E7F4EA;
        color: #067D62;
        border: 1px solid #B8E4C9;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }
    .badge-warning {
        background-color: #FFF3CD;
        color: #856404;
        border: 1px solid #FFEEBA;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-brand {
        background-color: #FFF4E5;
        color: #B12704;
        border: 1px solid #FFD8A8;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }

    /* Metric Stat Box */
    .metric-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-box {
        flex: 1;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0F1111;
        margin-bottom: 0.2rem;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #565959;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Button Primary (Amazon Orange) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(to bottom, #FFA41C, #FF8F00);
        border: 1px solid #FF8F00;
        color: #0F1111;
        font-weight: 600;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(213, 103, 0, 0.2);
        transition: all 0.15s ease-in-out;
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(to bottom, #FA8900, #E07B00);
        border-color: #D37400;
        color: #000000;
        transform: translateY(-1px);
    }

    /* Button Secondary */
    div.stButton > button[kind="secondary"] {
        background: #FFFFFF;
        border: 1px solid #D5D9D9;
        color: #0F1111;
        font-weight: 500;
        border-radius: 8px;
    }
    div.stButton > button[kind="secondary"]:hover {
        background: #F7FAFA;
        border-color: #888C8C;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F0F2F2;
        padding: 6px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 6px;
        color: #333333;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #0F1111 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* Character Counter Pill */
    .char-count {
        font-size: 0.8rem;
        color: #565959;
        font-weight: 500;
        text-align: right;
        margin-top: -0.5rem;
        margin-bottom: 0.5rem;
    }
    .char-count.warning {
        color: #C40000;
        font-weight: 700;
    }

    /* Image Preview Container */
    .img-preview-box {
        border: 1px solid #D5D9D9;
        border-radius: 8px;
        padding: 8px;
        background: #FFFFFF;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


def render_header(brand_name: str = "Manasvini Fancy"):
    """Renders the top branding header mimicking Amazon Seller Central."""
    st.markdown(f"""
    <div class="seller-header">
        <div>
            <h1>Amazon AutoList Studio</h1>
            <div style="font-size: 0.9rem; color: #E0E6ED; margin-top: 4px;">
                Complete Automated Listing Engine • Vision & Background • A9 AI Content • SP-API & Flat File
            </div>
        </div>
        <div style="text-align: right;">
            <div class="brand-pill">Store: {brand_name}</div>
            <div style="font-size: 0.78rem; color: #A6C8E0; margin-top: 5px;">Marketplace: Amazon.in</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
