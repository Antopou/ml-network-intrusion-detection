
# AI-Based Network Intrusion Detection System (NIDS)

This project is a starter template for a final year cybersecurity project.

## Goal
Build a machine learning system that can detect malicious network traffic.

## Workflow
1. Obtain dataset (CICIDS2017 / NSL-KDD)
2. Preprocess data
3. Train ML model
4. Evaluate performance
5. Build dashboard visualization

## Project structure
```text
data/
	raw/
	processed/
artifacts/
	models/
	logs/
docs/
	guides/
	planning/
src/
```

## Run dashboard
```bash
python3 -m venv .venv
```
```bash
source .venv/bin/activate
```
```bash
python -m pip install -r requirements.txt
```
```bash
streamlit run src/dashboard.py
```

## Run near real-time simulation (defense demo)
```bash
source .venv/bin/activate
python src/simulate_live_traffic.py \
	--csv data/raw/Friday-WorkingHours-Morning.pcap_ISCX.csv \
	--batch-size 500 \
	--sleep 0.7 \
	--max-batches 8 \
	--shuffle
```

Simulation guide:
- `docs/guides/DEFENSE_NON_EXPERT_SIMULATION_GUIDE.md`

Beginner lesson (full project explanation):
- `docs/guides/PROJECT_LESSON_BEGINNER.md`
