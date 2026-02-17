import numpy as np

def bootstrap_mean_diff(a, b, n_boot=5000, seed=7):
    rng = np.random.default_rng(seed)
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    diffs = []
    for _ in range(n_boot):
        sa = rng.choice(a, size=len(a), replace=True)
        sb = rng.choice(b, size=len(b), replace=True)
        diffs.append(sb.mean() - sa.mean())
    diffs = np.array(diffs)
    return {
        "diff": float(diffs.mean()),
        "ci_lo": float(np.quantile(diffs, 0.025)),
        "ci_hi": float(np.quantile(diffs, 0.975)),
    }