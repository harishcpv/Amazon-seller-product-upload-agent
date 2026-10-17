"""Amazon AutoList Studio - Main Streamlit Application.

Production-ready local web application for Amazon sellers ('Manasvini Fancy' brand profile).
Automates the full Amazon listing workflow:
- 5-angle raw photo ingestion and rembg background removal to 2000x2000 pure white (#FFFFFF)
- Multimodal AI listing generation (A9 titles, 5 benefit bullets, rich descriptions, search terms)
- Store profile pre-filler for Manasvini Fancy (brand, manufacturer, material, HSN, compliance)
- 5-tab Seller Central review dashboard (Product Identity, Description, Details, Offer, Compliance)
- Ready-to-upload Amazon flat file (.tsv/.csv), ZIP packager, and SP-API mock push.
"""

import os
import streamlit as st
from PIL import Image

# Page Configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Amazon AutoList Studio | Manasvini Fancy",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import internal modules
from core.config import APP_NAME, APP_TAGLINE, APP_VERSION, BRAND_PROFILE, GEMINI_CONFIG, save_gemini_api_key
from ui.styles import apply_custom_styles, render_header
from ui.step1_images import render_step1_images
from ui.step2_seller_inputs import render_step2_seller_inputs
from ui.step3_ai_studio import render_step3_ai_studio
from ui.step4_review_tabs import render_step4_review_tabs
from ui.step5_export_publish import render_step5_export_publish
from agents.prefill_agent import AttributePrefillerAgent


def init_session_state():
    """Initializes Streamlit session state defaults."""
    prefiller = AttributePrefillerAgent()

    if "raw_images" not in st.session_state:
        st.session_state.raw_images = {1: None, 2: None, 3: None, 4: None, 5: None}

    if "processed_images" not in st.session_state:
        st.session_state.processed_images = {}

    if "strip_bg_enabled" not in st.session_state:
        st.session_state.strip_bg_enabled = True

    if "seller_inputs" not in st.session_state:
        st.session_state.seller_inputs = {
            "product_type": "",
            "material": "Stainless Steel (Triply 304 Food Grade)",
            "sku": "MF-PROD-01",
            "price": 1499.0,
            "mrp": 2199.0,
            "quantity": 50,
            "capacity": "",
            "dimensions": "",
            "weight": "",
            "hsn": "73239390",
            "guidance": ""
        }

    if "generated_content" not in st.session_state:
        st.session_state.generated_content = {}

    if "content_generated" not in st.session_state:
        st.session_state.content_generated = False

    if "complete_listing" not in st.session_state:
        st.session_state.complete_listing = None

    if "current_step" not in st.session_state:
        st.session_state.current_step = 1

    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    if "sp_api_response" not in st.session_state:
        st.session_state.sp_api_response = None


def render_sidebar():
    """Renders the Seller Central sidebar controls and progress tracker."""
    with st.sidebar:
        st.markdown(f"### {APP_NAME}")
        st.caption(f"v{APP_VERSION} • {BRAND_PROFILE['brand_name']} Store")

        # Store Profile Card
        st.markdown(f"""
        <div style="background:#232F3E; color:#FFFFFF; padding:12px; border-radius:8px; margin-bottom:15px; font-size:0.85rem;">
            <b>Active Store Profile:</b><br>
            <span style="color:#FF9900; font-weight:700; font-size:1rem;">{BRAND_PROFILE['brand_name']}</span><br>
            <span style="color:#A6C8E0; font-size:0.8rem;">Entity: {BRAND_PROFILE['legal_entity']}</span><br>
            <span style="color:#E0E6ED; font-size:0.8rem;">Marketplace: {BRAND_PROFILE['marketplace_name']} (IN)</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Workflow Navigation")
        steps = [
            (1, "1. Vision & Photo Studio", "5 Photos to 2000x2000 #FFF"),
            (2, "2. Quick Seller Inputs", "SKU, Price, MRP, HSN"),
            (3, "3. AI Content Studio", "A9 Title, Bullets & Story"),
            (4, "4. 5-Tab Seller Review", "Seller Central Audit"),
            (5, "5. Export & SP-API Publish", "Flat File, ZIP & Push")
        ]

        for s_num, s_title, s_sub in steps:
            # Highlight current step
            is_active = (st.session_state.current_step == s_num)
            btn_type = "primary" if is_active else "secondary"
            if st.button(f"{s_title}", key=f"nav_step_{s_num}", type=btn_type, use_container_width=True):
                st.session_state.current_step = s_num
                st.rerun()

        st.markdown("---")

        # Completion Progress Bar
        completed_count = 0
        if len(st.session_state.processed_images) > 0:
            completed_count += 1
        if st.session_state.seller_inputs.get("sku"):
            completed_count += 1
        if st.session_state.get("content_generated"):
            completed_count += 1
        if st.session_state.get("complete_listing"):
            completed_count += 1
        if st.session_state.get("sp_api_response"):
            completed_count += 1

        pct = int((completed_count / 5) * 100)
        st.markdown(f"**Listing Readiness:** `{pct}% Complete`")
        st.progress(pct)

        st.markdown("---")

        # Google Gemini Configuration
        st.markdown("#### AI Multimodal Settings")
        key_input = st.text_input(
            "Gemini API Key",
            value=st.session_state.gemini_api_key,
            type="password",
            help="Enter your Google Gemini API key for multimodal image inspection and listing generation."
        )
        if key_input != st.session_state.gemini_api_key:
            st.session_state.gemini_api_key = key_input
            if key_input.strip():
                save_gemini_api_key(key_input.strip())
            st.toast("Gemini API Key updated & saved to .env!", icon="🔑")

        if not st.session_state.gemini_api_key:
            st.caption("No key provided? No problem! The built-in Smart Heuristic Rule Engine will generate production listings automatically.")

        st.markdown("---")
        if st.button("Reset / Clear Session", type="secondary", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


def main():
    """Main application loop."""
    init_session_state()
    apply_custom_styles()
    render_header(BRAND_PROFILE["brand_name"])
    render_sidebar()

    # Step Flow Navigation Bar
    curr = st.session_state.current_step
    step_labels = [
        "1. Image Studio",
        "2. Seller Inputs",
        "3. AI Generation",
        "4. Seller Central Review",
        "5. Export & Publish"
    ]

    col_nav_info, col_nav_prev, col_nav_next = st.columns([3, 1, 1])
    with col_nav_info:
        st.markdown(f"#### Step {curr} of 5: {step_labels[curr - 1]}")
    with col_nav_prev:
        if curr > 1:
            if st.button("< Previous Step", use_container_width=True):
                st.session_state.current_step -= 1
                st.rerun()
    with col_nav_next:
        if curr < 5:
            if st.button("Next Step >", type="primary", use_container_width=True):
                st.session_state.current_step += 1
                st.rerun()

    # Render Current Step View
    if curr == 1:
        render_step1_images(st.session_state)
    elif curr == 2:
        render_step2_seller_inputs(st.session_state)
    elif curr == 3:
        render_step3_ai_studio(st.session_state)
    elif curr == 4:
        render_step4_review_tabs(st.session_state)
    elif curr == 5:
        render_step5_export_publish(st.session_state)

    # Bottom Step Navigation
    st.markdown("---")
    b_col_prev, b_col_spacer, b_col_next = st.columns([1, 3, 1])
    with b_col_prev:
        if curr > 1:
            if st.button("< Back", key="bottom_prev", use_container_width=True):
                st.session_state.current_step -= 1
                st.rerun()
    with b_col_next:
        if curr < 5:
            if st.button("Continue >", key="bottom_next", type="primary", use_container_width=True):
                st.session_state.current_step += 1
                st.rerun()


if __name__ == "__main__":
    main()
