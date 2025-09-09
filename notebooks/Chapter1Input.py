

#!pip install ezc3d pandas
#Hossein Mokhtarzadeh PoseiQ.com

import urllib.request, zipfile, os

os.makedirs("sample_data/c3d_zip", exist_ok=True)

url = "https://www.c3d.org/data/Sample01.zip"
zip_path = "sample_data/c3d_zip/sample_data.zip"
urllib.request.urlretrieve(url, zip_path)

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall("sample_data/c3d_zip")

print("Extracted files in c3d_zip:", os.listdir("sample_data/c3d_zip"))
import os, urllib.request, pathlib

base_dir = pathlib.Path("sample_data/online")
base_dir.mkdir(parents=True, exist_ok=True)

# Public example TRC (OpenSim subject01 gait trial)
trc_url = "https://raw.githubusercontent.com/opensim-org/opensim-models/master/Pipelines/Gait2354_Simbody/subject01_walk1.trc"
trc_path = base_dir / "subject01_walk1.trc"

# Public example CSV (OptiTrack export in a robotics dataset)
csv_url = "https://raw.githubusercontent.com/JuSquare/ODA_Dataset/master/dataset/10/optitrack.csv"
csv_path = base_dir / "optitrack.csv"

urllib.request.urlretrieve(trc_url, trc_path.as_posix())
urllib.request.urlretrieve(csv_url, csv_path.as_posix())

print("Downloaded:", trc_path, "and", csv_path)

import ezc3d, glob, os

# Prefer a C3D from the downloaded zip; otherwise try any .c3d in subfolders
c3d_candidates = glob.glob("sample_data/c3d_zip/*.c3d") + glob.glob("sample_data/**/*.c3d", recursive=True)
assert c3d_candidates, "No C3D file found!"
c3d_path = c3d_candidates[0]

c3d = ezc3d.c3d(c3d_path)
points = c3d["data"]["points"]             # shape: 4 x n_markers x n_frames
labels = list(c3d["parameters"]["POINT"]["LABELS"]["value"])

print("Loaded C3D:", c3d_path)
print("Point array shape:", points.shape)
print("Markers (first 8):", labels[:8], "...")


import pandas as pd
import numpy as np
import glob, os

# Only look inside our dedicated 'online' folder to avoid accidental matches in Colab
trc_list = glob.glob("sample_data/online/*.trc")
csv_list = glob.glob("sample_data/online/*.csv")

if trc_list:
    trc_path = trc_list[0]
    # TRC: tab-delimited; first 3 lines are header in many OpenSim examples
    df_trc = pd.read_csv(trc_path, sep="\t", skiprows=3)
    print("Loaded TRC from online folder:", os.path.basename(trc_path))
    display(df_trc.head())

elif csv_list:
    csv_path = csv_list[0]
    df_csv = pd.read_csv(csv_path)
    print("Loaded CSV from online folder:", os.path.basename(csv_path))
    display(df_csv.head())

else:
    # Build DataFrame directly from the C3D markers
    n_markers, n_frames = points.shape[1], points.shape[2]
    xyz = points[:3, :, :].transpose(2, 1, 0)   # frames × markers × (X,Y,Z)

    axes = ["X", "Y", "Z"]
    cols = pd.MultiIndex.from_product([labels, axes], names=["marker", "axis"])

    df_markers = pd.DataFrame(xyz.reshape(n_frames, n_markers*3), columns=cols)
    df_markers.insert(0, "frame", np.arange(n_frames))

    print("No TRC/CSV in online folder - built DataFrame from C3D points.")
    display(df_markers.head())



from urllib.request import urlretrieve

# Replace with any direct .c3d URL you have:
example_c3d_url = "https://example.com/path/to/file.c3d"
local_c3d = "sample_data/online/input_url_file.c3d"

# Uncomment when you have a working URL
# urlretrieve(example_c3d_url, local_c3d)
# c3d_direct = ezc3d.c3d(local_c3d)
# print('Loaded from URL path:', local_c3d)
