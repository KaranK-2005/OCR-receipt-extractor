import sys
import json
from preprocess import preprocess_image
from ocr import extract_text
from parser import parse_text

def main(image_path):
    image = preprocess_image(image_path)
    text = extract_text(image)
    result = parse_text(text)

    with open("output/result.json", "w") as file:
        json.dump(result, file, indent=4)

    print("Extraction completed. Check output/result.json")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/main.py <image_path>")
    else:
        main(sys.argv[1])
