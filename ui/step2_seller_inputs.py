"""Step 2 UI: Seller Quick Inputs & Store Profile Pre-filler."""

import streamlit as st
from typing import Dict, Any

from core.config import BRAND_PROFILE, HSN_CODES, MATERIAL_PRESETS
from agents.prefill_agent import AttributePrefillerAgent


def render_step2_seller_inputs(session_state):
    """Renders the seller prompt and quick variable details dashboard."""
    st.markdown("""
    <div class="amazon-card">
        <div class="amazon-card-header">
            <div>
                <h3 class="amazon-card-title">Step 2: Interactive Seller Prompt & Store Profile</h3>
                <div style="font-size: 0.85rem; color: #565959;">
                    Provide quick listing variables (SKU, Price, MRP, HSN, Dimensions).
                    Store profile constants for <b>Manasvini Fancy</b> are automatically pre-filled.
                </div>
            </div>
            <span class="badge-brand">Store: Manasvini Fancy</span>
        </div>
    """, unsafe_allow_html=True)

    prefiller = AttributePrefillerAgent()
    inputs = session_state.seller_inputs

    # Row 1: Product Classification & Material
    c1, c2, c3 = st.columns([2, 2, 1.5])
    with c1:
        product_type = st.text_input(
            "Product Type / Title Hint *",
            value=inputs.get("product_type", "Triply Stainless Steel Deep Kadhai with Lid"),
            help="Common product category or working name (e.g., Deep Kadhai, Frying Pan, Handi, Tawa)"
        )
        inputs["product_type"] = product_type

        # Smart match detected material from AI
        mat_val = inputs.get("material", "")
        mat_idx = 0
        for i, m_opt in enumerate(MATERIAL_PRESETS):
            if any(term in m_opt.lower() for term in ["copper", "brass", "iron", "steel", "ceramic", "glass", "aluminium"] if term in mat_val.lower()):
                mat_idx = i
                break

        material = st.selectbox(
            "Primary Material *",
            options=MATERIAL_PRESETS,
            index=mat_idx,
            help="High-grade materials used for Manasvini Fancy products"
        )
        inputs["material"] = material

    with c3:
        capacity = st.text_input(
            "Capacity / Size *",
            value=inputs.get("capacity", "2.5 Litres"),
            help="e.g., 2.5 Litres, 24cm, 10-Inch, Set of 3"
        )
        inputs["capacity"] = capacity

    # Row 2: Pricing, SKU & MRP
    c_sku, c_price, c_mrp, c_inv = st.columns([2, 1.5, 1.5, 1.5])
    with c_sku:
        # SKU with auto-generate button
        default_sku = inputs.get("sku", "MF-SS-KAD-24CM")
        sku = st.text_input("Seller SKU (Stock Keeping Unit) *", value=default_sku)
        inputs["sku"] = sku

    with c_price:
        price = st.number_input(
            "Your Price / Selling Price (₹) *",
            min_value=1.0,
            max_value=500000.0,
            value=float(inputs.get("price", 1899.0)),
            step=50.0
        )
        inputs["price"] = price

    with c_mrp:
        mrp = st.number_input(
            "Maximum Retail Price / MRP (₹) *",
            min_value=1.0,
            max_value=500000.0,
            value=float(inputs.get("mrp", 2799.0)),
            step=50.0
        )
        inputs["mrp"] = mrp

    with c_inv:
        quantity = st.number_input(
            "Inventory Stock *",
            min_value=0,
            max_value=10000,
            value=int(inputs.get("quantity", 50)),
            step=5
        )
        inputs["quantity"] = quantity

    # Live Discount calculation pill
    if mrp > 0 and mrp >= price:
        disc = round(((mrp - price) / mrp) * 100, 1)
        savings = mrp - price
        st.markdown(f"""
        <div style="background:#E7F4EA; border:1px solid #B8E4C9; padding:6px 12px; border-radius:6px; font-size:0.85rem; display:inline-block; margin-bottom:12px;">
            <b>Offer Value:</b> Customer saves <b>₹{savings:,.2f}</b> (<span style="color:#067D62; font-weight:700;">{disc}% OFF</span>)
        </div>
        """, unsafe_allow_html=True)
    elif price > mrp:
        st.warning("Warning: Selling Price is higher than MRP. Amazon policies require Selling Price <= MRP.")

    # Row 3: HSN Code, Tax & Dimensions
    c_hsn, c_dim, c_wt = st.columns([2, 2, 1.5])
    with c_hsn:
        # Auto-lookup HSN based on material
        auto_hsn = prefiller.lookup_hsn_code(material)
        hsn_options = list(HSN_CODES.keys())
        hsn_index = hsn_options.index(auto_hsn) if auto_hsn in hsn_options else 0

        hsn = st.selectbox(
            "HSN Code (Indian GST) *",
            options=hsn_options,
            index=hsn_index,
            format_func=lambda code: f"{code} - {HSN_CODES[code]['category']} (GST {HSN_CODES[code]['gst_rate']}%)"
        )
        inputs["hsn"] = hsn
        st.caption(f"Category: {HSN_CODES[hsn]['description']}")

    with c_dim:
        dimensions = st.text_input(
            "Package Dimensions (L x W x H cm) *",
            value=inputs.get("dimensions", "28 x 25 x 12 cm"),
            help="Dimensions of packaged box for Amazon shipping weight tier"
        )
        inputs["dimensions"] = dimensions

    with c_wt:
        weight = st.text_input(
            "Package Weight *",
            value=inputs.get("weight", "1.35 kg"),
            help="Total gross shipping weight"
        )
        inputs["weight"] = weight

    # Custom Guidance for AI
    guidance = st.text_area(
        "Seller Guidance for AI Agent (Optional Key Selling Points / Story)",
        value=inputs.get("guidance", "Highlight heavy triply SAS construction, 100% toxin-free cooking, stay-cool ergonomic handles, and induction compatibility."),
        height=70
    )
    inputs["guidance"] = guidance

    st.markdown("</div>", unsafe_allow_html=True)
