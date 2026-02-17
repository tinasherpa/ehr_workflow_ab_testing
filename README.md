# A/B Testing Workflow Efficiency + Cost Impact (Synthetic EHR)

## Goal
Simulate and analyze a product-style A/B experiment to evaluate whether workflow improvements
reduce encounter time and downstream cost while maintaining operational guardrails.

## Data
Synthetic EHR-style tables:
- encounters.csv
- procedures.csv
- claims.csv
- claims_transactions.csv
- providers.csv
- organizations.csv


## Primary Metrics
- Encounter duration (minutes): stop - start
- Downstream cost proxy: sum of CHARGE line items per encounter (fallback to total_claim_cost)

## Guardrails
- Procedure count stability
- Variance in duration and cost

## Experiment Design
- Reproducible 50/50 assignment using a stable hash of encounter_id
- Simulated workflow improvement:
  - Higher complexity encounters (more procedures) receive larger expected time savings
  - Small cost savings modeled to reflect reduced rework

## How to Run
1. Install dependencies:
   pip install -r requirements.txt
2. Build encounter-level table:
   python -m src.build_encounter_table --data_dir data --out outputs/encounter_level.parquet
3. Run experiment:
   python -m src.simulate_experiment --in outputs/encounter_level.parquet --out outputs/ab_results.json
