"""Write one Kaggle notebook per (benchmark, model) for the comparison with the SLM-SQL paper.

    python scripts/make_paper_notebooks.py        # -> notebooks/paper/*.ipynb

Every notebook samples with evaluation.vllm_collect in the paper setting (prompt E.1,
temperature 0.8, max_new_tokens 1024), splits the questions over the GPUs (shard0/, shard1/) and
zips results/<RUN>/ for download. evaluation.paper_compare builds the table locally.
Run names here must match evaluation/paper_compare.py RUNS.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "paper"

BIRD = {"dataset": "data/benchmarks/bird_dev.json", "kaggle": "slmsql-bird-dev", "label": "BIRD dev (1534 câu)",
        "metric": "set"}
SPIDER = {"dataset": "data/benchmarks/spider_dev.json", "kaggle": "slmsql-spider-dev",
          "label": "Spider dev (1034 câu)", "metric": "spider"}

ROUND2_SEED = 300000  # round-2 samples differ from round 1 (seed 42 + offset + question index)
BIRD_ROUND1 = ("Vòng 1: 64 mẫu/câu với schema đầy đủ (Vote@64 tái lập bài báo). Vòng 2: rút gọn schema theo SQL "
               "của 32 mẫu đầu, sinh thêm 32 mẫu. Phương pháp mới = 32 mẫu đầu vòng 1 + 32 mẫu vòng 2 = 64 mẫu, "
               "bằng ngân sách của bài báo.")

# notebook file name -> (benchmark, title, paper note, jobs [(RUN, MODEL, POOL, SEED_OFFSET, ROUND2)], hours)
# ROUND2 = samples of the pruned-schema round (<RUN>-prune<ROUND2>), schema kept from the first ROUND2 samples.
NOTEBOOKS = {
    "bird-dev_SLM-SQL-0.5B_64mau_2vong": (
        BIRD, "BIRD dev · SLM-SQL-0.5B (Qwen2.5-Coder-0.5B, SFT + RL) · 64 mẫu + vòng 2",
        "Bài báo Bảng 2: **56.87** (64 mẫu + CSC). " + BIRD_ROUND1 + " **Vòng 1 đã chạy xong**: *Add Input* output "
        "version cũ của notebook BIRD 0.5B để bỏ qua vòng 1 (chỉ chép lại pool), chỉ còn vòng 2 (khoảng 2–3 giờ).",
        [("bird-dev-0.5b-rl", "cycloneboy/SLM-SQL-0.5B", 64, 0, 32)], "6–8 giờ (chỉ vòng 2: 2–3 giờ)"),
    "bird-dev_SLM-SQL-0.6B_64mau_2vong": (
        BIRD, "BIRD dev · SLM-SQL-0.6B (Qwen3-0.6B, SFT + RL) · 64 mẫu + vòng 2",
        "Bài báo Bảng 2: **59.52** (64 mẫu + CSC). " + BIRD_ROUND1,
        [("bird-dev-0.6b-rl", "cycloneboy/SLM-SQL-0.6B", 64, 0, 32)], "15–17 giờ, 2 version (vòng 1 đo thật: ~11 giờ)"),
    "bird-dev_SLM-SQL-Base-1B_64mau_2vong": (
        BIRD, "BIRD dev · SLM-SQL-Base-1B (Llama-3.2-1B, SFT) · 64 mẫu + vòng 2",
        "Bài báo Bảng 2: **54.78** (SLM-SQL-1B, SFT + RL, 64 mẫu + CSC). Tác giả **chưa công bố** bản SFT + RL "
        "của Llama (`cycloneboy/SLM-SQL-1B` không tồn tại), nên notebook chạy bản SFT `SLM-SQL-Base-1B`: "
        "kết quả dự kiến thấp hơn số của bài báo. " + BIRD_ROUND1,
        [("bird-dev-1b-sft", "cycloneboy/SLM-SQL-Base-1B", 64, 0, 32)], "7–10 giờ"),
    "bird-dev_SLM-SQL-1.3B_64mau_2vong": (
        BIRD, "BIRD dev · SLM-SQL-1.3B (deepseek-coder-1.3b, SFT + RL) · 64 mẫu + vòng 2",
        "Bài báo Bảng 2: **62.19** (64 mẫu + CSC). " + BIRD_ROUND1 + " Không dùng lại pool cũ `results/bird-dev-slm13`: "
        "nó được sinh trước bản sửa KV-cache của `vllm_collect` nên 30% mẫu không có SQL (vote 39.4). Model 1.3B "
        "có 16 KV head nên chậm: **khoảng 24–36 giờ**, tức 3 version (xem phần *Chạy tiếp*). Muốn tiết kiệm "
        "quota: đổi số mẫu vòng 1 thành 32 (mất cột Vote@64/CAV-3@64, vẫn có phương pháp mới).",
        [("bird-dev-1.3b-rl", "cycloneboy/SLM-SQL-1.3B", 64, 0, 32)], "24–36 giờ (3 version)"),
}
SPIDER_FAMILIES = [
    ("0.5B", "Qwen2.5-Coder-0.5B-Instruct", "0.5b", "Qwen/Qwen2.5-Coder-0.5B-Instruct", "cycloneboy/SLM-SQL-Base-0.5B",
     "cycloneboy/SLM-SQL-0.5B", "42.13 / 65.31 / 70.60", "2–3 giờ"),
    ("0.6B", "Qwen3-0.6B", "0.6b", "Qwen/Qwen3-0.6B", "cycloneboy/SLM-SQL-Base-0.6B", "cycloneboy/SLM-SQL-0.6B",
     "63.19 / 68.02 / 72.05", "3–5 giờ"),
    ("1B", "Llama-3.2-1B-Instruct", "1b", "unsloth/Llama-3.2-1B-Instruct", "cycloneboy/SLM-SQL-Base-1B", None,
     "30.79 / 63.77 / 67.63", "2–3 giờ"),
    ("1.3B", "deepseek-coder-1.3b-instruct", "1.3b", "deepseek-ai/deepseek-coder-1.3b-instruct",
     "cycloneboy/SLM-SQL-Base-1.3B", "cycloneboy/SLM-SQL-1.3B", "48.23 / 72.86 / 75.47", "6–9 giờ"),
    ("1.5B", "Qwen2.5-Coder-1.5B-Instruct", "1.5b", "Qwen/Qwen2.5-Coder-1.5B-Instruct",
     "cycloneboy/SLM-SQL-Base-1.5B", "cycloneboy/SLM-SQL-1.5B", "63.54 / 74.53 / 75.15", "3–5 giờ"),
]
for size, base_name, slug, base, sft, rl, paper, hours in SPIDER_FAMILIES:
    jobs = ([(f"spider-dev-{slug}-rl", rl, 16, 0, 8)] if rl else []) + [
        (f"spider-dev-{slug}-sft", sft, 16, 0, 8), (f"spider-dev-{slug}-base", base, 16, 0, 8)]
    note = (f"Bài báo Bảng 3, Spider **Dev EX, cột SC** (base / SFT / SFT + RL): **{paper}**. "
            "Chạy lần lượt " + ", ".join(f"`{m}`" for _, m, *_ in jobs) + ". Mỗi model: vòng 1 = 16 mẫu/câu với "
            "schema đầy đủ (Vote@16 tái lập cột SC), vòng 2 = 8 mẫu với schema rút gọn theo SQL của 8 mẫu đầu. "
            "Phương pháp mới = 8 mẫu đầu vòng 1 + 8 mẫu vòng 2 = 16 mẫu, bằng ngân sách SC của bài báo.")
    if slug == "1b":
        note += (" Bản SFT + RL của Llama (67.63) **chưa được tác giả công bố**, nên bỏ qua. Model gốc lấy từ "
                 "`unsloth/` (bản sao không cần xin quyền của `meta-llama/Llama-3.2-1B-Instruct`).")
    if slug == "0.6b":
        note += (" Qwen3-0.6B gốc mặc định *thinking*; với `max_new_tokens` 1024 như bài báo, một phần mẫu có thể "
                 "bị cắt trước khi ra SQL (đếm ở dòng `samples without SQL` của log).")
    NOTEBOOKS[f"spider-dev_{size}-{base_name}_base-sft-rl_2vong"] = (
        SPIDER, f"Spider dev · {base_name}: base / SFT / SFT + RL · 16 mẫu + vòng 2", note, jobs, hours)


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.strip("\n").splitlines(keepends=True)}


INSTALL = '''
import glob, os, shutil, subprocess, sys, time
VENV = "/tmp/vllm-env"
PY = f"{VENV}/bin/python"


def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-3000:], r.stderr[-3000:])
        raise RuntimeError(f"Lỗi khi chạy: {cmd}")


if not os.path.exists(PY):
    sh(f"{sys.executable} -m pip install -q uv")
    sh(f"{sys.executable} -m uv venv -q --python 3.12 {VENV}")
    sh(f'{sys.executable} -m uv pip install -q --python {PY} --exclude-newer 2025-05-15 '
       '"vllm==0.8.5.post1" "sqlglot==26.16.4" "PyYAML==6.0.2"')
r = subprocess.run([PY, "-c", "import sys, vllm; print('python', sys.version.split()[0], '| vllm', vllm.__version__)"],
                   capture_output=True, text=True)
print(r.stdout, r.stderr[-3000:])
assert r.returncode == 0, "Không import được vllm trong venv"
'''

COPY = '''
# Chỉ lấy bản code có database thật và có file dataset của notebook này
# (output của version trước, nếu được Add Input, cũng chứa một bản code).
src = [os.path.dirname(p) for p in glob.glob("/kaggle/input/**/adaptive-slm-sql/config.yaml", recursive=True)
       if os.path.isfile(os.path.join(os.path.dirname(p), DATASET))
       and os.path.isdir(os.path.join(os.path.dirname(p), "data", "external"))
       and not os.path.islink(os.path.join(os.path.dirname(p), "data", "external"))]
if not src:
    found = sorted(glob.glob("/kaggle/input/**/adaptive-slm-sql/data/benchmarks/*.json", recursive=True))
    raise SystemExit(f"Notebook {NOTEBOOK} cần {DATASET} (dataset {KAGGLE_DATASET}), nhưng /kaggle/input chỉ có:\\n  "
                     + ("\\n  ".join(found) or "(không có adaptive-slm-sql nào)")
                     + f"\\n→ Add Input dataset {KAGGLE_DATASET}, hoặc mở đúng notebook cho dataset đang có.")
src = src[0]
work = "/tmp/adaptive-slm-sql"  # ngoài /kaggle/working để Output chỉ có kết quả
if not os.path.exists(work):
    shutil.copytree(src, work, ignore=shutil.ignore_patterns("external"))
    shutil.copytree(os.path.join(src, "data", "external"), "/tmp/external")
    os.symlink("/tmp/external", os.path.join(work, "data", "external"))
os.chdir(work)
if not os.path.exists("evaluation/paper_compare.py"):
    print("Cảnh báo: dataset là bản code cũ (thiếu evaluation/paper_compare.py), cell kiểm tra EX sẽ lỗi; "
          "đóng gói lại zip theo hướng dẫn.")
print("Code:", src)
GPUS = len(subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout.strip().splitlines())
print("Số GPU:", GPUS)
'''

RUN = '''
def run_job(run, model, pool, seed_offset, keep=None):
    output = f"/kaggle/working/results/{run}"
    os.makedirs(output, exist_ok=True)
    procs = []
    for shard in range(GPUS):
        out = f"{output}/shard{shard}"
        previous = glob.glob(f"/kaggle/input/**/results/{run}/shard{shard}/pool.jsonl", recursive=True)
        if previous and not os.path.exists(f"{out}/pool.jsonl"):
            os.makedirs(out, exist_ok=True)
            shutil.copy(previous[0], f"{out}/pool.jsonl")
            print("Chạy tiếp từ", previous[0])
        cmd = [PY, "-u", "-m", "evaluation.vllm_collect", "--dataset", DATASET, "--output", out,
               "--pool", str(pool), "--chunk", "32", "--dtype", "half", "--seed-offset", str(seed_offset),
               "--shard", f"{shard}/{GPUS}", "--model", model]
        if keep:
            cmd += ["--keep-schema", keep]
        if LIMIT:
            cmd += ["--limit", str(LIMIT)]
        env = dict(os.environ, VLLM_USE_V1="0", CUDA_VISIBLE_DEVICES=str(shard))
        log = f"{output}/shard{shard}.log"
        with open(log, "a") as handle:
            procs.append((shard, log, subprocess.Popen(cmd, stdout=handle, stderr=subprocess.STDOUT, env=env)))
    seen = [0] * GPUS
    while True:
        running = any(proc.poll() is None for _, _, proc in procs)
        for shard, log, _ in procs:
            with open(log, encoding="utf-8", errors="replace") as handle:
                lines = handle.readlines()
            for line in lines[seen[shard]:]:
                if not line.startswith(("INFO", "WARNING", "Capturing", "Loading", "(")) or "Error" in line:
                    print(f"[{run} GPU {shard}]", line, end="")
            seen[shard] = len(lines)
        if not running:
            break
        if time.time() - START > STOP_AFTER_HOURS * 3600:
            # Stop before Kaggle's 12-hour kill so the zip cell still runs; every finished chunk is already on disk.
            print(f"Đã quá {STOP_AFTER_HOURS} giờ: dừng sinh mẫu, chạy tiếp ở version sau.", flush=True)
            for _, _, proc in procs:
                proc.terminate()
            for _, _, proc in procs:
                proc.wait()
            return False
        time.sleep(60)
    for shard, _, proc in procs:
        print(f"{run} GPU {shard}: exit code", proc.returncode)
    return all(proc.returncode == 0 for _, _, proc in procs)


def make_keep(run, samples):
    """Schema for round 2: tables/columns used by the first `samples` executable SQL of round 1 (no gold)."""
    rows = [line for path in sorted(glob.glob(f"/kaggle/working/results/{run}/shard*/pool.jsonl"))
            for line in open(path, encoding="utf-8") if line.strip()]
    pool = f"/tmp/{run}-round1.jsonl"
    with open(pool, "w", encoding="utf-8") as handle:
        handle.writelines(rows)
    keep = f"/kaggle/working/results/{run}-prune{samples}/keep.json"
    os.makedirs(os.path.dirname(keep), exist_ok=True)
    r = subprocess.run([PY, "-m", "evaluation.schema_keep", pool, DATASET, "--samples", str(samples),
                        "--output", keep], capture_output=True, text=True)
    print(r.stdout, r.stderr[-3000:])
    assert r.returncode == 0, "schema_keep lỗi"
    return keep


for run, model, pool, seed_offset, round2 in JOBS:
    print(f"=== {run}: {model}, vòng 1, {pool} mẫu/câu, schema đầy đủ ===", flush=True)
    done = run_job(run, model, pool, seed_offset)
    # Round 2's schema needs every question of round 1: never start it from a partial round 1.
    if done and round2:
        keep = make_keep(run, round2)
        print(f"=== {run}-prune{round2}: vòng 2, {round2} mẫu/câu, schema rút gọn ===", flush=True)
        done = run_job(f"{run}-prune{round2}", model, round2, ROUND2_SEED, keep)
    print(f"Đã chạy {(time.time() - START) / 3600:.1f} giờ", flush=True)
    if not done:
        print("CHƯA XONG: tải zip hoặc Add Input output của version này rồi Save & Run All lại để chạy tiếp.")
        break
'''

CHECK = '''
runs = " ".join(job[0] for job in JOBS)
!cd /tmp/adaptive-slm-sql && {PY} -m evaluation.paper_compare --results /kaggle/working/results --runs {runs} --output /tmp/paper-compare
'''

ZIP = '''
os.chdir("/kaggle/working")
with open("README.txt", "w", encoding="utf-8") as handle:
    handle.write(f"Notebook: {NOTEBOOK}\\nDataset: {DATASET}\\nRuns: " + ", ".join(f"{r} (+ vòng 2 {r}-prune{k}) = {m}" for r, m, _, _, k in JOBS) + "\\n")
import zipfile
archive = f"/kaggle/working/{NOTEBOOK}.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
    z.write("README.txt")
    for run, *_, round2 in JOBS:
        for path in sorted(glob.glob(f"results/{run}/**/*", recursive=True)
                           + glob.glob(f"results/{run}-prune{round2}/**/*", recursive=True)):
            if os.path.isfile(path):
                z.write(path)
from IPython.display import FileLink
print(archive, f"{os.path.getsize(archive) / 2 ** 20:.0f} MB")
FileLink(os.path.basename(archive))
'''


def notebook(name, bench, title, note, jobs, hours):
    jobs_src = "\n".join(f'    ("{r}", "{m}", {p}, {s}, {k}),' for r, m, p, s, k in jobs)
    intro = f"""
# {title}

{note}

| | |
|---|---|
| Tập dữ liệu | {bench['label']}, metric `{bench['metric']}` |
| Kaggle dataset cần *Add Input* | **`{bench['kaggle']}`** (từ `dist/{bench['kaggle']}.zip`) |
| Thiết lập | prompt Appendix E.1, temperature 0.8, top-p 1.0, `max_new_tokens` 1024, vLLM FP16 |
| Thời gian ước tính (T4 x2) | {hours} |
| File kết quả (tab *Output*) | **`{name}.zip`** → giải nén vào thư mục project |

**Cách chạy:**
1. *Settings*: **Accelerator = GPU T4 x2**, **Internet = On**. *Add Input* → dataset `{bench['kaggle']}`.
2. Chạy thử: đặt `LIMIT = 20` ở cell cấu hình, *Run All*, kiểm tra bảng EX cuối notebook.
3. Chạy thật: `LIMIT = None`, **Save Version → Save & Run All** (chạy nền tối đa 12 giờ, tắt máy được).
4. Tải `{name}.zip` ở tab *Output* của version đó.

**Chạy tiếp khi hết 12 giờ:** *Add Input* → *Notebooks* → chọn chính notebook này (output version trước), rồi *Save & Run All* lại. Cell sinh mẫu tự chép `pool.jsonl` cũ và chỉ sinh các câu còn thiếu.
"""
    config = f'''
import time
NOTEBOOK = "{name}"
KAGGLE_DATASET = "{bench['kaggle']}"
DATASET = "{bench['dataset']}"
ROUND2_SEED = {ROUND2_SEED}
JOBS = [  # (results/<RUN>, model Hugging Face, số mẫu vòng 1, seed offset, số mẫu vòng 2 với schema rút gọn)
{jobs_src}
]
LIMIT = None  # 20 để chạy thử nhanh
STOP_AFTER_HOURS = 11.3  # Kaggle dừng phiên ở 12 giờ; dừng sớm để kịp nén kết quả
START = time.time()
'''
    cells = [
        md(intro),
        code("!nvidia-smi --query-gpu=name,memory.total --format=csv"),
        md("## Cấu hình"),
        code(config),
        md("Cài vLLM 0.8.5 vào venv Python 3.12 riêng (3–5 phút; image Kaggle dùng Python 3.13 mà vLLM 0.8.5 "
           "chỉ hỗ trợ < 3.13). T4 không có bfloat16 nên dùng float16."),
        code(INSTALL),
        md("Chép code và database sang `/tmp` (ổ ghi được: database ở chế độ WAL không mở được trên "
           "`/kaggle/input`)."),
        code(COPY),
        md("## Sinh mẫu\n\nMỗi GPU một nửa số câu (`shard0/`, `shard1/`). Tiến độ in mỗi phút; log đầy đủ ở "
           "`results/<RUN>/shard*.log`."),
        code(RUN),
        md("## EX tạm tính so với bài báo\n\nVote@16/@64 = bỏ phiếu trên 16/64 mẫu đầu; Oracle = có ít nhất 1 mẫu "
           "đúng. Số chính thức tính lại ở máy local bằng `evaluation.paper_compare`."),
        code(CHECK),
        md("## Nén kết quả\n\nGiải nén zip vào thư mục project (giữ nguyên `results/<RUN>/shard*/`, không lồng "
           "`results/results/`)."),
        code(ZIP),
    ]
    return {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                                         "name": "python3"},
                                          "language_info": {"name": "python"}},
            "nbformat": 4, "nbformat_minor": 5}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, spec in NOTEBOOKS.items():
        path = OUT / f"{name}.ipynb"
        path.write_text(json.dumps(notebook(name, *spec), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
