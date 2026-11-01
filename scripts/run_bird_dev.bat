@echo off
rem BIRD dev subset, SLM-SQL paper setting (prompt E.1 with evidence, 16 samples, temperature 0.8).
rem Prepare once: scripts\import_bird.py --sample 200 ... --output data\benchmarks\bird_dev200.json (see README).
rem Pause: press Ctrl+C (or close this window), then shut down normally.
rem Resume: run this file again; finished questions are skipped, at most one question is redone.
setlocal
cd /d "%~dp0.."
set "PROJECT_PY=python"
if exist ".venv\Scripts\python.exe" set "PROJECT_PY=.venv\Scripts\python.exe"
set PYTHONIOENCODING=utf-8
"%PROJECT_PY%" -u -m evaluation.run_sweep collect --prompt paper --skip-greedy ^
    --dataset data\benchmarks\bird_dev200.json --pool 16 --batch-size 4 ^
    --output results\bird-dev200-paper
