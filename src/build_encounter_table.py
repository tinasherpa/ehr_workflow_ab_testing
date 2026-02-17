from __future__ import annotations
import argparse
import pandas as pd

def parse_dt(s):
    return pd.to_datetime(s, utc=True, errors="coerce")

def main(data_dir: str, out_path: str):
    encounters = pd.read_csv(f"{data_dir}/encounters.csv")
    procedures = pd.read_csv(f"{data_dir}/procedures.csv")
    claims = pd.read_csv(f"{data_dir}/claims.csv")
    tx = pd.read_csv(f"{data_dir}/claims_transactions.csv")
    providers = pd.read_csv(f"{data_dir}/providers.csv")
    orgs = pd.read_csv(f"{data_dir}/organizations.csv")

    encounters["start_ts"] = parse_dt(encounters["start"])
    encounters["stop_ts"] = parse_dt(encounters["stop"])
    encounters["duration_min"] = (encounters["stop_ts"] - encounters["start_ts"]).dt.total_seconds() / 60

    proc_counts = (
        procedures.assign(encounter=procedures["encounter"].astype(str))
        .groupby("encounter", as_index=False)
        .size()
        .rename(columns={"size": "procedure_count"})
    )

    tx["appointmentid"] = tx["appointmentid"].astype(str)
    tx["type"] = tx["type"].astype(str)

    charge = (
        tx[tx["type"].str.upper() == "CHARGE"]
        .groupby("appointmentid", as_index=False)["amount"]
        .sum()
        .rename(columns={"appointmentid": "id", "amount": "charge_amount"})
    )

    df = encounters.rename(columns={"id": "encounter_id", "provider": "provider_id", "organization": "organization_id"})
    df = df.merge(proc_counts, left_on="encounter_id", right_on="encounter", how="left").drop(columns=["encounter"])
    df["procedure_count"] = df["procedure_count"].fillna(0).astype(int)

    df = df.merge(charge, left_on="encounter_id", right_on="id", how="left").drop(columns=["id"])
    df["charge_amount"] = pd.to_numeric(df["charge_amount"], errors="coerce")
    df["total_claim_cost"] = pd.to_numeric(df["total_claim_cost"], errors="coerce")
    df["charge_amount"] = df["charge_amount"].fillna(df["total_claim_cost"])

    df = df[df["duration_min"].notna() & (df["duration_min"] >= 0)]

    df.to_parquet(out_path, index=False)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir", default="data")
    ap.add_argument("--out", default="outputs/encounter_level.parquet")
    args = ap.parse_args()
    main(args.data_dir, args.out)