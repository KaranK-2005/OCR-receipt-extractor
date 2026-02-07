import re


def extract_invoice_number(text):
    patterns = [
        r'invoice\s*(?:no|number)?\s*[:\-]?\s*([A-Z0-9\-]+)',
        r'inv\s*[:\-]?\s*([A-Z0-9\-]+)',
        r'bill\s*no\s*[:\-]?\s*([A-Z0-9\-]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match and match.groups():
            return match.group(1)
    return None



def extract_date(text):
    patterns = [
        r'\d{2}[/-]\d{2}[/-]\d{4}',
        r'\d{4}[/-]\d{2}[/-]\d{2}'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    return None


def extract_total_amount(text):
    priority_patterns = [
        r'(?:balance\s*due|amount\s*due)\s*[:\-]?\s*[₹$]?\s*(\d+\.?\d*)',
        r'grand\s*total\s*[:\-]?\s*[₹$]?\s*(\d+\.?\d*)',
        r'total\s*amount\s*[:\-]?\s*[₹$]?\s*(\d+\.?\d*)'
    ]

    for pattern in priority_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match and match.groups():
            return float(match.group(1))

    amounts = re.findall(r'[₹$]?\s*(\d+\.\d{2})', text)
    if amounts:
        return float(amounts[-1])

    return None

def extract_currency(text):
    text_lower = text.lower()

    if "₹" in text or "rs" in text_lower or "inr" in text_lower:
        return "INR"
    if "$" in text or "usd" in text_lower:
        return "USD"

    return None


def extract_merchant_name(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    ignore_keywords = [
        "invoice", "bill to", "ship to",
        "date", "invoice no", "invoice number"
    ]

    for line in lines[:5]:
        lower = line.lower()
        if not any(k in lower for k in ignore_keywords):
            if len(line.split()) <= 6:
                return line

    return None


def _to_number_token(token):
    cleaned = token.replace(",", "").replace("$", "").replace("₹", "").replace("Rs", "").replace("rs", "")
    if re.fullmatch(r'\d+(\.\d+)?', cleaned):
        return float(cleaned)
    return None


def extract_line_items_from_ocr(results):
    items = []
    if not results:
        return items

    heights = []
    for bbox, _, _ in results:
        ys = [pt[1] for pt in bbox]
        heights.append(max(ys) - min(ys))
    median_height = sorted(heights)[len(heights) // 2] if heights else 10
    bucket = max(6, int(median_height * 0.6))

    rows = {}
    for bbox, text, conf in results:
        xs = [pt[0] for pt in bbox]
        ys = [pt[1] for pt in bbox]
        y_center = (min(ys) + max(ys)) / 2.0
        x_center = (min(xs) + max(xs)) / 2.0
        y_bucket = int(y_center // bucket)
        rows.setdefault(y_bucket, []).append((x_center, text))

    header_cols = {}
    for y in sorted(rows.keys()):
        cells = sorted(rows[y], key=lambda c: c[0])
        header_text = " ".join([c[1] for c in cells]).lower()
        if all(k in header_text for k in ["item", "qty"]) and ("price" in header_text or "total" in header_text):
            for x, t in cells:
                t_lower = t.lower()
                if t_lower in ("item", "items", "description"):
                    header_cols["item"] = x
                elif t_lower in ("qty", "quantity"):
                    header_cols["qty"] = x
                elif t_lower in ("price", "rate", "unit"):
                    header_cols["price"] = x
                elif t_lower in ("total", "amount"):
                    header_cols["total"] = x
            break

    def _closest_col(x):
        if not header_cols:
            return None
        closest = min(header_cols.items(), key=lambda kv: abs(x - kv[1]))
        return closest[0]

    def _is_excluded_line(text):
        lower = text.lower()
        if any(k in lower for k in [
            "total", "subtotal", "tax", "vat", "gst", "amount due",
            "balance due", "grand total", "change", "cash", "card",
            "thank you", "paid", "payment", "tender", "invoice",
            "date", "time", "table", "server"
        ]):
            return True

        letters_only = re.sub(r'[^a-z]', '', lower)
        if letters_only.startswith(("tot", "tax", "vat", "gst", "amt", "due", "bal", "sub")):
            return True
        if letters_only in ("tex", "totd", "tota", "totl"):
            return True

        return False

    pending_item = None
    for y in sorted(rows.keys()):
        cells = sorted(rows[y], key=lambda c: c[0])
        line_text = " ".join([c[1] for c in cells])
        if len(line_text) < 5:
            continue

        lower = line_text.lower()
        if any(k in lower for k in [
            "description", "qty", "quantity",
            "price", "total", "subtotal",
            "tax", "amount"
        ]) or _is_excluded_line(line_text):
            continue

        if header_cols:
            row = {"item": "", "qty": None, "price": None, "total": None}
            for x, t in cells:
                col = _closest_col(x)
                if col == "item":
                    row["item"] = (row["item"] + " " + t).strip()
                else:
                    val = _to_number_token(t)
                    if val is not None:
                        if col == "qty":
                            row["qty"] = val
                        elif col == "price":
                            row["price"] = val
                        elif col == "total":
                            row["total"] = val

            if row["item"] and (row["qty"] is not None or row["total"] is not None or row["price"] is not None):
                qty_val = int(round(row["qty"])) if row["qty"] is not None else 1
                unit_price = row["price"]
                line_total = row["total"]

                if unit_price is not None and line_total is not None and qty_val == 1:
                    if line_total < unit_price:
                        unit_price, line_total = line_total, unit_price

                item_obj = {
                    "item": row["item"],
                    "quantity": qty_val,
                    "price": float(line_total if line_total is not None else (unit_price or 0.0))
                }
                if unit_price is not None:
                    item_obj["unit_price"] = float(unit_price)
                items.append(item_obj)
            continue

        tokens = [c[1] for c in cells]
        alpha_tokens = [t for t in tokens if re.search(r'[A-Za-z]', t)]
        numeric_tokens = []
        for t in tokens:
            val = _to_number_token(t)
            if val is not None:
                numeric_tokens.append({"value": val, "token": t})

        if alpha_tokens and numeric_tokens:
            item = " ".join(alpha_tokens).strip()
            price = numeric_tokens[-1]["value"]

            qty = None
            int_candidates = [n["value"] for n in numeric_tokens if float(n["value"]).is_integer() and 1 <= n["value"] <= 100]
            if int_candidates:
                qty = int(min(int_candidates))
            else:
                qty = 1

            item_obj = {
                "item": item,
                "quantity": qty,
                "price": float(price)
            }

            if len(numeric_tokens) >= 2:
                unit_price = numeric_tokens[-2]["value"]
                if unit_price != price:
                    item_obj["unit_price"] = float(unit_price)

            items.append(item_obj)
            pending_item = None
            continue

        if numeric_tokens and not alpha_tokens and pending_item:
            price = numeric_tokens[-1]["value"]
            items.append({
                "item": pending_item,
                "quantity": 1,
                "price": float(price)
            })
            pending_item = None
            continue

        if alpha_tokens and not numeric_tokens:
            pending_item = " ".join(alpha_tokens).strip()
            continue

    return items


def extract_line_items(text):
    items = []
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if len(line) < 5:
            continue

        if any(k in line.lower() for k in [
            "description", "qty", "quantity",
            "price", "total", "subtotal",
            "tax", "amount"
        ]):
            continue
        parts = re.split(r'\s{2,}', line)

        if len(parts) >= 3:
            try:
                item = parts[0]
                qty_match = re.findall(r'\d+', parts[1])
                price_match = re.findall(r'\d+\.?\d*', parts[-1])

                if not qty_match or not price_match:
                    continue

                items.append({
                    "item": item.strip(),
                    "quantity": int(qty_match[0]),
                    "price": float(price_match[0])
                })
                continue
            except Exception:
                pass

        tokens = line.split()
        if len(tokens) < 3:
            continue

        numeric_tokens = []
        for i, t in enumerate(tokens):
            cleaned = t.replace(",", "").replace("$", "").replace("₹", "")
            if re.fullmatch(r'\d+(\.\d+)?', cleaned):
                value = float(cleaned)
                numeric_tokens.append({
                    "index": i,
                    "raw": t,
                    "value": value,
                    "has_decimal": "." in cleaned
                })

        if len(numeric_tokens) < 2:
            continue

        first_num_index = numeric_tokens[0]["index"]
        if first_num_index == 0:
            continue

        item = " ".join(tokens[:first_num_index]).strip()

        qty = None
        lower_tokens = [t.lower() for t in tokens]
        for i, t in enumerate(lower_tokens):
            if t in ("qty", "quantity", "pcs", "pc", "ea"):
                for n in numeric_tokens:
                    if n["index"] > i:
                        qty = n["value"]
                        break
                if qty is not None:
                    break

        if qty is None:
            for t in tokens:
                m = re.fullmatch(r'(\d+)\s*x', t.lower())
                if m:
                    qty = float(m.group(1))
                    break
                m = re.fullmatch(r'x\s*(\d+)', t.lower())
                if m:
                    qty = float(m.group(1))
                    break

        if qty is None:
            small_ints = [n["value"] for n in numeric_tokens if n["value"].is_integer() and 1 <= n["value"] <= 100]
            if small_ints:
                qty = min(small_ints)

        if qty is None:
            qty = numeric_tokens[0]["value"]

        decimal_nums = [n["value"] for n in numeric_tokens if n["has_decimal"]]
        if decimal_nums:
            price = decimal_nums[-1]
        else:
            price = max(n["value"] for n in numeric_tokens)

        try:
            items.append({
                "item": item,
                "quantity": int(round(qty)),
                "price": float(price)
            })
        except Exception:
            continue

    return items


def extract_line_items_loose(text):
    items = []
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if len(line) < 5:
            continue

        lower = line.lower()
        if any(k in lower for k in [
            "description", "qty", "quantity",
            "price", "total", "subtotal",
            "tax", "amount"
        ]):
            continue

        if not re.search(r'[a-zA-Z]', line):
            continue

        numbers = re.findall(r'\d+(?:\.\d+)?', line.replace(",", ""))
        if not numbers:
            continue

        qty = 1
        price = float(numbers[-1])
        if len(numbers) >= 2:
            try:
                qty = int(float(numbers[0]))
            except Exception:
                qty = 1

        item = re.sub(r'\d+(?:\.\d+)?\s*$', '', line).strip(" -|:")
        if not item:
            item = line

        items.append({
            "item": item,
            "quantity": qty,
            "price": price
        })

    return items


def parse_text(text, ocr_results=None):
    text = text.replace("T0TAL", "TOTAL")
    text = text.replace("BALANCE DUE", "Balance Due")
    text = text.replace("AMOUNT DUE", "Amount Due")

    line_items = extract_line_items_from_ocr(ocr_results) if ocr_results else extract_line_items(text)
    if not line_items:
        line_items = extract_line_items(text)
    if not line_items:
        line_items = extract_line_items_loose(text)

    return {
        "merchant_name": extract_merchant_name(text),
        "invoice_number": extract_invoice_number(text),
        "date": extract_date(text),
        "total_amount": extract_total_amount(text),
        "currency": extract_currency(text),
        "line_items": line_items
    }
