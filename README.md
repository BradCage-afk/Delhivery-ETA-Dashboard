# Delhivery — Graph-Based ETA Intelligence (Dashboard)

Interactive Streamlit dashboard for a graph-based delivery-ETA project: the logistics
network modelled as a directed graph of 1,657 facilities and 2,783 corridors, used to
predict more accurate ETAs than the OSRM routing engine.

**Live views:** Overview · interactive Network Map (pan/zoom/hover) · Bottleneck Hubs ·
Corridors · ETA Predictor · Route-Type Recommender · Strategy Memo.

## Run locally
```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

## Deploy (Streamlit Community Cloud)
1. Push this repo to GitHub.
2. Go to share.streamlit.io → Create app → pick this repo.
3. Set **Main file path** = `dashboard/app.py` → Deploy.

This is the runtime-only bundle: it ships the trained model and pre-computed result
tables/figures, so it needs no training step and no GPU/torch at deploy time.
