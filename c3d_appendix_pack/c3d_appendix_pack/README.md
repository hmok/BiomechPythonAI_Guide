# C3D Appendix Pack

Self contained bundle for working with C3D files using ezc3d, plus diagrams and an appendix section.

## Contents
- `c3d_tools.py` reusable helpers
- `examples/quick_recipes.py` short usage
- `appendix/APPENDIX_C3D.md` appendix ready text with mermaid blocks
- `diagrams/c3d_mindmap.mmd` mermaid mind map
- `diagrams/c3d_flow.mmd` mermaid flow
- `requirements.txt` minimal dependencies
- `.gitignore` basic Python ignores

## Install
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Use
```python
from c3d_tools import markers_to_df, analogs_to_df, forceplates_map

df_m = markers_to_df("path/to/file.c3d")
df_a = analogs_to_df("path/to/file.c3d")
plates = forceplates_map("path/to/file.c3d")
```

## Diagrams
The mermaid `.mmd` files render on GitHub. If you want PNGs, use any mermaid CLI or an online renderer.

## License
MIT for the code in this pack.
