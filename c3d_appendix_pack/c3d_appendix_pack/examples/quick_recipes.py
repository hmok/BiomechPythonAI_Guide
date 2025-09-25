from c3d_tools import markers_to_df, analogs_to_df, forceplates_map, catalog

path = "path/to/file.c3d"

df_m = markers_to_df(path)
df_a = analogs_to_df(path)
plates = forceplates_map(path)
info = catalog(path)

print("Markers shape", df_m.shape)
print("Analogs shape", df_a.shape)
print("Force plates", len(plates))
print("Catalog", info)
