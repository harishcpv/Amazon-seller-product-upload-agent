"""Vision & Background Agent for Amazon AutoList Studio.

Strips product photo backgrounds using rembg, normalizes canvas to 2000x2000px,
and centers the product on a pure white (#FFFFFF / RGB 255,255,255) background
with strict 85% Amazon frame fill ratio compliance.
"""

import io
from typing import Optional, Tuple, Dict, Any, List
from PIL import Image, ImageOps, ImageFilter
import numpy as np

from core.config import IMAGE_CONFIG

# Module-level cached rembg session
_REMBG_SESSION = None


def get_rembg_session():
    """Lazily load and cache the rembg session for fast batch processing."""
    global _REMBG_SESSION
    if _REMBG_SESSION is None:
        try:
            import rembg
            # Use default 'u2net' or fast session
            _REMBG_SESSION = rembg.new_session()
        except Exception as e:
            print(f"[VisionAgent] Note on rembg session: {e}")
            _REMBG_SESSION = False
    return _REMBG_SESSION


class VisionBackgroundAgent:
    """Agent responsible for image background removal, centering, and Amazon 2000x2000 pure white standardization."""

    def __init__(self, target_size: Tuple[int, int] = (2000, 2000), fill_ratio: float = 0.85):
        self.target_size = target_size
        self.fill_ratio = fill_ratio # Product occupies 85% of target canvas
        self.target_width, self.target_height = target_size
        self.white_rgb = IMAGE_CONFIG["pure_white_rgb"]

    def remove_background(self, input_image: Image.Image) -> Image.Image:
        """Removes the background using rembg with fallback logic."""
        # Ensure image is in RGBA mode for transparency
        img = input_image.convert("RGBA")

        session = get_rembg_session()
        if session:
            try:
                import rembg
                # Strip background
                transparent_img = rembg.remove(img, session=session)
                return transparent_img
            except Exception as e:
                print(f"[VisionAgent] rembg remove error, applying smart fallback: {e}")

        # Smart fallback: If rembg fails or unavailable, apply intelligent alpha mask
        return self._smart_alpha_fallback(img)

    def _smart_alpha_fallback(self, img: Image.Image) -> Image.Image:
        """Fallback background isolator based on edge luminance and corner color sampling."""
        img_np = np.array(img)
        # Sample corner pixels to estimate background color
        h, w, c = img_np.shape
        corner_colors = [
            img_np[0, 0, :3],
            img_np[0, -1, :3],
            img_np[-1, 0, :3],
            img_np[-1, -1, :3]
        ]
        bg_estimate = np.mean(corner_colors, axis=0)

        # Compute Euclidean color distance from estimated background
        diff = np.linalg.norm(img_np[:, :, :3] - bg_estimate, axis=2)
        threshold = 28.0
        alpha = np.clip((diff - threshold) * 8.0, 0, 255).astype(np.uint8)

        # Smooth alpha mask
        alpha_img = Image.fromarray(alpha, mode="L").filter(ImageFilter.GaussianBlur(radius=1.5))
        r, g, b = img.split()[:3]
        result = Image.merge("RGBA", (r, g, b, alpha_img))
        return result

    def center_and_pad_to_white(
        self,
        transparent_image: Image.Image,
        fill_ratio: Optional[float] = None
    ) -> Image.Image:
        """Crops tightly to the product object, scales to 85% canvas fill,

        and centers it onto a pure #FFFFFF 2000x2000px canvas.
        """
        ratio = fill_ratio or self.fill_ratio
        
        # Ensure RGBA
        rgba = transparent_image.convert("RGBA")
        
        # Get bounding box of visible content (where alpha > 12)
        alpha = rgba.split()[3]
        # Threshold alpha to ignore faint artifacts
        binary_alpha = alpha.point(lambda p: 255 if p > 12 else 0)
        bbox = binary_alpha.getbbox()

        if bbox is None:
            # Entire image is empty or transparent, return pure white canvas
            return Image.new("RGB", self.target_size, self.white_rgb)

        # Crop tightly to product boundaries
        product_crop = rgba.crop(bbox)
        crop_w, crop_h = product_crop.size

        # Determine target bounding box based on fill ratio
        max_allowed_w = int(self.target_width * ratio)
        max_allowed_h = int(self.target_height * ratio)

        # Calculate uniform scaling factor
        scale_w = max_allowed_w / max(crop_w, 1)
        scale_h = max_allowed_h / max(crop_h, 1)
        scale_factor = min(scale_w, scale_h)

        # Resize product smoothly
        new_w = max(int(crop_w * scale_factor), 1)
        new_h = max(int(crop_h * scale_factor), 1)
        scaled_product = product_crop.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Create pure white background canvas: RGB (255, 255, 255)
        white_canvas = Image.new("RGBA", self.target_size, (255, 255, 255, 255))

        # Calculate dead-center coordinates
        offset_x = (self.target_width - new_w) // 2
        offset_y = (self.target_height - new_h) // 2

        # Paste product with transparency mask
        white_canvas.paste(scaled_product, (offset_x, offset_y), scaled_product)

        # Convert back to pure RGB for Amazon compliance (no alpha channel in final JPEG)
        final_rgb = white_canvas.convert("RGB")
        return final_rgb

    def process_single_image(
        self,
        raw_image: Image.Image,
        strip_bg: bool = True
    ) -> Dict[str, Any]:
        """Full pipeline for a single product image:

        1. Ingests raw photo
        2. Strips background with rembg
        3. Scales and centers on 2000x2000 pure white canvas
        4. Validates Amazon image compliance
        """
        orig_w, orig_h = raw_image.size

        if strip_bg:
            transparent = self.remove_background(raw_image)
            standardized = self.center_and_pad_to_white(transparent, self.fill_ratio)
        else:
            # Direct resize/pad without stripping background
            standardized = self._direct_pad_to_white(raw_image)

        # Quality & Compliance check
        compliance = self.verify_amazon_compliance(standardized)

        # Convert to JPEG bytes for quick download & storage
        buf = io.BytesIO()
        standardized.save(buf, format="JPEG", quality=IMAGE_CONFIG["output_quality"], optimize=True)
        jpeg_bytes = buf.getvalue()

        return {
            "processed_image": standardized,
            "image_bytes": jpeg_bytes,
            "original_dimensions": (orig_w, orig_h),
            "final_dimensions": standardized.size,
            "compliance": compliance,
            "size_kb": len(jpeg_bytes) / 1024.0,
        }

    def _direct_pad_to_white(self, img: Image.Image) -> Image.Image:
        """Pads an already clean image into 2000x2000 canvas with pure white background."""
        img_rgb = img.convert("RGB")
        max_dim = int(self.target_width * self.fill_ratio)
        img_copy = img_rgb.copy()
        img_copy.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

        canvas = Image.new("RGB", self.target_size, self.white_rgb)
        offset_x = (self.target_width - img_copy.width) // 2
        offset_y = (self.target_height - img_copy.height) // 2
        canvas.paste(img_copy, (offset_x, offset_y))
        return canvas

    def verify_amazon_compliance(self, img: Image.Image) -> Dict[str, Any]:
        """Verifies if the processed image satisfies Amazon Main Image Standards:

        - Exact dimensions >= 1000px, 2000x2000 for zoom
        - Corner pixels are pure white (255, 255, 255)
        - Color profile is sRGB/RGB
        """
        w, h = img.size
        is_2000 = (w == 2000 and h == 2000)
        
        # Check corner pixels for pure white (255, 255, 255)
        np_img = np.array(img)
        corners = [
            tuple(np_img[0, 0][:3]),
            tuple(np_img[0, -1][:3]),
            tuple(np_img[-1, 0][:3]),
            tuple(np_img[-1, -1][:3]),
            tuple(np_img[5, 5][:3]),
            tuple(np_img[-5, -5][:3]),
        ]
        
        all_pure_white = all(c == (255, 255, 255) for c in corners)

        return {
            "is_compliant": is_2000 and all_pure_white,
            "dimensions_ok": is_2000,
            "pure_white_background": all_pure_white,
            "zoom_enabled": (w >= 1600 and h >= 1600),
            "color_mode": img.mode,
            "corner_samples": corners[:4],
        }


# Module level convenience function
def process_product_photos(
    images_dict: Dict[int, Image.Image],
    strip_bg: bool = True
) -> Dict[int, Dict[str, Any]]:
    """Batch process up to 5 images corresponding to the 5 Amazon photo slots."""
    agent = VisionBackgroundAgent()
    results = {}
    for slot_idx, raw_img in images_dict.items():
        if raw_img is not None:
            results[slot_idx] = agent.process_single_image(raw_img, strip_bg=strip_bg)
    return results
