import easyocr

reader = easyocr.Reader(['en'], gpu=False)

def extract_text(image):
    results = reader.readtext(image, detail=1)

    grouped_lines = {}
    for box, text, _ in results:
        y_pos = int(box[0][1] // 10)
        grouped_lines.setdefault(y_pos, []).append(text)

    lines = []
    for y in sorted(grouped_lines):
        lines.append(" ".join(grouped_lines[y]))

    return "\n".join(lines)
