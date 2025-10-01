# biomech-setup

Minimal helper so notebooks can fetch and run chapter input scripts.

## Install in a notebook
```
%pip -q install "git+https://github.com/hmok/BiomechPythonAI_Guide@main#subdirectory=tools/setup"
```

## Use
```
!biomech-setup --chapters 1,2
# or
!biomech-setup --chapters all
```

## Add more chapters
Edit `biomech_setup/chapters.py` and extend `CHAPTER_FILES` with the new mapping.