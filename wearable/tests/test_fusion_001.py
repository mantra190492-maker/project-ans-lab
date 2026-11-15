import numpy as np

from wearable.experiments import fusion_001 as f


def _cohort(n=60, seed=0, redundant=False):
    rng = np.random.default_rng(seed)
    y = (np.arange(n) % 2).astype(int)
    age = rng.normal(65, 6, n)
    sex = (rng.random(n) < 0.5).astype(float)
    a = rng.normal(0, 1, n) - 0.9 * y
    b = (a + rng.normal(0, 0.05, n)) if redundant else (rng.normal(0, 1, n) - 0.9 * y)
    return a, b, rng.normal(0, 1, n), age, sex, y


def test_auc_matches_known_values():
    assert f.auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == 1.0
    assert f.auc([0, 1, 0, 1], [0.1, 0.2, 0.8, 0.9]) == 0.75
    assert f.auc([0, 0, 1, 1], [1, 1, 1, 1]) == 0.5


def test_leave_one_out_prediction_ignores_the_held_out_label():
    a, b, h, age, sex, y = _cohort(40)
    X = np.column_stack([age, sex, a, b])
    p1 = f.loo_predictions(X, y)
    y2 = y.copy(); y2[7] = 1 - y2[7]
    assert abs(f.loo_predictions(X, y2)[7] - p1[7]) < 1e-9


def test_independent_domains_add_but_redundant_ones_do_not(monkeypatch):
    monkeypatch.setattr(f, "N_BOOT", 300)
    gains = [f.analyse(*_cohort(120, seed=s))["fusion_gain_auc"] for s in range(4)]
    redundant = [f.analyse(*_cohort(120, seed=s, redundant=True))["fusion_gain_auc"] for s in range(4)]
    assert np.mean(gains) > 0.03 and np.mean(redundant) < 0.02
    assert not f.analyse(*_cohort(120, seed=1, redundant=True))["fusion_adds"]


def test_table_loader_requires_all_columns_and_checks_units():
    head = "SUBJECT NUMBER,Gender,Age,Group,VM RATIO,HR TILT BASELINE,TILT AVE,SBP TILT BASELINE1,TILT AVE1\n"
    rows = "".join(f"S{i:04d},{'M' if i % 2 else 'F'},{60 + i % 9},{'CONTROL' if i % 3 else 'DM'},1.{3 + i % 5},{60 + i % 7},{70 + i % 7},{120 + i % 9},{112 + i % 9}\n" for i in range(12))
    a, flow = f.load(head + rows + "S9999,M,60,DM,,60,70,120,110\n")
    assert flow == {"table_rows": 13, "missing_any_required": 1, "analysed": 12}
    assert set(np.unique(a[:, 5])) == {0.0, 1.0} and np.allclose(a[:, 1], -8)
    swapped = head + "".join(f"S{i:04d},M,60,DM,1.4,120,110,60,70\n" for i in range(6))
    try:
        f.load(swapped.replace(",M,", ",F,", 1))
        raise AssertionError("unit check should fail")
    except ValueError:
        pass
