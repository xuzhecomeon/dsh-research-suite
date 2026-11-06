#!/usr/bin/env python3
"""Data loader: JSON, CSV, TSV with intelligent format detection."""
import json, csv, os


def _is_number(s):
    """Check if string represents a number."""
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def load_data(path, chart_type=None):
    """
    Load data from JSON or CSV/TSV.

    Returns a dict appropriate for the chart type:
    - bar/line: {"labels": [], "series": {}, "errors": {}}
    - scatter: {"x": [], "y": [], "groups": []}
    - heatmap: {"matrix": [[]], "row_labels": [], "col_labels": []}
    - box/violin: {"labels": [], "series": {}}
    - forest: {"labels": [], "estimates": [], "ci_low": [], "ci_high": []}
    - pie: {"labels": [], "values": []}
    - radar: {"labels": [], "series": {}}
    - histogram: {"series": {}} or {"values": []}
    - 3d: {"x": [], "y": [], "z": []} or {"matrix": [[]]}
    - subplots: list of individual chart data dicts
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return _validate_and_convert(data, chart_type)
    elif ext in ('.csv', '.tsv'):
        return _load_tabular(path, ext, chart_type)
    else:
        raise ValueError(f"Unsupported format: {ext}. Use .json, .csv, or .tsv")


def _normalize_series_list(series):
    """Convert list-of-objects series to dict format.

    Handles: [{"name": "A", "values": [1,2], "errors": [0.1,0.2]}, ...]
      -> ({"A": [1,2]}, {"A": [0.1,0.2]})
    Also accepts: [{"label": "A", "data": [1,2]}, ...]
    """
    if not isinstance(series, list):
        return series, {}
    result = {}
    errors = {}
    for item in series:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("label") or item.get("key", f"Series {len(result)+1}")
        values = item.get("values") or item.get("data") or item.get("y") or item.get("value", [])
        if isinstance(values, list) and values:
            result[name] = values
        err = item.get("errors") or item.get("error") or item.get("std") or item.get("sem")
        if err is not None:
            errors[name] = err
    return result if result else series, errors if errors else {}


def _validate_and_convert(data, chart_type):
    """Validate JSON data against chart type and fill missing fields."""
    if not isinstance(data, dict):
        return data  # Could be a list for subplots

    # Check for common alternate keys and normalize
    key_map = {
        "x": ["x", "xs", "x_data", "x_values"],
        "y": ["y", "ys", "y_data", "y_values"],
        "z": ["z", "zs", "z_data", "z_values"],
        "labels": ["labels", "label", "categories", "names", "x_labels"],
        "series": ["series", "datasets", "data", "groups"],
        "matrix": ["matrix", "data", "grid", "array"],
        "estimates": ["estimates", "effects", "or", "rr", "hr"],
        "ci_low": ["ci_low", "lower", "ci_lower", "lo"],
        "ci_high": ["ci_high", "upper", "ci_upper", "hi"],
        "errors": ["errors", "error", "std", "sem"],
        "row_labels": ["row_labels", "y_labels", "rows", "y_ticks"],
        "col_labels": ["col_labels", "x_labels", "cols", "x_ticks", "columns"],
        "groups": ["groups", "group", "categories", "category", "color_by"],
    }

    normalized = {}
    for canonical, aliases in key_map.items():
        for alias in aliases:
            if alias in data:
                normalized[canonical] = data[alias]
                break

    # Keep any keys not in the alias map
    for k, v in data.items():
        found = False
        for aliases in key_map.values():
            if k in aliases:
                found = True
                break
        if not found:
            normalized[k] = v

    # Convert list-of-objects series to dict format
    if "series" in normalized and isinstance(normalized["series"], list):
        series_dict, embedded_errors = _normalize_series_list(normalized["series"])
        normalized["series"] = series_dict
        if embedded_errors and "errors" not in normalized:
            normalized["errors"] = embedded_errors
        # Also normalize errors if they are in list-of-objects format
        if "errors" in normalized and isinstance(normalized["errors"], list):
            errs, _ = _normalize_series_list(normalized["errors"])
            if errs:
                normalized["errors"] = errs

    return normalized


def _load_tabular(path, ext, chart_type):
    """Load CSV/TSV and auto-detect structure."""
    delimiter = '\t' if ext == '.tsv' else ','
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=delimiter)
        headers = next(reader)
        rows = list(reader)

    if not rows:
        return {"labels": [], "series": {}}

    # Identify numeric columns (>50% numeric threshold)
    numeric_col_indices = []
    for i, h in enumerate(headers):
        if i == 0:
            continue
        num_count = sum(1 for r in rows if i < len(r) and _is_number(r[i]))
        if num_count > len(rows) * 0.5:
            numeric_col_indices.append(i)

    # Filter bad rows (non-numeric in numeric columns)
    bad_rows = set()
    for i in numeric_col_indices:
        for ri, r in enumerate(rows):
            if ri < len(r) and not _is_number(r[i]):
                bad_rows.add(ri)

    good_rows = [ri for ri in range(len(rows)) if ri not in bad_rows]

    # Build series
    series = {}
    for i in numeric_col_indices:
        vals = [float(rows[ri][i]) for ri in good_rows if ri < len(rows)]
        if vals:
            series[headers[i]] = vals

    labels = [rows[ri][0] for ri in good_rows if ri < len(rows)]

    # --- Chart-specific conversions ---
    if chart_type in ('scatter',) and series:
        return _convert_to_scatter(headers, rows, good_rows, numeric_col_indices)

    if chart_type in ('box', 'boxplot', 'violin') and series:
        return _convert_to_grouped(headers, rows, good_rows, labels, numeric_col_indices)

    if chart_type in ('heatmap',) and series:
        matrix = list(series.values())
        return {
            "matrix": matrix,
            "row_labels": list(series.keys()),
            "col_labels": labels,
        }

    if chart_type in ('pie',) and series:
        first_key = list(series.keys())[0]
        return {"labels": labels, "values": series[first_key]}

    if chart_type in ('histogram',) and series:
        first_key = list(series.keys())
        if len(first_key) == 1:
            return {"values": series[first_key[0]], "name": first_key[0]}
        return {"series": series}

    if chart_type in ('radar',):
        return {"labels": labels, "series": series}

    # Default: bar/line format
    return {"labels": labels, "series": series}


def _convert_to_scatter(headers, rows, good_rows, numeric_col_indices):
    """Convert tabular data to scatter format."""
    all_numeric = []
    for i, h in enumerate(headers):
        num_count = sum(1 for ri in good_rows if ri < len(rows) and _is_number(rows[ri][i]))
        if num_count > len(good_rows) * 0.5:
            all_numeric.append((i, h))

    if len(all_numeric) < 2:
        col_i, col_name = all_numeric[0]
        y_vals = [float(rows[ri][col_i]) for ri in good_rows if ri < len(rows)]
        labels = [rows[ri][0] for ri in good_rows]
        if labels and all(_is_number(l) for l in labels):
            return {"x": [float(l) for l in labels], "y": y_vals}
        return {"x": list(range(len(y_vals))), "y": y_vals}

    col_i, col_x_name = all_numeric[0]
    col_j, col_y_name = all_numeric[1]
    x_vals = [float(rows[ri][col_i]) for ri in good_rows if ri < len(rows) and col_i < len(rows[ri])]
    y_vals = [float(rows[ri][col_j]) for ri in good_rows if ri < len(rows) and col_j < len(rows[ri])]

    # Try to find grouping column
    groups = None
    _group_hints = {'group', 'groups', 'category', 'categories', 'class', 'label', 'type'}
    candidates = []
    for i, h in enumerate(headers):
        if i in [idx for idx, _ in all_numeric]:
            continue
        vals = [rows[ri][i] for ri in good_rows if ri < len(rows)]
        unique = set(vals)
        if 1 < len(unique) <= 20:
            score = (0, len(unique), i)
            if h.lower().strip() in _group_hints:
                score = (-1, len(unique), i)
            candidates.append((score, vals, h))

    if candidates:
        candidates.sort()
        groups = candidates[0][1]

    result = {"x": x_vals, "y": y_vals}
    if groups:
        result["groups"] = groups
    return result


def _convert_to_grouped(headers, rows, good_rows, labels, numeric_col_indices):
    """Convert tabular to box/violin (grouped long-format) format."""
    first_col_vals = [rows[ri][0] for ri in good_rows if ri < len(rows)]
    unique_groups = list(dict.fromkeys(first_col_vals))

    if len(unique_groups) < len(first_col_vals) * 0.8 and len(unique_groups) >= 2:
        num_col_idx = numeric_col_indices[0] if numeric_col_indices else None
        if num_col_idx is not None:
            grouped = {g: [] for g in unique_groups}
            for ri in good_rows:
                if ri < len(rows) and num_col_idx < len(rows[ri]):
                    g = rows[ri][0]
                    v = rows[ri][num_col_idx]
                    if _is_number(v):
                        grouped[g].append(float(v))
            if any(len(v) >= 2 for v in grouped.values()):
                return {"labels": unique_groups, "series": grouped}

    # Fallback: wide format
    series = {}
    for i in numeric_col_indices:
        vals = [float(rows[ri][i]) for ri in good_rows if ri < len(rows)]
        if vals:
            series[headers[i]] = vals
    return {"labels": labels if labels else list(series.keys()), "series": series}
