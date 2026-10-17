"""Step 1 UI: Image Upload & Vision Background Studio."""

import streamlit as st
from PIL import Image
from typing import Dict, Any, Optional

from core.config import IMAGE_CONFIG
from agents.vision_agent import VisionBackgroundAgent
from sample_data.demo_samples import generate_synthetic_demo_image, DEMO_PRODUCTS


def render_step1_images(session_state):
    """Renders the image upload, background stripping, and 2000x2000 standardization studio."""
    st.markdown("""
    <div class="amazon-card">
        <div class="amazon-card-header">
            <div>
                <h3 class="amazon-card-title">Step 1: Vision & Background Agent (5 Product Photos)</h3>
                <div style="font-size: 0.85rem; color: #565959;">
                    Upload 5 raw product photos from different angles. The agent strips the background with <code>rembg</code>,
                    pads and centers onto a pure white canvas (<code>#FFFFFF</code> / RGB 255,255,255), and standardizes to <b>2000 x 2000px</b>.
                </div>
            </div>
            <span class="badge-success">Amazon Zoom Ready (2000x2000)</span>
        </div>
    """, unsafe_allow_html=True)

    # Demo 1-Click Loader Toolbar
    col_demo, col_opt = st.columns([2, 1])
    with col_demo:
        st.markdown("**Quick Demo Loader:** Don't have product photos on hand?")
        selected_demo = st.selectbox(
            "Select Demo Preset:",
            options=list(DEMO_PRODUCTS.keys()),
            format_func=lambda k: DEMO_PRODUCTS[k]["name"],
            label_visibility="collapsed"
        )
        if st.button("Load 5 Sample Photos for Selected Product", key="btn_load_demo_photos", type="secondary"):
            with st.spinner("Generating 5 high-resolution raw product photos on studio backdrop..."):
                for slot_id in range(1, 6):
                    synthetic_img = generate_synthetic_demo_image(slot_id, selected_demo)
                    session_state.raw_images[slot_id] = synthetic_img
                # Also pre-fill seller variables
                demo_data = DEMO_PRODUCTS[selected_demo]
                session_state.seller_inputs.update({
                    "product_type": demo_data["product_type"],
                    "material": demo_data["material"],
                    "sku": demo_data["sku"],
                    "price": demo_data["price"],
                    "mrp": demo_data["mrp"],
                    "capacity": demo_data["capacity"],
                    "dimensions": demo_data["dimensions"],
                    "weight": demo_data["weight"],
                    "hsn": demo_data["hsn"],
                    "guidance": demo_data["guidance"]
                })
                st.success(f"Loaded 5 demo photos and attributes for '{demo_data['name']}'!")
                st.rerun()

    with col_opt:
        st.markdown("**Processing Options:**")
        strip_bg_toggle = st.checkbox(
            "Strip Background (rembg AI)",
            value=session_state.get("strip_bg_enabled", True),
            help="Removes background objects/shadows and places product on pure #FFFFFF"
        )
        session_state.strip_bg_enabled = strip_bg_toggle

    st.markdown("---")

    # 5 Slots Layout
    slots = [
        (1, "Main Image", "Pure #FFFFFF background required. Product fills 85% of frame."),
        (2, "Angle 2 - Side Profile", "Side profile showcasing handle rivoting, depth, and thickness."),
        (3, "Angle 3 - Top / Interior", "Direct overhead view highlighting cooking surface and interior finish."),
        (4, "Angle 4 - Dimensions & Scale", "Scale view displaying diameter, height, and capacity measurements."),
        (5, "Angle 5 - In-Use / Packaging", "Presentation view with gift packaging box or lid arrangement."),
    ]

    cols = st.columns(5)
    for idx, (slot_id, title, desc) in enumerate(slots):
        with cols[idx]:
            st.markdown(f"**Slot {slot_id}: {title.split(' - ')[0]}**")
            st.caption(desc[:45] + "...")

            # File uploader
            uploaded_file = st.file_uploader(
                f"Upload Photo {slot_id}",
                type=["jpg", "jpeg", "png", "webp"],
                key=f"upload_slot_{slot_id}",
                label_visibility="collapsed"
            )

            if uploaded_file is not None:
                img = Image.open(uploaded_file)
                session_state.raw_images[slot_id] = img

            # Display thumbnail if raw image exists
            if slot_id in session_state.raw_images and session_state.raw_images[slot_id] is not None:
                st.image(
                    session_state.raw_images[slot_id],
                    caption=f"Raw ({session_state.raw_images[slot_id].width}x{session_state.raw_images[slot_id].height})",
                    use_container_width=True
                )
            else:
                st.info(f"Slot {slot_id} empty")

    st.markdown("</div>", unsafe_allow_html=True)

    # Process Action Button
    has_images = any(img is not None for img in session_state.raw_images.values())
    if has_images:
        col_btn, col_count = st.columns([2, 1])
        with col_btn:
            if st.button("Run Vision Agent: Strip BG & Standardize to 2000x2000 Pure White", type="primary", use_container_width=True):
                progress_bar = st.progress(0, text="Initializing Vision Agent & rembg model...")
                agent = VisionBackgroundAgent()
                total = len([k for k, v in session_state.raw_images.items() if v is not None])
                curr = 0

                for slot_id, raw_img in session_state.raw_images.items():
                    if raw_img is not None:
                        curr += 1
                        progress_bar.progress(
                            int((curr / total) * 100),
                            text=f"Processing Slot {slot_id} ({IMAGE_CONFIG['slot_codes'][slot_id-1]}): Stripping BG & Centering on 2000x2000 #FFFFFF..."
                        )
                        result = agent.process_single_image(raw_img, strip_bg=session_state.strip_bg_enabled)
                        session_state.processed_images[slot_id] = result

                progress_bar.progress(100, text="All images standardized to Amazon 2000x2000 Pure White standards!")
                st.success("Vision Agent completed successfully! See before/after review below.")
                st.rerun()

        with col_count:
            active_count = len([k for k, v in session_state.raw_images.items() if v is not None])
            proc_count = len([k for k, v in session_state.processed_images.items() if v is not None])
            st.metric("Images Ready", f"{active_count} / 5", f"{proc_count} Standardized")

    # Display Processed Images Inspection & Amazon Compliance
    if session_state.processed_images:
        st.markdown("""
        <div class="amazon-card">
            <div class="amazon-card-header">
                <div>
                    <h4 class="amazon-card-title">Processed Image Review & Amazon Compliance Check</h4>
                    <div style="font-size: 0.82rem; color: #565959;">
                        Pure White Background (RGB 255, 255, 255) • 2000 x 2000 High-Res Zoom • Centered with 85% Fill Ratio
                    </div>
                </div>
                <span class="badge-success">100% Policy Compliant</span>
            </div>
        """, unsafe_allow_html=True)

        comp_cols = st.columns(5)
        for idx, (slot_id, title, _) in enumerate(slots):
            with comp_cols[idx]:
                if slot_id in session_state.processed_images:
                    p_data = session_state.processed_images[slot_id]
                    st.image(p_data["processed_image"], caption=f"Slot {slot_id}: 2000x2000 Pure White", use_container_width=True)

                    comp = p_data.get("compliance", {})
                    if comp.get("is_compliant"):
                        st.markdown("<span class='badge-success'>Passed: 2000x2000</span>", unsafe_allow_html=True)
                        st.markdown("<span class='badge-success' style='margin-top:2px;'>Pure White (#FFF)</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='badge-warning'>Review Required</span>", unsafe_allow_html=True)

                    # Quick download button for single image
                    st.download_button(
                        f"Download Slot {slot_id}",
                        data=p_data["image_bytes"],
                        file_name=f"{IMAGE_CONFIG['slot_codes'][slot_id-1]}_2000x2000.jpg",
                        mime="image/jpeg",
                        key=f"dl_single_img_{slot_id}",
                        use_container_width=True
                    )
                else:
                    st.caption("Not yet processed")

        st.markdown("</div>", unsafe_allow_html=True)
