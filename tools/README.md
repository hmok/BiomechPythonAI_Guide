# biomech-setup

Tiny helper so notebooks can fetch and run the chapter prep scripts.

## Install in a notebook
```python
%pip -q install "git+https://github.com/hmok/BiomechPythonAI_Guide@main#subdirectory=tools/setup"


!biomech-setup --chapters 1,2
# or
!biomech-setup --chapters all


### tools/setup/biomech_setup/__init__.py
```python
# Minimal package init for biomech_setup
