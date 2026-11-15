"""Compare independent beat-level Python HRF against original Costa AWK.

Public official fixtures ONLY; never process private SHHS/MrOS data in CI.
The reference AWK is downloaded to the runner and its SHA checked.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

from anslab.hrf_costa_reference import costa_fragmentation_from_peaks

EXPECTED_AWK_SHA256="aec918325b8ca12074db99370e4429c6e6588016df350af39ca7d11d45e1c1a7"
OFFICIAL={
  "timeseries_1PVC.txt":(33,53,24,43,19,51),
  "timeseries_1PVC_1outlier.txt":(31,50,21,40,19,47),
  "timeseries_1PVC_2outliers.txt":(30,46,21,36,15,43)
}
TRIPLES=("pip","pnnss","pnnls")


def read_beats(path):
    rows=[line.split() for line in Path(path).read_text().splitlines() if line.strip()]
    return [float(row[0]) for row in rows],[int(row[1]) for row in rows]


def parse_author_output(output):
    def pair(key):
        found=re.search(rf"\b{key}\s*=\s*(\d+)/(\d+)",output)
        if not found:
            raise ValueError(f"Cannot parse {key}: {output}")
        return int(found.group(1)),int(found.group(2))
    return tuple(x for name in ("PIP","PNNSS","PNNLS") for x in pair(name))


def analyze(folder):
    root=Path(folder)
    src=root/"HRF.awk"
    digest=hashlib.sha256(src.read_bytes()).hexdigest()
    if digest != EXPECTED_AWK_SHA256:
        raise ValueError("Unexpected author AWK checksum; do NOT evaluate against unverified source")
    results=[]
    for filename,expected in OFFICIAL.items():
        raw=(root/filename).read_bytes()
        original=subprocess.run(["awk","-f",str(src)],input=raw,
                                capture_output=True,check=True,text=False)
        actual=parse_author_output(original.stdout.decode())
        peaks,labels=read_beats(root/filename)
        output=costa_fragmentation_from_peaks(peaks,labels)
        observed=(output["n_inflection_points"],output["n_author_eligible_nn"],
                  output["n_short_delta_nn"], output["n_short_delta_nn"]+output["n_long_delta_nn"],
                  output["n_long_delta_nn"],output["n_counted_delta_nn"])
        results.append({
            "fixture":filename,
            "author_fraction_counts":dict(zip(("IP","eligible_NN","short","accelerative_decelerative","long","delta_NN"),actual)),
            "python_fraction_counts":dict(zip(("IP","eligible_NN","short","accelerative_decelerative","long","delta_NN"),observed)),
            "python_percentages":{k:output[k] for k in ("pip_percent","pnnss_percent","pnnls_percent")},
            "author_stdout":original.stdout.decode().strip(),
            "match_author":observed==actual,
            "match_published_technical_table":actual==expected,
            "fixture_sha256":hashlib.sha256(raw).hexdigest(),
        })
    return {"created_utc":datetime.now(timezone.utc).isoformat(),
            "reference":"Costa PhysioNet HRF.awk v1.0.0",
            "author_awk_sha256":digest,
            "all_match_author":all(r["match_author"] for r in results),
            "results":results,
            "limitations":"Public synthetic/reference examples only; long-term clinical performance and ECG annotation correctness unverified."}


def write_report(payload):
    out=Path("reports");out.mkdir(parents=True,exist_ok=True)
    (out/"HRF_DIFFERENTIAL_TEST.json").write_text(json.dumps(payload,indent=2)+"\n")
    lines=["# Costa author-vs-Python HRF differential gate","",
           f"Generated UTC: {payload['created_utc']}",
           f"Source SHA256: `{payload['author_awk_sha256']}`",
           "",
           f"**Reference equivalence on three author fixtures: {'PASS' if payload['all_match_author'] else 'FAIL'}**",
           "",
           "| Official fixture | Reference PIP (IP/NN) | Python PIP (IP/NN) | All six counts equal? |",
           "|---|---:|---:|---|"]
    for result in payload["results"]:
        a=result["author_fraction_counts"];b=result["python_fraction_counts"]
        lines.append(f"| {result['fixture']} | {a['IP']}/{a['eligible_NN']} | {b['IP']}/{b['eligible_NN']} | {'PASS' if result['match_author'] else '**FAIL**'} |")
    lines+=["","## Exact official and independent counts",""]
    for result in payload["results"]:
        lines+= [f"### {result['fixture']}","",
                  "~~~json",json.dumps({"official":result["author_fraction_counts"],
                                        "python":result["python_fraction_counts"]},indent=2),
                  "~~~",""]
    lines += [
        "## Interpretation","",
        "- These fixtures test author-coded PIP, PNNSS, PNNLS (including ectopy and outliers).",
        "- Official program source is downloaded and hashed at runtime. The author GPL code is not imported into our module.",
        "- Even a perfect match on three fixtures is **limited analytical equivalence**, not clinical validation.",
        "- Need additional withheld synthetic sequences testing sample-grid drift, zeros, atrial/ventricular ectopy, missed beats and long noisy recordings.",
        "- **No SHHS/MrOS controlled data were accessed or uploaded.**",
        ""]
    (out/"HRF_DIFFERENTIAL_TEST.md").write_text("\n".join(lines),encoding="utf-8")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--reference-dir",default="/tmp/costa-reference")
    p.add_argument("--fail-on-mismatch",action="store_true")
    args=p.parse_args()
    result=analyze(args.reference_dir)
    write_report(result)
    print(json.dumps(result,indent=2))
    if args.fail_on_mismatch and not result["all_match_author"]:
        raise SystemExit("FAIL: Python candidate differs from original Costa AWK")


if __name__=="__main__":
    main()
