import os
from pdf2image import convert_from_path
import cv2
import numpy as np
import tempfile

def pdf_to_images(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    images = convert_from_path(pdf_path)

    image_paths = []

    with tempfile.TemporaryDirectory() as temp_dir:
        for i, page in enumerate(images):
            image_path = os.path.join(temp_dir, f"page_{i}.png")
            page.save(image_path, "PNG")

            img = cv2.imread(image_path)
            image_paths.append(img)

    return image_paths
