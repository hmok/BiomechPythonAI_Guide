

#!pip install ezc3d pandas
#Hossein Mokhtarzadeh PoseiQ.com this is for Chapter 2 onward
import numpy as np
import ezc3d, glob, os
c3d = ezc3d.c3d('/content/sample_data/c3d_zip/Eb015pi.c3d') #c3d = ezc3d.c3d(c3d_path) 
# Sampling rate of the motion-capture system (frames per second)
point_rate = float(c3d["parameters"]["POINT"]["RATE"]["value"][0])

# Total number of frames in the file
n_frames = int(c3d["data"]["points"].shape[2])

# Quick sanity check: make sure both values are valid
assert point_rate > 0 and n_frames > 0

# Create a time vector: [0, 1/point_rate, 2/point_rate, ...]
time = np.arange(n_frames, dtype=float) / point_rate

# Quick check: show first few values
print("Frame rate (Hz):", point_rate)
print("Number of frames:", n_frames)
print("First 5 time stamps (s):", time[:5])

# Notes
# If your file has dropped frames or a non-zero start time in metadata, this approach is safer: it builds the time vector directly from the frame count.
# The time vector is now ready to align with markers and force data in later steps.
# Step 2 • Extract Marker Positions
# Prompt: Run this cell to extract a single marker (e.g., heel) from the motion-capture file.
import pandas as pd

# Marker labels from the file
marker_labels = list(c3d["parameters"]["POINT"]["LABELS"]["value"])

# Choose the target marker (example: right heel "RFT3")
target_label = "RFT3"   # change this to match your dataset

if target_label in marker_labels:
    heel_idx = marker_labels.index(target_label)
else:
    print(f"Warning: {target_label} not found. Using first marker:", marker_labels[0])
    heel_idx = 0
    target_label = marker_labels[0]

# Extract XYZ position (mm) for chosen marker
heel_mm = c3d["data"]["points"][:3, heel_idx, :].T
df_markers_mm = pd.DataFrame(heel_mm, columns=["Heel_X_mm", "Heel_Y_mm", "Heel_Z_mm"])

print("Marker extracted:", target_label)
print(df_markers_mm.head())

# Notes
# Marker names differ across labs. Run print(marker_labels[:12]) to preview common names.
# Keep units in mm for now; we’ll normalize later.
# Step 3 • Extract Force Plate Vertical Force
# Prompt
# Run this cell to extract vertical ground reaction force (Fz) from the force plate.
analog_labels = list(c3d["parameters"]["ANALOG"]["LABELS"]["value"])
wanted = "FZ1"   # typical vertical force label

if wanted in analog_labels:
    fz_idx = analog_labels.index(wanted)
    analog = c3d["data"]["analogs"]      # shape: subframes × channels × frames
    fz_per_frame = analog[:, fz_idx, :].mean(axis=0)  # average across subframes
else:
    print(f"Warning: {wanted} not found. Available:", analog_labels[:10], "...")
    fz_per_frame = np.full(n_frames, np.nan, dtype=float)

print("Vertical force length:", len(fz_per_frame))
print("First 5 values:", fz_per_frame[:5])

# Notes
# Don’t flatten subframes directly. Averaging per frame keeps force data aligned with marker frames.
# If subframe detail is important (e.g., event detection), resample instead of averaging.
# Step 4 • Normalize Units
# Prompt
# Run this cell to convert units: markers from mm → m, force from N → body weight.
g = 9.81
body_mass_kg = 80.0   # replace with subject's mass if known

# Convert markers to meters
df_markers_m = df_markers_mm.copy() / 1000.0
df_markers_m.columns = ["Heel_X", "Heel_Y", "Heel_Z"]

# Normalize vertical force to body weight
fz_bw = fz_per_frame / (body_mass_kg * g)

print("Heel marker (m):")
print(df_markers_m.head())
print("Vertical force (BW): first 5 =", fz_bw[:5])

# Notes
# If subject mass is unknown, keep values in Newtons and note the unit.
# Storing constants like g and body_mass_kg in one place makes updates easier.
# Step 5 • Filter Noise
# Prompt
# Run this cell to apply a low-pass Butterworth filter to smooth the marker trajectory.
from scipy.signal import butter, filtfilt

cutoff_hz = 6.0   # common cutoff for gait markers
nyq = point_rate / 2.0
b, a = butter(4, cutoff_hz / nyq, btype="low")

heel_filt = filtfilt(b, a, df_markers_m[["Heel_X", "Heel_Y", "Heel_Z"]].values, axis=0)
df_markers_filt = pd.DataFrame(heel_filt, columns=["Heel_X", "Heel_Y", "Heel_Z"])

print("Filtered heel positions:")
print(df_markers_filt.head())

# Notes
# Typical cutoffs: markers 4–8 Hz, forces 15–25 Hz.
# Avoid filtering across NaN gaps — fill missing data first if needed.
# Step 6 • Assemble a Tidy Table
# Prompt
# Run this cell to combine time, heel marker, and vertical force into one DataFrame.
def ensure_same_length(*arrays):
    L = min(len(a) for a in arrays)
    return [np.asarray(a)[:L] for a in arrays], L

(arrs, L) = ensure_same_length(
    time,
    df_markers_filt["Heel_X"].values,
    df_markers_filt["Heel_Y"].values,
    df_markers_filt["Heel_Z"].values,
    fz_bw
)
time_a, hx_a, hy_a, hz_a, fz_a = arrs
print("Using aligned length:", L)

df = pd.DataFrame({
    "Time": time_a,
    "Heel_X": hx_a,
    "Heel_Y": hy_a,
    "Heel_Z": hz_a,
    "Fz_BW": fz_a
})

df.head()

