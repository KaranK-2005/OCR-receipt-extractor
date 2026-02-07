import os
import sys
import json
from preprocess import preprocess_image, preprocess_image_from_array
from ocr import extract_text, extract_text_with_boxes
from parser import parse_text
from pdf_utils import pdf_to_images


def process_single_file(file_path):
    full_text = ""
    all_ocr_results = []
    debug_ocr = os.environ.get("OCR_DEBUG", "").strip() == "1"

    if file_path.lower().endswith(".pdf"):
        pages = pdf_to_images(file_path)
        for page in pages:
            processed = preprocess_image_from_array(page)
            page_text, page_results = extract_text_with_boxes(processed)
            full_text += page_text + "\n"
            all_ocr_results.extend(page_results)
    else:
        processed = preprocess_image(file_path)
        full_text, all_ocr_results = extract_text_with_boxes(processed)

    parsed_data = parse_text(full_text, ocr_results=all_ocr_results)

    os.makedirs("output", exist_ok=True)
    for name in os.listdir("output"):
        if name.lower().endswith(".json"):
            os.remove(os.path.join("output", name))

    output_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join("output", f"{output_name}.json")

    with open(output_path, "w") as f:
        json.dump(parsed_data, f, indent=4)

    if debug_ocr:
        os.makedirs("output/_debug", exist_ok=True)
        output_name = os.path.splitext(os.path.basename(file_path))[0]

        def _to_serializable(obj):
            try:
                import numpy as np
                if isinstance(obj, np.generic):
                    return obj.item()
            except Exception:
                pass
            if isinstance(obj, (list, tuple)):
                return [_to_serializable(x) for x in obj]
            if isinstance(obj, dict):
                return {k: _to_serializable(v) for k, v in obj.items()}
            return obj

        with open(os.path.join("output", "_debug", f"{output_name}.ocr.json"), "w") as f:
            json.dump(_to_serializable(all_ocr_results), f, indent=2)

    print(f"Saved {output_path}")


def main(input_path):
    if not os.path.exists(input_path):
        print(f"Input path not found: {input_path}")
        return

    if os.path.isdir(input_path):
        files = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".pdf", ".tif", ".tiff", ".bmp", ".webp"))
        ]

        if not files:
            print("No valid input files found in folder.")
            return

        for file_path in files:
            print(f"Processing: {file_path}")
            try:
                process_single_file(file_path)
            except Exception as e:
                print(f"Failed to process {file_path}: {e}")

    else:
        process_single_file(input_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <file_or_folder_path>")
    else:
        main(sys.argv[1])
