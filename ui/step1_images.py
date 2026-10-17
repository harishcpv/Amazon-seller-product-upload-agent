"""Step 1 UI: Image Upload, Vision AI Analysis & Background Studio."""

import streamlit as st
from PIL import Image
from typing import Dict, Any, Optional

from core.config import IMAGE_CONFIG, BRAND_PROFILE, save_gemini_api_key
from agents.vision_agent import VisionBackgroundAgent
from agents.content_agent import ContentGenerationAgent
from agents.local_vision_analyzer import LocalVisionAnalyzer
from core.models import CompleteListing, ProductIdentity, ProductDescription, ProductDetails, OfferPricing, SafetyCompliance
from sample_data.demo_samples import generate_synthetic_demo_image, DEMO_PRODUCTS
from ui.live_pdp_preview import render_amazon_pdp_preview


def render_step1_images(session_state):
    """Renders the image upload, instant AI visual analysis, and background standardization studio."""
    st.markdown("""
    <div class="amazon-card">
        <div class="amazon-card-header">
            <div>
                <h3 class="amazon-card-title">Step 1: Upload Product Picture & AI Vision Analysis</h3>
                <div style="font-size: 0.85rem; color: #565959;">
                    Upload your product photo(s). The <b>AI Vision Agent</b> visually inspects the image pixels
                    to identify the exact product, detect its material & finish, and automatically generate
                    the <b>A9 Title</b>, <b>5 Benefit Bullet Points</b>, and <b>Rich Description</b>.
                </div>
            </div>
            <span class="badge-brand">Image-First AI Workflow</span>
        </div>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # AI Vision Engine Status & API Key Configuration Banner
    # -----------------------------------------------------------------
    curr_key = session_state.get("gemini_api_key", "").strip()
    with st.expander("🔑 AI Vision Engine Configuration (Google Gemini 2.5 Flash Vision / Local Vision)", expanded=not bool(curr_key)):
        col_k1, col_k2 = st.columns([3, 1])
        with col_k1:
            input_key = st.text_input(
                "Google Gemini API Key (Enables Deep Multimodal Vision Inspection):",
                value=curr_key,
                type="password",
                placeholder="AIzaSy...",
                help="Get a 100% free Gemini API key from Google AI Studio: https://aistudio.google.com/app/apikey"
            )
            st.caption("Don't have a Gemini key? [Click here to get a free Google Gemini API key](https://aistudio.google.com/app/apikey) (Takes 30 seconds, no credit card required). Without a key, our built-in Local Computer Vision Analyzer inspects the image pixels locally.")
        with col_k2:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if st.button("Save API Key", type="primary", use_container_width=True):
                if input_key.strip():
                    save_gemini_api_key(input_key.strip())
                    session_state.gemini_api_key = input_key.strip()
                    st.success("Gemini API Key saved permanently to .env!")
                    st.rerun()

    # Active Engine Status Pill
    if session_state.get("gemini_api_key", "").strip():
        st.markdown("""
        <div style="background:#E7F4EA; border:1px solid #B8E4C9; padding:8px 14px; border-radius:6px; font-size:0.85rem; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <b style="color:#067D62;">Active AI Engine:</b> <b>Google Gemini 2.5 Flash Multimodal Vision</b>
                <span style="color:#565959; margin-left:8px;">(High-precision visual recognition from photo pixels)</span>
            </div>
            <span class="badge-success">Connected</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#FFF3CD; border:1px solid #FFEEBA; padding:8px 14px; border-radius:6px; font-size:0.85rem; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <b style="color:#856404;">Active AI Engine:</b> <b>Local Computer Vision Analyzer</b>
                <span style="color:#565959; margin-left:8px;">(Inspects color spectra, metallic luster, and silhouette ratios from image)</span>
            </div>
            <span class="badge-warning">Local Vision Mode</span>
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # Photo Upload Slots & Quick Demo Loader
    # -----------------------------------------------------------------
    col_demo, col_opt = st.columns([2, 1])
    with col_demo:
        st.markdown("**Test with Sample Products:**")
        selected_demo = st.selectbox(
            "Select Demo Preset:",
            options=list(DEMO_PRODUCTS.keys()),
            format_func=lambda k: DEMO_PRODUCTS[k]["name"],
            label_visibility="collapsed"
        )
        if st.button("Load Sample Photos for Selected Product", key="btn_load_demo_photos", type="secondary"):
            with st.spinner("Generating sample product photos..."):
                for slot_id in range(1, 6):
                    synthetic_img = generate_synthetic_demo_image(slot_id, selected_demo)
                    session_state.raw_images[slot_id] = synthetic_img
                st.success("Loaded sample photos! Click 'Analyze Photo with AI' below.")
                st.rerun()

    with col_opt:
        st.markdown("**Image Processing:**")
        strip_bg_toggle = st.checkbox(
            "Strip Background (rembg AI)",
            value=session_state.get("strip_bg_enabled", True),
            help="Removes background and centers product on pure #FFFFFF"
        )
        session_state.strip_bg_enabled = strip_bg_toggle

    st.markdown("---")

    # 5 Slots Layout
    slots = [
        (1, "Main Product Photo *", "Front primary angle. Upload any product photo here."),
        (2, "Angle 2 - Side Profile", "Side profile showcasing depth, handles, and thickness."),
        (3, "Angle 3 - Top / Interior", "Direct overhead view highlighting cooking surface or opening."),
        (4, "Angle 4 - Dimensions / Scale", "Scale view displaying size and capacity."),
        (5, "Angle 5 - In-Use / Packaging", "Presentation view with gift packaging or lid."),
    ]

    cols = st.columns(5)
    for idx, (slot_id, title, desc) in enumerate(slots):
        with cols[idx]:
            st.markdown(f"**Slot {slot_id}: {title.split(' - ')[0]}**")
            st.caption(desc[:45] + "...")

            uploaded_file = st.file_uploader(
                f"Upload Photo {slot_id}",
                type=["jpg", "jpeg", "png", "webp"],
                key=f"upload_slot_{slot_id}",
                label_visibility="collapsed"
            )

            if uploaded_file is not None:
                img = Image.open(uploaded_file)
                session_state.raw_images[slot_id] = img

            # Display thumbnail
            if slot_id in session_state.raw_images and session_state.raw_images[slot_id] is not None:
                st.image(
                    session_state.raw_images[slot_id],
                    caption=f"Uploaded ({session_state.raw_images[slot_id].width}x{session_state.raw_images[slot_id].height})",
                    use_container_width=True
                )
            else:
                st.info(f"Slot {slot_id} empty")

    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # Primary Action Bar: Analyze Photo with AI & Generate Listing
    # -----------------------------------------------------------------
    has_images = any(img is not None for img in session_state.raw_images.values())

    if has_images:
        st.markdown("""
        <div style="background:#FFF9E6; border:1px solid #FFE082; padding:16px; border-radius:8px; margin-bottom:15px;">
            <div style="font-size:1.05rem; font-weight:700; color:#0F1111; margin-bottom:6px;">
                Ready to Analyze Your Uploaded Product Photo
            </div>
            <div style="font-size:0.88rem; color:#565959; margin-bottom:12px;">
                The AI will inspect the uploaded image pixels, recognize the exact item, and create an Amazon A9 Title, 5 Benefit Bullets, Description, and Keywords tailored to your photo.
            </div>
        """, unsafe_allow_html=True)

        col_act1, col_act2 = st.columns([2, 1.5])
        with col_act1:
            analyze_clicked = st.button(
                "✨ Analyze Photo with AI & Generate Listing (Title, Bullets & Description)",
                type="primary",
                use_container_width=True,
                key="btn_analyze_and_generate"
            )
        with col_act2:
            process_bg_clicked = st.button(
                "🖼️ Standardize Images to 2000x2000 Pure White (#FFFFFF)",
                type="secondary",
                use_container_width=True,
                key="btn_process_bg_only"
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # Execution Logic: Analyze with AI
        if analyze_clicked:
            with st.spinner("AI Vision Agent inspecting product photo pixels and synthesizing Amazon listing..."):
                agent = ContentGenerationAgent(api_key=session_state.get("gemini_api_key", ""))

                # Collect uploaded images
                active_imgs = [img for img in session_state.raw_images.values() if img is not None]

                # Run AI generation
                generated = agent.generate_listing_content(
                    images=active_imgs,
                    seller_inputs=session_state.seller_inputs,
                    user_guidance=""
                )

                session_state.generated_content = generated
                session_state.content_generated = True

                # Synchronize detected attributes into seller inputs
                if "material" in generated:
                    session_state.seller_inputs["material"] = generated["material"]
                if "product_name" in generated and generated["product_name"]:
                    session_state.seller_inputs["product_type"] = generated["product_name"]
                elif "title" in generated:
                    session_state.seller_inputs["product_type"] = generated["title"].replace(BRAND_PROFILE["brand_name"], "").strip()[:50]
                if "dimensions" in generated:
                    session_state.seller_inputs["dimensions"] = generated["dimensions"]
                if "item_weight" in generated:
                    session_state.seller_inputs["weight"] = generated["item_weight"]
                if "capacity" in generated:
                    session_state.seller_inputs["capacity"] = generated["capacity"]
                if "suggested_hsn" in generated:
                    session_state.seller_inputs["hsn"] = generated["suggested_hsn"]

                # Also automatically process background if not done
                if not session_state.processed_images and active_imgs:
                    v_agent = VisionBackgroundAgent()
                    for slot_id, raw_img in session_state.raw_images.items():
                        if raw_img is not None:
                            session_state.processed_images[slot_id] = v_agent.process_single_image(raw_img, strip_bg=session_state.strip_bg_enabled)

                st.success(f"AI Vision Analysis Complete! Listing generated via {generated.get('source', 'AI Agent')}.")
                st.rerun()

        # Execution Logic: Process Background Only
        if process_bg_clicked:
            progress_bar = st.progress(0, text="Initializing Vision Agent & rembg...")
            v_agent = VisionBackgroundAgent()
            total = len([k for k, v in session_state.raw_images.items() if v is not None])
            curr = 0

            for slot_id, raw_img in session_state.raw_images.items():
                if raw_img is not None:
                    curr += 1
                    progress_bar.progress(int((curr / total) * 100), text=f"Processing Slot {slot_id} to 2000x2000 #FFFFFF...")
                    result = v_agent.process_single_image(raw_img, strip_bg=session_state.strip_bg_enabled)
                    session_state.processed_images[slot_id] = result

            progress_bar.progress(100, text="Standardized all photos to Amazon 2000x2000 Pure White!")
            st.success("Images standardized to 2000x2000 Pure White #FFFFFF!")
            st.rerun()

    # -----------------------------------------------------------------
    # Display AI Analysis Breakdown & Generated Listing
    # -----------------------------------------------------------------
    if session_state.get("content_generated") and session_state.generated_content:
        gen = session_state.generated_content
        vis = gen.get("detected_visuals", {})

        st.markdown("""
        <div class="amazon-card">
            <div class="amazon-card-header">
                <div>
                    <h3 class="amazon-card-title">✨ AI Visual Inspection Results & Generated Listing</h3>
                    <div style="font-size:0.85rem; color:#565959;">
                        Derived strictly from visual analysis of your uploaded product photo.
                    </div>
                </div>
                <span class="badge-success">Analysis Complete</span>
            </div>
        """, unsafe_allow_html=True)

        # Visual Detection Badges
        c_vis1, c_vis2, c_vis3, c_vis4 = st.columns(4)
        c_vis1.metric("Detected Material", gen.get("material", "Authentic Material"))
        c_vis2.metric("Visual Color / Finish", gen.get("color", "Polished Finish")[:22])
        c_vis3.metric("Capacity / Scale", gen.get("capacity", "Standard")[:22])
        c_vis4.metric("Suggested HSN", gen.get("suggested_hsn", "73239390"), "GST 18%")

        st.markdown("---")

        # 1. Title
        st.markdown("**Amazon A9-Optimized Title (Generated from Image):**")
        st.text_area("Title", value=gen.get("title", ""), height=75, key="step1_title", label_visibility="collapsed")

        # 2. Five Bullets
        st.markdown("**5 Benefit-Driven Bullet Points (About this item):**")
        for i in range(1, 6):
            b_key = f"bullet_{i}"
            st.text_input(f"Bullet {i}", value=gen.get(b_key, ""), key=f"step1_{b_key}", label_visibility="collapsed")

        # 3. Description
        with st.expander("View Generated Product Description & Backend Keywords", expanded=False):
            st.markdown("**Product Description (HTML):**")
            st.text_area("Desc", value=gen.get("description", ""), height=150, key="step1_desc", label_visibility="collapsed")
            st.markdown(f"**Backend Search Terms:** `{gen.get('search_terms', '')}`")

        # 4. Instant Live Amazon Customer Preview (PDP)
        st.markdown("---")
        st.markdown("### 🛍️ Live Customer View on Amazon (Simulated Detail Page)")

        # Build listing object for live preview
        temp_listing = CompleteListing(
            identity=ProductIdentity(
                item_name=gen.get("title", f"{BRAND_PROFILE['brand_name']} Kitchenware"),
                brand_name=BRAND_PROFILE["brand_name"],
                product_id="GTIN_EXEMPTION_APPLIED",
                product_id_type="GTIN Exemption",
                item_type_keyword="kitchen-and-dining",
                model_name="MF-SERIES-2026",
                model_number="MF-2026-01"
            ),
            description=ProductDescription(
                bullet_point_1=gen.get("bullet_1", ""),
                bullet_point_2=gen.get("bullet_2", ""),
                bullet_point_3=gen.get("bullet_3", ""),
                bullet_point_4=gen.get("bullet_4", ""),
                bullet_point_5=gen.get("bullet_5", ""),
                product_description=gen.get("description", ""),
                search_terms=gen.get("search_terms", "")
            ),
            details=ProductDetails(
                material=gen.get("material", "Stainless Steel"),
                color=gen.get("color", "Mirror Finish"),
                finish_type=gen.get("finish_type", "Polished"),
                capacity=gen.get("capacity", "2.5 Litres"),
                item_weight=gen.get("item_weight", "1.2 kg"),
                package_dimensions=gen.get("dimensions", "28 x 25 x 12 cm"),
                is_dishwasher_safe=True,
                is_induction_compatible=True
            ),
            offer=OfferPricing(
                seller_sku=session_state.seller_inputs.get("sku", "MF-PROD-01"),
                standard_price=float(session_state.seller_inputs.get("price", 1899.0)),
                list_price=float(session_state.seller_inputs.get("mrp", 2799.0)),
                quantity=int(session_state.seller_inputs.get("quantity", 50)),
                fulfillment_channel="DEFAULT",
                handling_time=2,
                condition_type="New"
            ),
            compliance=SafetyCompliance(
                country_of_origin=BRAND_PROFILE["country_of_origin"],
                hsn_code=gen.get("suggested_hsn", "73239390"),
                gst_tax_code=BRAND_PROFILE["default_tax_code"],
                manufacturer=BRAND_PROFILE["manufacturer"],
                packer_details=BRAND_PROFILE["packer_details"]
            ),
            status="READY_TO_EXPORT"
        )
        session_state.complete_listing = temp_listing

        render_amazon_pdp_preview(
            listing=temp_listing,
            processed_images=session_state.processed_images,
            raw_images=session_state.raw_images
        )

        st.markdown("</div>", unsafe_allow_html=True)
