from scripts.cded_inventory import (
    classify_record, parse_header, parse_sha256sums, subject_id, summarize_csv,
)


def test_sha256sums_paths_keep_spaces():
    text = "abc123  Data_Description/GE-79_Files_and Channels.csv\ndef456 *RECORDS\n"
    assert parse_sha256sums(text) == ["Data_Description/GE-79_Files_and Channels.csv", "RECORDS"]


def test_record_classification_and_subject_ids():
    assert classify_record("Data/S0250/s0250DB-v2") == "labview_visit2"
    assert classify_record("Data/S0250/s0250DB-v8") == "labview_visit8"
    assert classify_record("Data/S0250/s0250ECG") == "ecg_24h"
    assert subject_id("Data/S0250/s0250DB-v8") == "0250"


def test_header_parse_reads_only_structure():
    text = "s0250DB-v2 3 500 300000\nf.dat 16 200 16 0 0 0 0 ECG\nf.dat 16 1 16 0 0 0 0 Finger BP\nf.dat 16 1 16 0 0 0 0 Resp belt\n"
    h = parse_header(text)
    assert h["fs"] == 500.0 and h["n_samples"] == 300000
    assert h["channels"] == ["ECG", "Finger BP", "Resp belt"]


def test_csv_summary_counts_without_values():
    out = summarize_csv("id,Valsalva ratio,HR_supine\n1,1.3,\n2,NA,60\n3,1.1,62\n")
    cols = {c["name"]: c["nonmissing"] for c in out["columns"]}
    assert out["rows"] == 3 and cols == {"id": 3, "Valsalva ratio": 2, "HR_supine": 2}


def test_marker_run_lengths_collapse_levels():
    from scripts.cded_segments import run_lengths
    fs = 10.0
    trace = [0] * 50 + [1] * 30 + [0] * 3 + [2] * 40
    runs = run_lengths(trace, fs, min_seconds=0.5)
    assert [r[0] for r in runs] == [0.0, 1.0, 2.0]
    assert runs[1][1] == 5.0 and runs[1][2] == 3.0
