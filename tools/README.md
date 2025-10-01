# biomech-setup

Tiny helper so notebooks can fetch and run the chapter prep scripts that live in
https://github.com/hmok/BiomechPythonAI_Guide/tree/main/notebooks

## Install in a notebook
```python
%pip -q install "git+https://github.com/hmok/BiomechPythonAI_Guide@main#subdirectory=tools/setup"

**# Use**
!biomech-setup --chapters 1,2
# or
!biomech-setup --chapters all

**Add more chapters**

### tools/setup/biomech_setup/__init__.py
```python
# Minimal package init for biomech_setup

