import easyocr

_READER = None

def _get_reader():
    global _READER
    if _READER is None:
        _READER = easyocr.Reader(['en'], gpu=False)
    return _READER

def _group_results_into_lines(results, conf_threshold=0.0):
    if not results:
        return []

    heights = []
    for bbox, _, _ in results:
        ys = [pt[1] for pt in bbox]
        heights.append(max(ys) - min(ys))
    median_height = sorted(heights)[len(heights) // 2] if heights else 10
    bucket = max(5, int(median_height * 0.6))

    lines = {}
    for bbox, text, conf in results:
        if conf < conf_threshold:
            continue
        xs = [pt[0] for pt in bbox]
        ys = [pt[1] for pt in bbox]
        y_center = (min(ys) + max(ys)) / 2.0
        x_center = (min(xs) + max(xs)) / 2.0
        y_bucket = int(y_center // bucket)
        lines.setdefault(y_bucket, []).append((x_center, text, bbox, conf))

    grouped = []
    for y in sorted(lines.keys()):
        grouped.append(sorted(lines[y], key=lambda item: item[0]))
    return grouped


def extract_text_with_boxes(image, conf_threshold=0.0):
    if image is None:
        return "", []
    try:
        if image.size == 0:
            return "", []
    except Exception:
        return "", []

    try:
        results = _get_reader().readtext(image, detail=1)
    except Exception:
        return "", []

    if not results:
        return "", []

    lines = _group_results_into_lines(results, conf_threshold=conf_threshold)
    text_lines = []
    for line in lines:
        text_lines.append(" ".join([w[1] for w in line]))

    return "\n".join(text_lines), results


def extract_text(image, conf_threshold=0.0):
    if image is None:
        return ""
    try:
        if image.size == 0:
            return ""
    except Exception:
        return ""

    try:
        results = _get_reader().readtext(image, detail=1)
    except Exception:
        return ""

    if not results:
        return ""

    lines = _group_results_into_lines(results, conf_threshold=conf_threshold)
    final_lines = []
    for line in lines:
        final_lines.append(" ".join([w[1] for w in line]))

    return "\n".join(final_lines)
