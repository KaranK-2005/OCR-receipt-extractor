# 🧾 OCR Receipt & Invoice Data Extraction System

## 📌 Overview

This project is an OCR-based data extraction system that processes receipt and invoice images or PDFs and converts them into structured JSON outputs.

The pipeline is designed for **real-world variability** and can handle:
- Different document layouts
- Printed and scanned inputs
- Digital invoices
- Varying fonts and resolutions
- Common OCR imperfections

It uses **EasyOCR** for text recognition and **rule-based parsing (regex + heuristics)** to identify important financial and vendor information.

---

## 🎯 Objective

To build a practical and robust OCR pipeline that:

- Accepts images and PDFs  
- Extracts text reliably  
- Identifies key structured fields  
- Produces machine-readable JSON  
- Works across multiple document styles without being tuned to a single template  

---

## 📥 Input

The system accepts:

- Receipt or invoice images (`.jpg`, `.jpeg`, `.png`)
- PDF documents (single or multi-page)
- Mixed formats within the same folder

### Example
```
input/
├── receipt1.png
├── receipt2.jpg
├── invoice.pdf
```

---

## 📤 Output

For each input file, a corresponding JSON file is generated in the `output/` directory.

### Extracted Fields
- Merchant / Vendor Name  
- Invoice Number (if present)  
- Date  
- Total Amount (prioritizes Balance Due / Amount Due when available)  
- Currency  
- Line Items (best-effort)

---

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

> Line-item extraction is heuristic-based and may be partial depending on OCR quality and table complexity.

---

## 🧠 Key Design Principles

- Robustness over perfection  
- Graceful handling of noisy OCR  
- Avoid crashes in batch scenarios  
- Work across diverse real-world formats  
- Keep logic explainable and maintainable  

---

## 🛠️ Technologies Used

- Python  
- EasyOCR – text detection & recognition  
- OpenCV – preprocessing & normalization  
- Regex – rule-based information extraction  
- NumPy  
- Pillow  
- pdf2image – PDF → image conversion  

---

## 📁 Project Structure

```
ocr-receipt-extractor/
│
├── input/               # Documents to process
├── output/              # JSON outputs generated per file
│
├── src/
│   ├── preprocess.py    # Image normalization & safety
│   ├── ocr.py           # OCR execution
│   ├── parser.py        # Field extraction logic
│   └── main.py          # Entry point (file or folder)
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/KaranK-2005/OCR-receipt-extractor.git
cd OCR-receipt-extractor
pip install -r requirements.txt
```

### PDF Support (Windows)
Ensure **Poppler** is installed and available in PATH.

---

## ▶️ How to Run

### Process a single file
```bash
python src/main.py input/sample.png
```

### Process an entire folder (recommended)
```bash
python src/main.py input/
```

Outputs will be saved as:
```
output/<filename>.json
```

---

## 🔁 Batch Processing Capability

The system supports running against large sets of documents.  
Each file is processed independently so a failure in one document will not interrupt others.

This makes the pipeline suitable for:
- Bulk testing  
- Vendor variability  
- Real-world invoice collections  

---

## 🧪 Robustness Improvements Implemented

- Adaptive preprocessing for high-resolution inputs  
- Safe resizing to prevent OCR memory crashes  
- Defensive handling of unreadable or extreme images  
- Priority detection for final payable fields  
- Flexible parsing across table variations  
- Non-blocking multi-file execution  

---

## ⚠️ Limitations

- Line-item extraction is heuristic-based  
- Very complex tables may yield partial results  
- OCR accuracy depends on scan quality  
- Some documents may require vendor-specific tuning for perfect extraction  

---

## 🚀 Possible Future Enhancements

- ML-based table structure detection  
- Confidence scoring for extracted fields  
- Vendor template recognition  
- REST API / UI interface  
- Human-in-the-loop correction workflow  

---

