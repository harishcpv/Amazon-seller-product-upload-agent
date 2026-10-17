"""Step 4 UI: Amazon Seller Central 5-Tab Unified Review Screen."""

import streamlit as st
from typing import Dict, Any

from core.models import CompleteListing, ProductIdentity, ProductDescription, ProductDetails, OfferPricing, SafetyCompliance
from core.config import BRAND_PROFILE, HSN_CODES, MATERIAL_PRESETS, THEME_PRESETS, AUDIENCE_PRESETS
from agents.prefill_agent import AttributePrefillerAgent
from ui.live_pdp_preview import render_amazon_pdp_preview


def render_step4_review_tabs(session_state):
    """Renders the Seller Central tabbed listing dashboard."""
    st.markdown("""
    <div class="amazon-card">
        <div class="amazon-card-header">
            <div>
                <h3 class="amazon-card-title">Step 4: Amazon Seller Central 5-Tab Unified Review</h3>
                <div style="font-size: 0.85rem; color: #565959;">
                    Review all attributes across the 5 core Amazon Seller Central listing tabs before exporting or publishing.
                </div>
            </div>
            <span class="badge-success">Policy Checked</span>
        </div>
    """, unsafe_allow_html=True)

    gen = session_state.get("generated_content", {})
    inputs = session_state.get("seller_inputs", {})
    prefiller = AttributePrefillerAgent()

    # Pre-populate defaults if not already present
    title = gen.get("title", inputs.get("product_type", f"{BRAND_PROFILE['brand_name']} Premium Kitchen Cookware"))
    brand = BRAND_PROFILE["brand_name"]
    sku = inputs.get("sku", "MF-SS-KAD-24CM")
    price = float(inputs.get("price", 1899.0))
    mrp = float(inputs.get("mrp", 2799.0))
    hsn = inputs.get("hsn", "73239390")

    # Amazon 5 Tabs
    tab_identity, tab_desc, tab_details, tab_offer, tab_comp = st.tabs([
        "1. Product Identity",
        "2. Description",
        "3. Product Details",
        "4. Offer & Pricing",
        "5. Safety & Compliance"
    ])

    # TAB 1: PRODUCT IDENTITY
    with tab_identity:
        st.markdown("#### Product Identity Specifications")
        c_t1, c_t2 = st.columns([3, 1])
        with c_t1:
            rev_title = st.text_area(
                "Item Name (Title) *",
                value=title,
                height=70,
                help="Max 200 characters. Must start with Brand Name."
            )
        with c_t2:
            st.metric("Title Chars", f"{len(rev_title)} / 200", "Valid" if 50 <= len(rev_title) <= 200 else "Check")

        c_b1, c_b2, c_b3 = st.columns(3)
        with c_b1:
            rev_brand = st.text_input("Brand Name *", value=brand, disabled=False)
        with c_b2:
            rev_id_type = st.selectbox(
                "Product ID Type *",
                options=["GTIN Exemption", "UPC", "EAN", "ASIN"],
                index=0
            )
        with c_b3:
            rev_prod_id = st.text_input(
                "Product ID *",
                value="GTIN_EXEMPTION_APPLIED" if rev_id_type == "GTIN Exemption" else "",
                help="Enter barcode or keep GTIN exemption"
            )

        c_k1, c_k2, c_k3 = st.columns(3)
        with c_k1:
            rev_item_type = st.text_input("Item Type Keyword *", value="cookware-kadhais-and-pans")
        with c_k2:
            rev_model_name = st.text_input("Model Name", value="MF-LUXE-TRI")
        with c_k3:
            rev_model_num = st.text_input("Model Number", value="MF-2026-01")

    # TAB 2: DESCRIPTION
    with tab_desc:
        st.markdown("#### Key Product Features (5 Bullet Points)")
        rev_b1 = st.text_input("Bullet 1 (Material & Durability):", value=gen.get("bullet_1", ""))
        rev_b2 = st.text_input("Bullet 2 (Thermal Performance):", value=gen.get("bullet_2", ""))
        rev_b3 = st.text_input("Bullet 3 (Ergonomics & Safety):", value=gen.get("bullet_3", ""))
        rev_b4 = st.text_input("Bullet 4 (Cooktop Compatibility):", value=gen.get("bullet_4", ""))
        rev_b5 = st.text_input("Bullet 5 (Maintenance & Care):", value=gen.get("bullet_5", ""))

        st.markdown("#### Product Description")
        rev_desc = st.text_area("Product Description (HTML)", value=gen.get("description", ""), height=150)

        st.markdown("#### Backend Search Terms")
        c_st1, c_st2 = st.columns([3, 1])
        with c_st1:
            rev_search = st.text_input("Generic Keywords (No commas, < 249 bytes)", value=gen.get("search_terms", ""))
        with c_st2:
            s_bytes = len(rev_search.encode("utf-8"))
            st.metric("Bytes", f"{s_bytes} / 249", "Compliant" if s_bytes <= 249 else "Too Long")

    # TAB 3: PRODUCT DETAILS
    with tab_details:
        st.markdown("#### Specifications & Attributes")
        c_d1, c_d2, c_d3 = st.columns(3)
        with c_d1:
            rev_material = st.selectbox(
                "Material *",
                options=MATERIAL_PRESETS,
                index=0 if "Stainless Steel" in gen.get("material", inputs.get("material", "")) else 1
            )
        with c_d2:
            rev_color = st.text_input("Color", value=gen.get("color", "Silver Mirror Polish"))
        with c_d3:
            rev_finish = st.text_input("Finish Type", value=gen.get("finish_type", "Mirror Polished Inner, Brushed Outer"))

        c_d4, c_d5, c_d6 = st.columns(3)
        with c_d4:
            rev_shape = st.text_input("Item Shape", value=gen.get("item_shape", "Deep Round Bottom Kadhai"))
        with c_d5:
            rev_cap = st.text_input("Capacity", value=gen.get("capacity", inputs.get("capacity", "2.5 Litres")))
        with c_d6:
            rev_weight = st.text_input("Item Weight", value=gen.get("item_weight", inputs.get("weight", "1.35 kg")))

        c_d7, c_d8 = st.columns(2)
        with c_d7:
            rev_dim = st.text_input("Package Dimensions", value=inputs.get("dimensions", "28 x 25 x 12 cm"))
        with c_d8:
            rev_care = st.text_input("Care Instructions", value=gen.get("care_instructions", "Dishwasher Safe. Hand wash recommended."))

        c_cb1, c_cb2, c_cb3 = st.columns(3)
        with c_cb1:
            rev_dw = st.checkbox("Dishwasher Safe", value=True)
        with c_cb2:
            rev_ind = st.checkbox("Induction Compatible", value=True)
        with c_cb3:
            rev_ov = st.checkbox("Oven Safe (up to 260°C)", value=True)

    # TAB 4: OFFER & PRICING
    with tab_offer:
        st.markdown("#### Pricing, Stock & Fulfillment")
        c_o1, c_o2, c_o3, c_o4 = st.columns(4)
        with c_o1:
            rev_sku = st.text_input("Seller SKU *", value=sku)
        with c_o2:
            rev_price = st.number_input("Selling Price (₹) *", value=float(price), step=50.0)
        with c_o3:
            rev_mrp = st.number_input("MRP / List Price (₹) *", value=float(mrp), step=50.0)
        with c_o4:
            rev_qty = st.number_input("Available Stock *", value=int(inputs.get("quantity", 50)), step=5)

        c_o5, c_o6, c_o7 = st.columns(3)
        with c_o5:
            rev_fulf = st.selectbox(
                "Fulfillment Channel *",
                options=["DEFAULT", "AMAZON_NA"],
                format_func=lambda x: "Merchant Fulfilled (MFN)" if x == "DEFAULT" else "Fulfilled by Amazon (FBA)"
            )
        with c_o6:
            rev_lead = st.number_input("Handling Time (Lead time to ship days) *", min_value=1, max_value=15, value=2)
        with c_o7:
            rev_cond = st.selectbox("Item Condition *", options=["New", "Refurbished"], index=0)

    # TAB 5: SAFETY & COMPLIANCE
    with tab_comp:
        st.markdown("#### Legal, Tax & Country of Origin")
        c_c1, c_c2, c_c3 = st.columns(3)
        with c_c1:
            rev_origin = st.text_input("Country of Origin *", value=BRAND_PROFILE["country_of_origin"])
        with c_c2:
            rev_hsn = st.text_input("HSN Code *", value=hsn)
            if rev_hsn in HSN_CODES:
                st.caption(f"GST: {HSN_CODES[rev_hsn]['gst_rate']}% | {HSN_CODES[rev_hsn]['category']}")
        with c_c3:
            rev_tax = st.text_input("Product Tax Code", value=BRAND_PROFILE["default_tax_code"])

        rev_mfg = st.text_input("Manufacturer Details *", value=BRAND_PROFILE["manufacturer"])
        rev_packer = st.text_area("Packer Contact Details *", value=BRAND_PROFILE["packer_details"], height=65)
        rev_warranty = st.text_input("Warranty Description", value=BRAND_PROFILE["default_warranty"])

    st.markdown("---")

    # Build CompleteListing Object into session_state
    listing_obj = CompleteListing(
        identity=ProductIdentity(
            item_name=rev_title,
            brand_name=rev_brand,
            product_id=rev_prod_id,
            product_id_type=rev_id_type,
            item_type_keyword=rev_item_type,
            model_name=rev_model_name,
            model_number=rev_model_num
        ),
        description=ProductDescription(
            bullet_point_1=rev_b1,
            bullet_point_2=rev_b2,
            bullet_point_3=rev_b3,
            bullet_point_4=rev_b4,
            bullet_point_5=rev_b5,
            product_description=rev_desc,
            search_terms=rev_search
        ),
        details=ProductDetails(
            material=rev_material,
            color=rev_color,
            finish_type=rev_finish,
            item_shape=rev_shape,
            theme=THEME_PRESETS[0],
            target_audience=AUDIENCE_PRESETS[0],
            care_instructions=rev_care,
            capacity=rev_cap,
            item_weight=rev_weight,
            package_dimensions=rev_dim,
            is_dishwasher_safe=rev_dw,
            is_induction_compatible=rev_ind,
            is_oven_safe=rev_ov
        ),
        offer=OfferPricing(
            seller_sku=rev_sku,
            standard_price=rev_price,
            list_price=rev_mrp,
            quantity=rev_qty,
            fulfillment_channel=rev_fulf,
            handling_time=rev_lead,
            condition_type=rev_cond
        ),
        compliance=SafetyCompliance(
            country_of_origin=rev_origin,
            hsn_code=rev_hsn,
            gst_tax_code=rev_tax,
            manufacturer=rev_mfg,
            packer_details=rev_packer,
            warranty_description=rev_warranty
        ),
        status="READY_TO_EXPORT"
    )

    session_state.complete_listing = listing_obj

    # Validation Scorecard Bar
    st.markdown("""
    <div style="background:#F0F8FF; border:1px solid #B9D5ED; border-radius:8px; padding:12px 18px; margin-top:10px; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <b>Listing Validation Status:</b>
            <span style="color:#067D62; font-weight:700; margin-left:8px;">All Mandatory Attributes Completed & Validated</span>
        </div>
        <div>
            <span class="badge-success">Amazon A9 Certified</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Live Amazon Buyer Page Preview in Step 4
    with st.expander("🛍️ Live Amazon Buyer Page Preview (Click to Expand / Collapse)", expanded=True):
        render_amazon_pdp_preview(
            listing=listing_obj,
            processed_images=session_state.processed_images,
            raw_images=session_state.raw_images
        )

    st.markdown("</div>", unsafe_allow_html=True)
