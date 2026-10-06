"""Prep a portrait for ASCII conversion.

1. Remove the background (rembg) so only the subject remains.
2. Boost local contrast with CLAHE so a flatly lit face gets real
   highlights and shadows.
3. Composite onto white so the background maps to spaces.

Usage: python scripts/prep_photo.py source-photo.png
Writes: source-prepped.png (grayscale)
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.png"
img = Image.open(src).convert("RGB")

cut = remove(img, session=new_session("u2net_human_seg"))  # light model (~170MB)
rgba = np.array(cut).astype(np.float32)
alpha = rgba[..., 3:4] / 255.0

gray = cv2.cvtColor(rgba[..., :3].astype(np.uint8), cv2.COLOR_RGB2GRAY)
clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
gray = clahe.apply(gray).astype(np.float32)

# Lift the darkest tones slightly so hair/suit keep some texture
gray = 255 * (gray / 255) ** 0.85

out = gray * alpha[..., 0] + 255 * (1 - alpha[..., 0])
Image.fromarray(out.clip(0, 255).astype(np.uint8), "L").save("source-prepped.png")
print("wrote source-prepped.png")
