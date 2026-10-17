"""Step 3 UI: AI Content & Attribute Generation Studio."""

import streamlit as st
from typing import Dict, Any, List
from PIL import Image

from agents.content_agent import ContentGenerationAgent
from core.config import AMAZON_LIMITS


def render_step3_ai_studio(session_state):
    """Renders the AI Content Generation Studio where Gemini/LLM creates A9-optimized listings."""
    st.markdown("""
    <div class="amazon-card">
        <div class="amazon-card-header">
            <div>
                <h3 class="amazon-card-title">Step 3: AI Content & Attribute Generation Studio</h3>
                <div style="font-size: 0.85rem; color: #565959;">
                    Multimodal LLM inspects the product photos & seller variables to generate
                    Amazon A9-optimized titles, 5 benefit-driven bullet points, rich descriptions, and backend keywords.
                </div>
            </div>
            <span class="badge-brand">A9 Optimization Engine</span>
        </div>
    """, unsafe_allow_html=True)

    # Gemini API Key Status Check
    api_key = session_state.get("gemini_api_key", "").strip()
    col_status, col_btn = st.columns([2, 1.2])

    with col_status:
        if api_key:
            st.markdown("<span class='badge-success'>Google Gemini API Connected</span>", unsafe_allow_html=True)
            st.caption("Active Model: `gemini-2.5-flash` (Multimodal Vision)")
        else:
            st.markdown("<span class='badge-warning'>Gemini API Key Not Configured (Using Smart Heuristic Engine)</span>", unsafe_allow_html=True)
            st.caption("You can enter your Google Gemini API key in the sidebar for full multimodal vision.")

    with col_btn:
        generate_clicked = st.button(
            "Generate Full Listing Content",
            type="primary",
            use_container_width=True,
            key="btn_generate_listing"
        )

    if generate_clicked:
        with st.spinner("AI Agent analyzing product photos & synthesizing A9-compliant listing..."):
            agent = ContentGenerationAgent(api_key=api_key)

            # Collect active images for vision inspection
            images_to_inspect = []
            for slot_id in range(1, 6):
                if slot_id in session_state.processed_images:
                    images_to_inspect.append(session_state.processed_images[slot_id]["processed_image"])
                elif slot_id in session_state.raw_images and session_state.raw_images[slot_id] is not None:
                    images_to_inspect.append(session_state.raw_images[slot_id])

            generated = agent.generate_listing_content(
                images=images_to_inspect,
                seller_inputs=session_state.seller_inputs,
                user_guidance=session_state.seller_inputs.get("guidance", "")
            )

            session_state.generated_content = generated
            session_state.content_generated = True
            st.success(f"Generated listing content via {generated.get('source', 'AI Agent')}!")
            st.rerun()

    # Display and Edit Generated Content
    if session_state.get("content_generated", False) and session_state.generated_content:
        gen = session_state.generated_content

        st.markdown("---")
        st.subheader("Interactive Content Editor & Validator")

        # 1. Amazon Title
        title_val = gen.get("title", "")
        title_len = len(title_val)
        is_title_ok = 50 <= title_len <= 200

        col_t_label, col_t_count = st.columns([3, 1])
        with col_t_label:
            st.markdown("**Amazon A9-Optimized Title (Formula: Brand + Material + Type + Specs + Usability)**")
        with col_t_count:
            count_color = "#067D62" if is_title_ok else "#C40000"
            st.markdown(f"<div class='char-count' style='color:{count_color};'>Length: <b>{title_len}</b> / 200 chars</div>", unsafe_allow_html=True)

        new_title = st.text_area(
            "Product Title",
            value=title_val,
            height=75,
            key="editor_title",
            label_visibility="collapsed"
        )
        gen["title"] = new_title

        # 2. Five Benefit-Driven Bullet Points
        st.markdown("**5 Benefit-Driven Bullet Points (Amazon Format: `[CAPITALIZED BENEFIT]: Detail`)**")
        bullet_keys = ["bullet_1", "bullet_2", "bullet_3", "bullet_4", "bullet_5"]
        bullet_labels = [
            "1. Craftsmanship & Food-Grade Material",
            "2. Thermal Performance & Heat Distribution",
            "3. Ergonomic Safety & Handles",
            "4. Cooktop & Induction Compatibility",
            "5. Cleaning, Maintenance & Warranty"
        ]

        for i, (b_key, b_lbl) in enumerate(zip(bullet_keys, bullet_labels)):
            b_val = gen.get(b_key, "")
            b_len = len(b_val)
            col_b_lbl, col_b_cnt = st.columns([3, 1])
            with col_b_lbl:
                st.caption(f"Bullet {b_lbl}")
            with col_b_cnt:
                st.markdown(f"<div class='char-count'>Length: {b_len} chars</div>", unsafe_allow_html=True)

            new_b = st.text_area(
                f"Bullet {i+1}",
                value=b_val,
                height=68,
                key=f"editor_{b_key}",
                label_visibility="collapsed"
            )
            gen[b_key] = new_b

        # 3. Product Description
        st.markdown("**Rich Product Description (HTML Structured)**")
        desc_tabs = st.tabs(["HTML Source Editor", "Live Amazon Render Preview"])
        with desc_tabs[0]:
            new_desc = st.text_area(
                "Product Description Source",
                value=gen.get("description", ""),
                height=180,
                key="editor_description",
                label_visibility="collapsed"
            )
            gen["description"] = new_desc
        with desc_tabs[1]:
            st.markdown(
                f"<div style='border:1px solid #D5D9D9; border-radius:6px; padding:15px; background:#FFFFFF;'>{gen.get('description', '')}</div>",
                unsafe_allow_html=True
            )

        # 4. Backend Search Terms (Generic Keywords)
        st.markdown("**Backend Search Terms / Generic Keywords**")
        terms_val = gen.get("search_terms", "")
        terms_bytes = len(terms_val.encode("utf-8"))
        col_s_lbl, col_s_cnt = st.columns([3, 1])
        with col_s_lbl:
            st.caption("No brand names, no commas, space-separated only (Amazon Max: 249 bytes)")
        with col_s_cnt:
            byte_color = "#067D62" if terms_bytes <= 249 else "#C40000"
            st.markdown(f"<div class='char-count' style='color:{byte_color};'>Bytes: <b>{terms_bytes}</b> / 249 bytes</div>", unsafe_allow_html=True)

        new_terms = st.text_input(
            "Search Terms",
            value=terms_val,
            key="editor_search_terms",
            label_visibility="collapsed"
        )
        gen["search_terms"] = new_terms

    st.markdown("</div>", unsafe_allow_html=True)
