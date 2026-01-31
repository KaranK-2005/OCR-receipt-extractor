import re

def extract_invoice_number(text):
    patterns = [
        r'invoice\s*(no|number)?\s*[:\-]?\s*([A-Z0-9\-]+)',
        r'inv\s*[:\-]?\s*([A-Z0-9\-]+)',
        r'bill\s*no\s*[:\-]?\s*([A-Z0-9\-]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(match.lastindex)
    return None


def extract_date(text):
    match = re.search(r'\d{2}[/-]\d{2}[/-]\d{4}', text)
    return match.group(0) if match else None


def extract_total_amount(text):
    patterns = [
        r'total amount\s*[:\-]?\s*₹?\s*(\d+\.?\d*)',
        r'grand total\s*[:\-]?\s*₹?\s*(\d+\.?\d*)',
        r'\btotal\b\s*[:\-]?\s*₹?\s*(\d+\.?\d*)'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return float(matches[-1])
    return None


def extract_currency(text):
    lower_text = text.lower()

    if "₹" in text or "rs" in lower_text or "inr" in lower_text:
        return "INR"
    if "$" in text or "usd" in lower_text:
        return "USD"

    if re.search(r'\d{2}/\d{2}/\d{4}', text):
        return "INR"

    return None


def extract_merchant_name(text):
    return text.split()[0] if text else None


def extract_line_items(text):
    items = []
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if len(line) < 5:
            continue

        if any(word in line.lower() for word in [
            "item", "qty", "price",
            "total", "subtotal", "gst", "tax", "amount"
        ]):
            continue

        tokens = line.split()

        if len(tokens) >= 3 and tokens[-2].isdigit():
            try:
                items.append({
                    "item": " ".join(tokens[:-2]),
                    "quantity": int(tokens[-2]),
                    "price": float(tokens[-1])
                })
            except ValueError:
                continue

    return items


def parse_text(text):
    cleaned_text = text.replace("T0TAL", "TOTAL")

    return {
        "merchant_name": extract_merchant_name(cleaned_text),
        "invoice_number": extract_invoice_number(cleaned_text),
        "date": extract_date(cleaned_text),
        "total_amount": extract_total_amount(cleaned_text),
        "currency": extract_currency(cleaned_text),
        "line_items": extract_line_items(cleaned_text)
    }
