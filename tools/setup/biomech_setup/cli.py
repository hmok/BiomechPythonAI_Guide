import argparse, sys, subprocess, tempfile, os, urllib.request, runpy, shutil
from .chapters import CHAPTER_FILES, BASE

def sh(cmd: str):
    print(f"[run] {cmd}")
    subprocess.check_call(cmd, shell=True)

def ensure_deps():
    # Safety net for notebook users. If installed via pip, deps should already be present.
    try:
        import pandas  # noqa: F401
        import ezc3d   # noqa: F401
    except Exception:
        sh(f"{sys.executable} -m pip install -q pandas ezc3d")

# Provide display/HTML/Markdown/clear_output in case we're not inside a notebook
try:
    from IPython.display import display, HTML, Markdown, clear_output  # type: ignore
except Exception:
    def display(*args, **kwargs):  # no-op fallback
        pass
    def HTML(_):  # type: ignore
        return None
    def Markdown(_):  # type: ignore
        return None
    def clear_output(*args, **kwargs):  # type: ignore
        pass

def fetch(url: str, dest: str):
    print(f"[fetch] {url} -> {dest}")
    urllib.request.urlretrieve(url, dest)

def run_file(path: str):
    # Inject notebook-y globals so chapter scripts don’t blow up
    g = {
        "__name__": "__main__",
        "display": display,
        "HTML": HTML,
        "Markdown": Markdown,
        "clear_output": clear_output,
    }
    print(f"[exec] {os.path.basename(path)}")
    runpy.run_path(path, init_globals=g)

def resolve_chapters(arg: str):
    if arg.lower() == "all":
        return list(CHAPTER_FILES.keys())
    return [c.strip() for c in arg.split(",") if c.strip()]

def main():
    p = argparse.ArgumentParser(description="Setup data/code for BiomechPythonAI book chapters.")
    p.add_argument("--chapters", default="1,2", help="Comma list like '1,2' or 'all'")
    args = p.parse_args()

    ensure_deps()

    chapters = resolve_chapters(args.chapters)
    unknown = [c for c in chapters if c not in CHAPTER_FILES]
    if unknown:
        sys.exit(f"Unknown chapters: {unknown}. Known: {sorted(CHAPTER_FILES)}")

    tmpdir = tempfile.mkdtemp(prefix="biomech_setup_")
    try:
        local_files = []
        for c in chapters:
            fname = CHAPTER_FILES[c]
            dest = os.path.join(tmpdir, fname)
            fetch(BASE + fname, dest)
            local_files.append(dest)

        for f in local_files:
            run_file(f)

        print("[ok] Finished")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

if __name__ == "__main__":
    main()
