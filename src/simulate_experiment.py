import argparse, hashlib, json
import numpy as np
import pandas as pd
from .stats import bootstrap_mean_diff

def assign_group(encounter_id):
    h = hashlib.md5(encounter_id.encode()).hexdigest()
    return "treatment" if int(h[:8], 16) % 2 == 0 else "control"

def main(inp, out):
    df = pd.read_parquet(inp)
    df["group"] = df["encounter_id"].astype(str).map(assign_group)

    pc = df["procedure_count"].to_numpy(float)
    time_savings = np.clip(0.04 + 0.01 * np.log1p(pc), 0, 0.12)
    cost_savings = np.clip(0.01 + 0.005 * np.log1p(pc), 0, 0.05)

    df["duration_cf"] = df["duration_min"]
    df["charge_cf"] = df["charge_amount"]

    t = df["group"] == "treatment"
    df.loc[t, "duration_cf"] *= (1 - time_savings[t])
    df.loc[t, "charge_cf"] *= (1 - cost_savings[t])

    res = {
        "duration": bootstrap_mean_diff(
            df[df.group=="control"].duration_cf.values,
            df[df.group=="treatment"].duration_cf.values,
        ),
        "cost": bootstrap_mean_diff(
            df[df.group=="control"].charge_cf.values,
            df[df.group=="treatment"].charge_cf.values,
        ),
    }

    with open(out, "w") as f:
        json.dump(res, f, indent=2)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="outputs/encounter_level.parquet")
    ap.add_argument("--out", dest="out", default="outputs/ab_results.json")
    args = ap.parse_args()
    main(args.inp, args.out)
