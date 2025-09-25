import numpy as np
import pandas as pd

def _ensure_c3d_mapping(obj):
    """
    Accepts:
      - str or Path to .c3d
      - ezc3d.c3d mapping (dict-like)
      - plain dict shaped like ezc3d output
    Returns a mapping with ['header','parameters','data'].
    """
    if isinstance(obj, dict) or (hasattr(obj, "keys") and hasattr(obj, "__getitem__")):
        return obj
    try:
        from pathlib import Path
        is_pathish = isinstance(obj, (str, Path))
    except Exception:
        is_pathish = isinstance(obj, str)
    if is_pathish:
        import ezc3d
        return ezc3d.c3d(str(obj))  # already a mapping
    raise TypeError("Give me a .c3d path or the ezc3d mapping.")

def get_param(c3d_like, group, name, default=None):
    c3d = _ensure_c3d_mapping(c3d_like)
    try:
        val = c3d["parameters"][group][name]["value"]
        if isinstance(val, (list, tuple)) and val and isinstance(val[0], bytes):
            val = [v.decode("utf-8", errors="ignore") for v in val]
        return val
    except Exception:
        return default

def _labels_sanitized(labels):
    if not labels:
        return []
    out = []
    for x in labels:
        out.append(x.decode("utf-8", "ignore") if isinstance(x, bytes) else str(x))
    return out

def catalog(c3d_like):
    c3d = _ensure_c3d_mapping(c3d_like)
    P = c3d["data"].get("points", np.zeros((4, 0, 0)))
    A = c3d["data"].get("analogs", np.zeros((1, 0, 0)))
    if A.ndim == 2:
        A = A[np.newaxis, :, :]
    return {
        "point_labels": _labels_sanitized(get_param(c3d, "POINT", "LABELS", [])),
        "analog_labels": _labels_sanitized(get_param(c3d, "ANALOG", "LABELS", [])),
        "point_units": get_param(c3d, "POINT", "UNITS", []),
        "analog_units": get_param(c3d, "ANALOG", "UNITS", []),
        "point_rate": get_param(c3d, "POINT", "RATE", [c3d["header"]["points"].get("frame_rate")])[0],
        "analog_rate": get_param(c3d, "ANALOG", "RATE", [c3d["header"]["analogs"].get("frame_rate")])[0],
        "points_shape": tuple(P.shape),
        "analogs_shape": tuple(A.shape),
        "force_platform_keys": list(c3d["parameters"].get("FORCE_PLATFORM", {}).keys()),
    }

def markers_to_df(c3d_like, start_frame=0, end_frame=None):
    c3d = _ensure_c3d_mapping(c3d_like)
    P = c3d["data"]["points"]  # [4, N, T]
    if P.ndim != 3 or P.shape[0] < 3:
        raise ValueError(f"Unexpected points shape {P.shape}. Expected [4, n_points, n_frames].")
    labels = _labels_sanitized(get_param(c3d, "POINT", "LABELS", []))
    n_points, n_frames = P.shape[1], P.shape[2]
    j_end = n_frames if end_frame is None else min(end_frame, n_frames)
    if start_frame < 0 or start_frame >= j_end:
        raise ValueError("start_frame out of range")
    xyz = P[0:3, :, start_frame:j_end]            # [3, N, F]
    frames = np.arange(start_frame, j_end)
    n_use = min(n_points, len(labels)) if labels else n_points
    if labels and len(labels) != n_points:
        print(f"Note: point labels {len(labels)} vs points {n_points}. Using first {n_use}.")
    cols, chunks = [], []
    for j in range(n_use):
        name = labels[j] if labels else f"pt{j:03d}"
        cols += [f"{name}_X", f"{name}_Y", f"{name}_Z"]
        chunks.append(xyz[:, j, :].T)             # [F, 3]
    wide = np.concatenate(chunks, axis=1) if chunks else np.empty((len(frames), 0))
    df = pd.DataFrame(wide, columns=cols, index=frames)
    df.index.name = "frame"
    return df

def analogs_to_df(c3d_like, start_sample=0, end_sample=None):
    c3d = _ensure_c3d_mapping(c3d_like)
    A = c3d["data"]["analogs"]          # expected [1, C, T]
    if A.ndim == 2:                     # tolerate [C, T]
        A = A[np.newaxis, :, :]
    if A.ndim != 3 or A.shape[0] != 1:
        raise ValueError(f"Unexpected analogs shape {A.shape}. Expected [1, n_channels, n_samples].")
    _, n_ch, n = A.shape
    i_end = n if end_sample is None else min(end_sample, n)
    if start_sample < 0 or start_sample >= i_end:
        raise ValueError("start_sample out of range")
    labels = _labels_sanitized(get_param(c3d, "ANALOG", "LABELS", []))
    if labels and len(labels) != n_ch:
        print(f"Note: analog labels {len(labels)} vs channels {n_ch}. Truncating to match.")
        labels = labels[:n_ch]
    if not labels:
        labels = [f"ch{idx:03d}" for idx in range(n_ch)]
    data_tc = np.moveaxis(A[:, :, start_sample:i_end], 2, 1)[0]  # [T, C]
    df = pd.DataFrame(data_tc, columns=labels)
    df.index.name = "sample"
    return df

def forceplates_map(c3d_like):
    c3d = _ensure_c3d_mapping(c3d_like)
    fp = c3d["parameters"].get("FORCE_PLATFORM", {})
    if not fp:
        return []
    def take(key, default):
        return fp.get(key, {}).get("value", default)
    types = take("TYPE", [])
    channels = take("CHANNEL", [])
    corners = take("CORNERS", [])
    origin = take("ORIGIN", [])
    cal = take("CAL_MATRIX", [])
    return [{
        "index": k,
        "type": types[k] if k < len(types) else None,
        "channels": channels[k] if k < len(channels) else [],
        "corners": corners[k*12:(k+1)*12],
        "origin":  origin[k*3:(k+1)*3],
        "cal_matrix": cal[k*36:(k+1)*36],
    } for k in range(len(types))]

def grf_cop_from_plate(analog_df, plate, force_scale=1.0, moment_scale=1.0, threshold=20.0):
    idx = [i-1 if isinstance(i, (int, np.integer)) and i > 0 else i for i in plate.get("channels", [])]
    if len(idx) < 6:
        raise ValueError("Need at least 6 channels for Fx Fy Fz Mx My Mz")
    Fx, Fy, Fz, Mx, My, Mz = analog_df.iloc[:, idx[:6]].to_numpy().T
    F = np.vstack([Fx, Fy, Fz]).T * force_scale
    M = np.vstack([Mx, My, Mz]).T * moment_scale
    Fz_safe = np.where(np.abs(F[:, 2]) < threshold, np.nan, F[:, 2])
    cop_x = -My / Fz_safe
    cop_y =  Mx / Fz_safe
    cop = np.vstack([cop_x, cop_y, np.zeros_like(cop_x)]).T
    return F, M, cop
