# Costa author-vs-Python HRF differential gate

Generated UTC: 2026-11-15T15:30:08.192411+00:00
Source SHA256: `aec918325b8ca12074db99370e4429c6e6588016df350af39ca7d11d45e1c1a7`

**Reference equivalence on three author fixtures: PASS**

| Official fixture | Reference PIP (IP/NN) | Python PIP (IP/NN) | All six counts equal? |
|---|---:|---:|---|
| timeseries_1PVC.txt | 33/53 | 33/53 | PASS |
| timeseries_1PVC_1outlier.txt | 31/50 | 31/50 | PASS |
| timeseries_1PVC_2outliers.txt | 30/46 | 30/46 | PASS |

## Exact official and independent counts

### timeseries_1PVC.txt

~~~json
{
  "official": {
    "IP": 33,
    "eligible_NN": 53,
    "short": 24,
    "accelerative_decelerative": 43,
    "long": 19,
    "delta_NN": 51
  },
  "python": {
    "IP": 33,
    "eligible_NN": 53,
    "short": 24,
    "accelerative_decelerative": 43,
    "long": 19,
    "delta_NN": 51
  }
}
~~~

### timeseries_1PVC_1outlier.txt

~~~json
{
  "official": {
    "IP": 31,
    "eligible_NN": 50,
    "short": 21,
    "accelerative_decelerative": 40,
    "long": 19,
    "delta_NN": 47
  },
  "python": {
    "IP": 31,
    "eligible_NN": 50,
    "short": 21,
    "accelerative_decelerative": 40,
    "long": 19,
    "delta_NN": 47
  }
}
~~~

### timeseries_1PVC_2outliers.txt

~~~json
{
  "official": {
    "IP": 30,
    "eligible_NN": 46,
    "short": 21,
    "accelerative_decelerative": 36,
    "long": 15,
    "delta_NN": 43
  },
  "python": {
    "IP": 30,
    "eligible_NN": 46,
    "short": 21,
    "accelerative_decelerative": 36,
    "long": 15,
    "delta_NN": 43
  }
}
~~~

## Interpretation

- These fixtures test author-coded PIP, PNNSS, PNNLS (including ectopy and outliers).
- Official program source is downloaded and hashed at runtime. The author GPL code is not imported into our module.
- Even a perfect match on three fixtures is **limited analytical equivalence**, not clinical validation.
- Need additional withheld synthetic sequences testing sample-grid drift, zeros, atrial/ventricular ectopy, missed beats and long noisy recordings.
- **No SHHS/MrOS controlled data were accessed or uploaded.**
