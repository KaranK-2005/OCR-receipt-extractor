# 🧾 OCR Receipt Data Extraction System

## 📌 Overview

This project is an OCR-based data extraction system that processes receipt or bill images and extracts key information into a structured JSON format.

The system is designed to handle:
- Different receipt layouts
- Varying fonts and image quality
- Common OCR errors

It uses **EasyOCR** for text extraction and **rule-based parsing** (regex + heuristics) to identify required fields.

---

## 🎯 Objective

To build a practical OCR pipeline that:
- Accepts receipt/bill images (and PDFs)
- Extracts text using OCR
- Identifies important fields
- Outputs the result in a structured JSON format

---

## 📥 Input

- Receipt or bill images (`.jpg`, `.png`)
- (Optional) PDF files
- Different layouts and formats

### Sample Input
```
input/sample.png
```

---

## 📤 Output

Structured JSON containing:
- Merchant / Vendor Name
- Invoice Number
- Date
- Total Amount
- Currency
- Line Items (heuristic-based, may be partial)

### Sample Output
```json
{
  "merchant_name": "RELIANCE",
  "invoice_number": "INV123456",
  "date": "28/01/2025",
  "total_amount": 189.0,
  "currency": "INR",
  "line_items": [
    {
      "item": "Milk",
      "quantity": 2,
      "price": 60.0
    }
  ]
}
```

> **Note:** Line-item extraction is heuristic-based and may be partial due to OCR noise and layout variations.

---

## 🛠️ Technologies Used

- Python
- EasyOCR – Optical Character Recognition
- OpenCV – Image preprocessing
- Regex (`re` module) – Rule-based parsing
- NumPy
- Pillow
- pdf2image (optional PDF support)

---

## 📁 Project Structure

```
ocr-receipt-extractor/
│
├── input/
│   └── sample.png
│
├── output/
│   └── result.json
│
├── src/
│   ├── preprocess.py
│   ├── ocr.py
│   ├── parser.py
│   └── main.py
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/KaranK-2005/ocr-receipt-extractor.git
cd ocr-receipt-extractor
pip install -r requirements.txt
```

---

## ▶️ How to Run

```bash
python src/main.py input/sample.png
```

Output will be saved in:
```
output/result.json
```

---

## ⚠️ Limitations

- Line-item extraction is heuristic-based
- OCR output varies with image quality and layout
- Partial line-item extraction is expected

---

## 🚀 Future Improvements

- Improve line-item recall
- Add confidence scores
- Support multiple languages
- Add web or API interface
