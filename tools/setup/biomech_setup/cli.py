import argparse, sys, subprocess, tempfile, os, urllib.request, runpy, shutil
from .chapters import CHAPTER_FILES, BASE

def sh(cmd):
    print(f"[run] {cmd}")
    subprocess.check_call(cmd, shell=True)

def ensure_deps():
    # If installed via pip, deps are already satisfied. This is a safety net for notebook users.
    try:
        import pandas  # noqa: F401
        import ezc3d   # noqa: F401
    except Exception:
        sh(f"{sys.executable} -m pip install -q pandas ezc3d")

def fetch(url, dest):
    print(f"[fetch] {url} -> {dest}")
    urllib.request.urlretrieve(url, dest)

def run_file(path):
    print(f"[exec] {os.path.basename(path)}")
    runpy.run_path(path, run_name="__main__")

def resolve_chapters(arg):
    if arg.lower() == "all":
        return list(CHAPTER_FILES.keys())
    return [c.strip() for c in arg.split(",") if c.strip()]

def main():
    p = argparse.ArgumentParser(description="Setup data for BiomechPythonAI book chapters.")
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