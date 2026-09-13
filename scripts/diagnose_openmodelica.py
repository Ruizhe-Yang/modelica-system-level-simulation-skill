#!/usr/bin/env python3
"""Lightweight staged OpenModelica diagnostic runner.

Runs one or more OMC scripting gates: check -> flatten -> build -> simulate.
It is designed for Codex/agent workflows and emits a compact JSON/text summary.
It does not parse the full OpenModelica backend representation.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


def mo_quote(s: str) -> str:
    return s.replace("\\", "/").replace('"', '\\"')


def result_marked(body: list[str]) -> list[str]:
    return ['print("__RESULT_BEGIN__\\n");', *body, 'print("__RESULT_END__\\n");']


def error_block() -> list[str]:
    return [
        'print("__ERRORS_BEGIN__\\n");',
        'print(getErrorString());',
        'print("\\n__ERRORS_END__\\n");',
    ]


def stage_lines(stage: str, model: str, args) -> list[str]:
    common = (
        f'{model}, startTime={args.start}, stopTime={args.stop}, '
        f'numberOfIntervals={args.intervals}, tolerance={args.tolerance}, '
        f'method="{mo_quote(args.method)}", outputFormat="{mo_quote(args.output_format)}"'
    )
    if stage == "check":
        return [
            f'check__ := checkModel({model});',
            *result_marked(['print(check__);', 'print("\\n");']),
        ]
    if stage == "flatten":
        return [
            f'flat__ := instantiateModel({model});',
            *result_marked([
                'print("flattenLength=");',
                'print(String(stringLength(flat__)));',
                'print("\\n");',
            ]),
        ]
    if stage == "build":
        return [
            f'build__ := buildModel({common});',
            *result_marked([
                'print("executable="); print(build__[1]); print("\\n");',
                'print("initFile="); print(build__[2]); print("\\n");',
            ]),
        ]
    if stage in {"simulate", "profile"}:
        lines = []
        if stage == "profile":
            lines.append('setCommandLineOptions("--profiling=blocks+html");')
        lines.extend([
            f'sim__ := simulate({common});',
            *result_marked([
                'print("resultFile="); print(sim__.resultFile); print("\\n");',
                'print("timeFrontend="); print(String(sim__.timeFrontend)); print("\\n");',
                'print("timeBackend="); print(String(sim__.timeBackend)); print("\\n");',
                'print("timeSimCode="); print(String(sim__.timeSimCode)); print("\\n");',
                'print("timeTemplates="); print(String(sim__.timeTemplates)); print("\\n");',
                'print("timeCompile="); print(String(sim__.timeCompile)); print("\\n");',
                'print("timeSimulation="); print(String(sim__.timeSimulation)); print("\\n");',
                'print("timeTotal="); print(String(sim__.timeTotal)); print("\\n");',
                'print("messages="); print(sim__.messages); print("\\n");',
            ]),
        ])
        return lines
    raise ValueError(stage)


def make_mos(stage: str, args) -> str:
    lines: list[str] = []
    if args.msl_version:
        lines.append(f'print("__LOAD_MSL__=" + String(loadModel(Modelica, {{"{mo_quote(args.msl_version)}"}})) + "\\n");')
    else:
        lines.append('print("__LOAD_MSL__=" + String(loadModel(Modelica)) + "\\n");')
    lines.extend(error_block())
    for load in args.load:
        path = mo_quote(str(Path(load).resolve()))
        lines.append(f'print("__LOAD_FILE__=" + String(loadFile("{path}")) + "\\n");')
        lines.extend(error_block())
    lines.extend(stage_lines(stage, args.model, args))
    lines.extend(error_block())
    return "\n".join(lines) + "\n"


def parse_output(stage: str, stdout: str, stderr: str, returncode: int, elapsed: float) -> dict:
    error_blocks = [x.strip() for x in re.findall(r"__ERRORS_BEGIN__\s*(.*?)\s*__ERRORS_END__", stdout, re.S) if x.strip()]
    m = re.search(r"__RESULT_BEGIN__\s*(.*?)\s*__RESULT_END__", stdout, re.S)
    result_text = m.group(1).strip() if m else None
    combined = "\n".join(error_blocks + ([stderr.strip()] if stderr.strip() else []))
    success = returncode == 0 and not re.search(r"(?:^|\n).*\bError:\s", combined, re.I)

    fields: dict[str, str] = {}
    if result_text:
        for line in result_text.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                fields[k.strip()] = v.strip()

    if stage == "check" and result_text and re.search(r"failed|error", result_text, re.I):
        success = False
    if stage == "flatten" and not fields.get("flattenLength"):
        success = False
    if stage == "build" and not fields.get("executable"):
        success = False
    if stage in {"simulate", "profile"} and not fields.get("resultFile"):
        success = False

    timings = {}
    for k, v in fields.items():
        if k.startswith("time"):
            try:
                timings[k] = float(v)
            except ValueError:
                pass

    return {
        "stage": stage,
        "success": success,
        "returncode": returncode,
        "wall_seconds": elapsed,
        "result_file": fields.get("resultFile") or None,
        "timings": timings,
        "fields": fields,
        "result_excerpt": result_text[:4000] if result_text else None,
        "errors": error_blocks,
        "stderr_excerpt": stderr.strip()[:4000] or None,
    }


def run_stage(stage: str, args, work: Path) -> dict:
    mos = work / f"diagnose_{stage}.mos"
    mos.write_text(make_mos(stage, args), encoding="utf-8")
    t0 = time.monotonic()
    try:
        cp = subprocess.run(
            [args.omc, str(mos)],
            cwd=str(work),
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
        elapsed = time.monotonic() - t0
        r = parse_output(stage, cp.stdout, cp.stderr, cp.returncode, elapsed)
        r["timed_out"] = False
        return r
    except subprocess.TimeoutExpired as e:
        elapsed = time.monotonic() - t0
        out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
        r = parse_output(stage, out, err, 124, elapsed)
        r["success"] = False
        r["timed_out"] = True
        return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="Fully qualified Modelica class name")
    ap.add_argument("--load", action="append", default=[], help="package.mo or .mo file to load; repeatable")
    ap.add_argument("--stage", choices=["check", "flatten", "build", "simulate", "profile", "all"], default="all")
    ap.add_argument("--omc", default="omc")
    ap.add_argument("--msl-version", default="4.0.0")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--stop", type=float, default=1.0)
    ap.add_argument("--intervals", type=int, default=500)
    ap.add_argument("--tolerance", type=float, default=1e-6)
    ap.add_argument("--method", default="ida")
    ap.add_argument("--output-format", default="mat")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--work-dir", default=None)
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if shutil.which(args.omc) is None:
        msg = {"error": f"OpenModelica compiler not found on PATH: {args.omc}"}
        print(json.dumps(msg, ensure_ascii=False) if args.json else msg["error"])
        return 2

    owned_temp = args.work_dir is None
    work = Path(args.work_dir).resolve() if args.work_dir else Path(tempfile.mkdtemp(prefix="modelica_diag_"))
    work.mkdir(parents=True, exist_ok=True)
    stages = [args.stage] if args.stage != "all" else ["check", "flatten", "build", "simulate"]
    results = []
    try:
        for stage in stages:
            r = run_stage(stage, args, work)
            results.append(r)
            if not r["success"]:
                break
        payload = {"model": args.model, "work_dir": str(work), "results": results}
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"OpenModelica diagnosis: {args.model}")
            for r in results:
                status = "PASS" if r["success"] else ("TIMEOUT" if r["timed_out"] else "FAIL")
                print(f"- {r['stage']}: {status} ({r['wall_seconds']:.3f}s)")
                if r["timings"]:
                    print("  timings:", ", ".join(f"{k}={v:g}" for k, v in r["timings"].items()))
                if r["result_file"]:
                    print(f"  result: {r['result_file']}")
                if r["errors"]:
                    print("  diagnostics:")
                    for e in r["errors"]:
                        print("   ", e[:1000].replace("\n", "\n    "))
            if args.keep or not owned_temp:
                print(f"Work directory: {work}")
        return 0 if results and all(r["success"] for r in results) else 1
    finally:
        if owned_temp and not args.keep:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
