"""Zip the code, BIRD dataset JSONs and SQLite databases for upload as a private Kaggle Dataset.

Kaggle extracts the zip; notebooks/kaggle_vllm_bird.ipynb finds `adaptive-slm-sql/` under
/kaggle/input and runs evaluation.vllm_collect there. Dataset paths are rewritten with forward
slashes (Windows-written JSON uses backslashes, which Linux reads as part of the file name).

    python scripts/pack_kaggle.py --dataset data/benchmarks/bird_dev.json data/benchmarks/bird_dev200.json
"""
import argparse
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CODE = ["core", "evaluation", "databases", "scripts", "config.yaml", "pyproject.toml", "requirements.txt",
        "requirements-model.txt"]


def _files(path: Path):
    if path.is_file():
        yield path
    else:
        yield from (p for p in sorted(path.rglob("*")) if p.is_file() and "__pycache__" not in p.parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset", type=Path, nargs="+", required=True, help="Dataset JSONs (import_bird output)")
    parser.add_argument("--extra", type=Path, nargs="*", default=[], help="More project files, e.g. the merge pairs")
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "adaptive-slm-sql-kaggle.zip")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    needed = {}  # archive name -> source file
    for name in CODE:
        for path in _files(ROOT / name):
            needed[path.relative_to(ROOT).as_posix()] = path
    for path in args.extra:
        needed[path.resolve().relative_to(ROOT).as_posix()] = path.resolve()
    datasets = {}
    for dataset in args.dataset:
        dataset = dataset.resolve()
        items = json.loads(dataset.read_text(encoding="utf-8"))
        for item in items:
            for key in ("db_path", "tables_path"):
                if item.get(key):
                    item[key] = item[key].replace("\\", "/")
                    source = (dataset.parent / item[key]).resolve()
                    if not source.is_file():
                        sys.exit(f"Missing {source} (from {dataset.name})")
                    needed[source.relative_to(ROOT).as_posix()] = source
        datasets[dataset.relative_to(ROOT).as_posix()] = json.dumps(items, ensure_ascii=False, indent=2)
    size = sum(p.stat().st_size for p in needed.values())
    print(f"{len(needed)} files, {size / 2 ** 30:.2f} GB before compression -> {args.output}", flush=True)
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, source in sorted(needed.items()):
            archive.write(source, f"adaptive-slm-sql/{name}")
        for name, text in datasets.items():
            archive.writestr(f"adaptive-slm-sql/{name}", text)
    print(f"Done: {args.output.stat().st_size / 2 ** 20:.0f} MB", flush=True)


if __name__ == "__main__":
    main()
