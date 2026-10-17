"""Amazon Product Detail Page (PDP) Live Buyer Preview Component.

Renders an authentic, pixel-perfect simulation of how the listing will look to
customers on Amazon.in (including the image gallery, title, pricing, bullet points,
product specifications, and the Amazon Buy Box) before pushing the upload.
"""

import streamlit as st
from typing import Dict, Any, List
from PIL import Image

from core.models import CompleteListing
from core.config import BRAND_PROFILE, IMAGE_CONFIG


def render_amazon_pdp_preview(listing: CompleteListing, processed_images: Dict[int, Dict[str, Any]], raw_images: Dict[int, Any]):
    """Renders the authentic Amazon Product Detail Page preview card."""
    ident = listing.identity
    desc = listing.description
    det = listing.details
    off = listing.offer
    comp = listing.compliance

    # Inject Amazon-specific detail page styles
    st.markdown("""
    <style>
    .pdp-container {
        background: #FFFFFF;
        border: 1px solid #D5D9D9;
        border-radius: 8px;
        padding: 24px;
        margin-top: 15px;
        margin-bottom: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .amazon-brand-link {
        color: #007185;
        font-size: 0.88rem;
        font-weight: 500;
        text-decoration: none;
    }
    .amazon-brand-link:hover {
        color: #C7511F;
        text-decoration: underline;
    }
    .pdp-title {
        font-size: 1.45rem;
        font-weight: 600;
        line-height: 1.35;
        color: #0F1111;
        margin: 6px 0 10px 0;
    }
    .pdp-stars {
        color: #FFA41C;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .pdp-rating-count {
        color: #007185;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .choice-badge {
        background: #232F3E;
        color: #FFFFFF;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 3px;
        display: inline-block;
        margin-bottom: 12px;
    }
    .choice-badge span {
        color: #FF9900;
    }
    .price-discount {
        color: #CC0C39;
        font-size: 1.7rem;
        font-weight: 300;
        margin-right: 8px;
    }
    .price-current {
        font-size: 1.85rem;
        font-weight: 600;
        color: #0F1111;
    }
    .price-symbol {
        font-size: 1.1rem;
        vertical-align: super;
    }
    .price-mrp {
        color: #565959;
        font-size: 0.88rem;
        margin-top: 2px;
    }
    .mrp-strike {
        text-decoration: line-through;
    }
    .pdp-spec-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 0.88rem;
    }
    .pdp-spec-table td {
        padding: 6px 8px;
    }
    .pdp-spec-label {
        font-weight: 600;
        color: #0F1111;
        width: 35%;
    }
    .pdp-spec-val {
        color: #333333;
    }
    .pdp-bullet-list {
        margin: 10px 0 20px 0;
        padding-left: 20px;
        font-size: 0.92rem;
        line-height: 1.6;
        color: #0F1111;
    }
    .pdp-bullet-list li {
        margin-bottom: 8px;
    }
    .buybox-card {
        border: 1px solid #D5D9D9;
        border-radius: 8px;
        padding: 16px;
        background: #FFFFFF;
    }
    .buybox-price {
        font-size: 1.5rem;
        font-weight: 600;
        color: #B12704;
    }
    .buybox-instock {
        color: #007600;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 8px 0;
    }
    .buybox-meta {
        font-size: 0.82rem;
        color: #565959;
        line-height: 1.4;
    }
    .btn-cart-amazon {
        background: #FFD814;
        border: 1px solid #FCD200;
        border-radius: 20px;
        color: #0F1111;
        font-weight: 600;
        font-size: 0.9rem;
        text-align: center;
        padding: 8px 12px;
        margin: 10px 0 6px 0;
        display: block;
        box-shadow: 0 2px 5px rgba(213, 217, 217, 0.5);
    }
    .btn-buy-amazon {
        background: #FFA41C;
        border: 1px solid #FF8F00;
        border-radius: 20px;
        color: #0F1111;
        font-weight: 600;
        font-size: 0.9rem;
        text-align: center;
        padding: 8px 12px;
        margin-bottom: 12px;
        display: block;
        box-shadow: 0 2px 5px rgba(213, 217, 217, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="pdp-container">', unsafe_allow_html=True)

    # Header Alert Bar
    st.markdown(f"""
    <div style="background:#FFF8E7; border-left:4px solid #FF9900; padding:10px 16px; border-radius:4px; margin-bottom:18px; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <b style="color:#B12704;">LIVE AMAZON BUYER PAGE PREVIEW</b>
            <span style="color:#565959; font-size:0.85rem; margin-left:8px;">This simulates the exact customer view on Amazon.in before submitting.</span>
        </div>
        <span class="badge-success">SKU: {off.seller_sku}</span>
    </div>
    """, unsafe_allow_html=True)

    # 3-Column Amazon PDP Layout: (Left: Gallery | Middle: Buy Info & Bullets | Right: Buy Box)
    col_gallery, col_center, col_buybox = st.columns([1.6, 2.5, 1.2])

    # -------------------------------------------------------------
    # LEFT COLUMN: Interactive Photo Reel & Main Image Zoom
    # -------------------------------------------------------------
    with col_gallery:
        st.markdown("**Product Gallery (5 Angles):**")

        # Select which image slot to view in main view
        available_slots = []
        for s in range(1, 6):
            if s in processed_images and processed_images[s] is not None:
                available_slots.append(s)
            elif s in raw_images and raw_images[s] is not None:
                available_slots.append(s)

        if not available_slots:
            st.info("No photos uploaded yet. Using default thumbnail.")
            selected_slot = 1
        else:
            slot_labels = {
                1: "1. Main View (Pure White #FFF)",
                2: "2. Side Profile & Rivets",
                3: "3. Top Interior Cooking Surface",
                4: "4. Dimensions & Scale",
                5: "5. Packaging & In-Use"
            }
            selected_slot = st.radio(
                "Select Angle to Inspect:",
                options=available_slots,
                format_func=lambda s: slot_labels.get(s, f"Photo {s}"),
                horizontal=False,
                key="pdp_selected_image_slot"
            )

        # Display Selected Image
        display_img = None
        is_processed = False
        if selected_slot in processed_images and processed_images[selected_slot] is not None:
            display_img = processed_images[selected_slot]["processed_image"]
            is_processed = True
        elif selected_slot in raw_images and raw_images[selected_slot] is not None:
            display_img = raw_images[selected_slot]

        if display_img:
            st.image(
                display_img,
                caption=f"Slot {selected_slot} • {'2000x2000 Pure White #FFFFFF' if is_processed else 'Raw Image'}",
                use_container_width=True
            )
            if is_processed:
                st.markdown("<div style='text-align:center;'><span class='badge-success'>Pure White Background (255, 255, 255)</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='text-align:center;'><span class='badge-warning'>Raw image (not yet processed with rembg)</span></div>", unsafe_allow_html=True)
        else:
            st.warning("No image available for this slot.")

    # -------------------------------------------------------------
    # MIDDLE COLUMN: Product Info, Price, Bullets & Specs
    # -------------------------------------------------------------
    with col_center:
        # Brand Link
        st.markdown(f'<a href="#" class="amazon-brand-link">Visit the {ident.brand_name} Store</a>', unsafe_allow_html=True)

        # Title
        st.markdown(f'<div class="pdp-title">{ident.item_name}</div>', unsafe_allow_html=True)

        # Ratings & Badges
        st.markdown("""
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
            <div class="pdp-stars">4.6 ★★★★★ <span class="pdp-rating-count">(142 ratings)</span></div>
            <span style="color:#565959; font-size:0.85rem;">| 200+ bought in past month</span>
        </div>
        <div class="choice-badge">Amazon\'s <span>Choice</span> in Cookware Kadhais & Pans</div>
        <hr style="margin: 8px 0 14px 0; border: none; border-top: 1px solid #EAEAEA;">
        """, unsafe_allow_html=True)

        # Pricing Block
        disc_pct = off.discount_percent
        st.markdown(f"""
        <div style="margin-bottom: 12px;">
            <div>
                <span class="price-discount">-{disc_pct:.0f}%</span>
                <span class="price-current"><span class="price-symbol">₹</span>{off.standard_price:,.2f}</span>
            </div>
            <div class="price-mrp">
                M.R.P.: <span class="mrp-strike">₹{off.list_price:,.2f}</span>
                <span style="margin-left: 8px; color: #007600; font-weight: 600;">You Save ₹{(off.list_price - off.standard_price):,.2f}</span>
            </div>
            <div style="font-size: 0.8rem; color: #565959; margin-top: 4px;">Inclusive of all taxes</div>
            <div style="font-size: 0.82rem; color: #007185; margin-top: 2px; font-weight: 500;">
                EMI starts at ₹92 per month. EMI options available.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Key Specification Table
        st.markdown(f"""
        <table class="pdp-spec-table">
            <tr><td class="pdp-spec-label">Brand</td><td class="pdp-spec-val">{ident.brand_name}</td></tr>
            <tr><td class="pdp-spec-label">Material</td><td class="pdp-spec-val">{det.material}</td></tr>
            <tr><td class="pdp-spec-label">Capacity</td><td class="pdp-spec-val">{det.capacity}</td></tr>
            <tr><td class="pdp-spec-label">Color & Finish</td><td class="pdp-spec-val">{det.color} ({det.finish_type})</td></tr>
            <tr><td class="pdp-spec-label">Product Dimensions</td><td class="pdp-spec-val">{det.package_dimensions}</td></tr>
            <tr><td class="pdp-spec-label">Item Weight</td><td class="pdp-spec-val">{det.item_weight}</td></tr>
            <tr><td class="pdp-spec-label">Special Features</td><td class="pdp-spec-val">{"Induction & Gas Compatible" if det.is_induction_compatible else "Gas Safe"}, {"Dishwasher Safe" if det.is_dishwasher_safe else "Hand Wash"}</td></tr>
        </table>
        <hr style="margin: 12px 0; border: none; border-top: 1px solid #EAEAEA;">
        """, unsafe_allow_html=True)

        # 5 Benefit-Driven Bullet Points
        st.markdown("**About this item:**")
        bullets = desc.get_bullet_points()
        bullet_html = "<ul class='pdp-bullet-list'>"
        for b in bullets:
            if b.strip():
                # Highlight [BRACKETED BENEFIT] in bold if present
                text = b.strip()
                if text.startswith("[") and "]" in text:
                    tag_end = text.index("]") + 1
                    header = text[:tag_end]
                    rest = text[tag_end:]
                    bullet_html += f"<li><b>{header}</b>{rest}</li>"
                else:
                    bullet_html += f"<li>{text}</li>"
        bullet_html += "</ul>"
        st.markdown(bullet_html, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # RIGHT COLUMN: Authentic Amazon Buy Box
    # -------------------------------------------------------------
    with col_buybox:
        fulfillment_label = "Fulfilled by Amazon" if off.fulfillment_channel == "AMAZON_NA" else "Merchant Fulfilled"
        st.markdown(f"""
        <div class="buybox-card">
            <div class="buybox-price">₹{off.standard_price:,.2f}</div>
            <div style="font-size:0.85rem; color:#007185; margin-top:2px;">
                <b>FREE delivery</b> Tomorrow.<br>
                Order within <b>4 hrs 28 mins</b>.
            </div>
            <div style="font-size:0.82rem; color:#0F1111; margin-top:6px;">
                📍 Deliver to Haris - Chennai 600058
            </div>
            <div class="buybox-instock">In stock</div>
            <div style="font-size:0.85rem; color:#0F1111; margin-bottom:8px;">
                Quantity: <b>1</b> (Stock: {off.quantity})
            </div>
            
            <div class="btn-cart-amazon">Add to Cart</div>
            <div class="btn-buy-amazon">Buy Now</div>
            
            <div class="buybox-meta">
                <table style="width:100%; font-size:0.78rem;">
                    <tr><td style="color:#565959;">Ships from</td><td style="color:#0F1111; font-weight:600;">Amazon</td></tr>
                    <tr><td style="color:#565959;">Sold by</td><td style="color:#007185; font-weight:600;">{ident.brand_name} Store</td></tr>
                    <tr><td style="color:#565959;">Returns</td><td style="color:#007185;">10-day replacement</td></tr>
                    <tr><td style="color:#565959;">Warranty</td><td style="color:#0F1111;">1-Year Domestic</td></tr>
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # BOTTOM SECTION: Manufacturer Description & Technical Details
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Product Description & Manufacturer Highlights")
    st.markdown(f"""
    <div style="background:#FDFDFD; border:1px solid #EAEAEA; padding:18px 24px; border-radius:6px; font-size:0.92rem; line-height:1.7;">
        {desc.product_description}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Technical Compliance & Specifications")
    c_tech1, c_tech2 = st.columns(2)
    with c_tech1:
        st.markdown(f"""
        - **Country of Origin:** {comp.country_of_origin}
        - **HSN Code:** `{comp.hsn_code}` (GST Tax Code: `{comp.gst_tax_code}`)
        - **Manufacturer:** {comp.manufacturer}
        - **Packer Information:** {comp.packer_details}
        """)
    with c_tech2:
        st.markdown(f"""
        - **Item Model Number:** `{ident.model_number}`
        - **Item Part / SKU:** `{off.seller_sku}`
        - **Product ID / Barcode:** `{ident.product_id}` ({ident.product_id_type})
        - **Safety Certifications:** {comp.compliance_certification}
        """)

    st.markdown('</div>', unsafe_allow_html=True)
