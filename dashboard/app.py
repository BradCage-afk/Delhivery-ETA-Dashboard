"""Delhivery Graph-ETA — operations dashboard (optional Deliverable 6).

Run:  streamlit run dashboard/app.py

UI: light "analytics" design — bright canvas, white cards with soft shadows, indigo
accent, top-tab navigation, native interactive charts (Altair). Data-forward.
"""
import streamlit as st
import pandas as pd, numpy as np, json, os, joblib
import altair as alt
import pydeck as pdk

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def p(*a): return os.path.join(ROOT, *a)

# palette
BG, CARD, INK, MUTED, LINE = "#f7f8fa", "#ffffff", "#0f172a", "#64748b", "#e8ebf0"
INDIGO, GREEN, AMBER, RED = "#4f46e5", "#059669", "#d97706", "#e11d48"

st.set_page_config(page_title="Delhivery Graph-ETA", layout="wide", page_icon="📦")

# ============================ THEME — light analytics ============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root{--bg:#f7f8fa;--card:#fff;--ink:#0f172a;--muted:#64748b;--line:#e8ebf0;
  --indigo:#4f46e5;--green:#059669;--amber:#d97706;--red:#e11d48;--sans:'Inter',system-ui,sans-serif;}
.stApp{background:var(--bg);color:var(--ink);font-family:var(--sans);}
[data-testid="stHeader"]{background:transparent;}
.block-container{max-width:1180px;padding-top:2rem;padding-bottom:5rem;}
h1,h2,h3,h4{font-family:var(--sans)!important;color:var(--ink)!important;letter-spacing:-0.02em;}
p,span,div,label,li{color:var(--ink);}
a,a:visited{color:var(--indigo)!important;text-decoration:none;}

/* fix: restore Material icon font (broken by an earlier global font override) */
[data-testid="stIconMaterial"],span.material-symbols-rounded,span.material-symbols-outlined,
[class*="material-symbols"]{font-family:'Material Symbols Rounded','Material Symbols Outlined','Material Icons'!important;}

/* hero */
.hero{padding:4px 0 18px;position:relative;}
.hero::after{content:"";position:absolute;right:-4%;top:-90px;width:460px;height:280px;pointer-events:none;z-index:0;
  background:radial-gradient(ellipse at center,rgba(79,70,229,0.10),rgba(79,70,229,0.03) 45%,transparent 70%);}
.hero>*{position:relative;z-index:1;}
.hero .eb{font-size:12px;font-weight:600;letter-spacing:0.12em;color:var(--indigo);text-transform:uppercase;}
.hero h1{font-size:42px;line-height:1.08;letter-spacing:-0.03em;font-weight:600;color:var(--ink);margin:12px 0 10px;}
.hero .sub{color:var(--muted);font-size:17px;max-width:700px;line-height:1.5;}
.hero .sub b{color:var(--ink);font-weight:600;}

/* top tabs */
[data-baseweb="tab-list"]{gap:10px;border-bottom:1px solid var(--line);margin-bottom:6px;}
button[data-baseweb="tab"]{font-family:var(--sans);font-size:15px;color:var(--muted);padding:10px 6px;}
button[data-baseweb="tab"][aria-selected="true"]{color:var(--ink);font-weight:600;}
[data-baseweb="tab-highlight"]{background:var(--indigo)!important;height:2px;}
[data-baseweb="tab-border"]{background:transparent;}

/* section header */
.sec{margin:38px 0 16px;}
.sec .eb{font-size:12px;font-weight:600;letter-spacing:0.1em;color:var(--indigo);text-transform:uppercase;}
.sec h2{font-size:26px!important;font-weight:600!important;letter-spacing:-0.02em;color:var(--ink)!important;margin:7px 0 5px;}
.sec .sec-d{color:var(--muted);font-size:15px;max-width:760px;line-height:1.5;}

/* KPI cards */
.kpi{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px 22px;
  box-shadow:0 1px 2px rgba(16,24,40,0.04),0 6px 16px -8px rgba(16,24,40,0.10);min-height:120px;}
.kpi-l{font-size:12px;font-weight:500;letter-spacing:0.05em;color:var(--muted);text-transform:uppercase;}
.kpi-v{font-size:34px;font-weight:600;letter-spacing:-0.03em;color:var(--ink);margin-top:12px;line-height:1;}
.kpi-d{font-size:13px;font-weight:500;margin-top:9px;}
.kpi-d.pos{color:var(--green);} .kpi-d.neg{color:var(--red);} .kpi-d.mut{color:var(--muted);}
/* meaningful pastel tints */
.kpi.blue{background:#eef3ff;border-color:#dde6fe;}
.kpi.rose{background:#fff1f3;border-color:#ffe0e6;}
.kpi.green{background:#ecfdf5;border-color:#caeede;}
.kpi.amber{background:#fffaeb;border-color:#fbeec4;}
.kpi.blue .kpi-v{color:#3730a3;} .kpi.rose .kpi-v{color:#be123c;}
.kpi.green .kpi-v{color:#047857;} .kpi.amber .kpi-v{color:#b45309;}

/* image card */
.imgwrap{background:#fff;border:1px solid var(--line);border-radius:16px;padding:10px;
  box-shadow:0 1px 2px rgba(16,24,40,0.04);}

/* tables, metrics, inputs */
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff;}
[data-testid="stMetric"]{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;
  box-shadow:0 1px 2px rgba(16,24,40,0.04);}
[data-testid="stMetricValue"]{color:var(--ink)!important;font-weight:600;}
[data-testid="stMetricLabel"] p{color:var(--muted)!important;font-size:0.8rem!important;}
[data-baseweb="select"]>div{background:#fff!important;border-color:var(--line)!important;border-radius:10px!important;}
.stTextInput input{background:#fff!important;border-color:var(--line)!important;}
.stButton>button{background:var(--indigo);color:#fff;border:none;border-radius:10px;font-weight:500;padding:8px 20px;}
.stButton>button:hover{background:#4338ca;color:#fff;}
[data-testid="stAlert"]{background:#eef2ff;border:1px solid #c7d2fe;border-radius:12px;color:var(--ink);}
[data-testid="stCaptionContainer"]{color:var(--muted)!important;}

/* ---- micro-interactions: smooth lift on hover ---- */
.kpi{transition:transform .18s ease,box-shadow .18s ease;}
.kpi:hover{transform:translateY(-3px);
  box-shadow:0 2px 4px rgba(16,24,40,0.05),0 16px 30px -12px rgba(16,24,40,0.20);}
.imgwrap{transition:transform .18s ease,box-shadow .18s ease;}
.imgwrap:hover{transform:translateY(-2px);box-shadow:0 14px 28px -14px rgba(16,24,40,0.20);}
[data-testid="stMetric"]{transition:transform .18s ease,box-shadow .18s ease;}
[data-testid="stMetric"]:hover{transform:translateY(-2px);box-shadow:0 12px 22px -12px rgba(16,24,40,0.16);}
.stButton>button{transition:background .15s ease,transform .12s ease,box-shadow .15s ease;
  box-shadow:0 6px 14px -6px rgba(79,70,229,0.45);}
.stButton>button:hover{transform:translateY(-1px);box-shadow:0 11px 22px -8px rgba(79,70,229,0.55);}
.stButton>button:active{transform:translateY(0);box-shadow:0 4px 10px -6px rgba(79,70,229,0.5);}
button[data-baseweb="tab"]{transition:color .15s ease;}
[data-testid="stDataFrame"]{transition:box-shadow .18s ease;}
[data-testid="stDataFrame"]:hover{box-shadow:0 12px 26px -16px rgba(16,24,40,0.18);}

/* ---- hero pills ---- */
.pills{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px;}
.pill{display:inline-flex;align-items:center;gap:7px;background:#fff;border:1px solid var(--line);
  border-radius:999px;padding:6px 14px;font-size:12.5px;font-weight:500;color:var(--ink);
  box-shadow:0 1px 2px rgba(16,24,40,0.04);transition:transform .15s ease,box-shadow .15s ease;}
.pill:hover{transform:translateY(-1px);box-shadow:0 7px 15px -8px rgba(16,24,40,0.20);}
.pill .dot{width:7px;height:7px;border-radius:50%;background:var(--indigo);}
.pill.g .dot{background:var(--green);} .pill.a .dot{background:var(--amber);}

/* ---- footer ---- */
.foot{margin-top:64px;padding-top:24px;border-top:1px solid var(--line);
  display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:14px;}
.foot .who{font-size:13.5px;color:var(--muted);}
.foot .who b{color:var(--ink);font-weight:600;}
.foot .stack{display:flex;flex-wrap:wrap;gap:7px;}
.foot .chip{background:#fff;border:1px solid var(--line);border-radius:999px;padding:5px 12px;
  font-size:12px;color:var(--muted);font-weight:500;transition:transform .15s ease,box-shadow .15s ease;}
.foot .chip:hover{transform:translateY(-1px);box-shadow:0 6px 13px -8px rgba(16,24,40,0.18);color:var(--ink);}
.foot a{color:var(--indigo)!important;font-weight:600;}
</style>
""", unsafe_allow_html=True)


# ---------- helpers ----------
def section(eyebrow, title, desc=None):
    d = f'<div class="sec-d">{desc}</div>' if desc else ''
    st.markdown(f'<div class="sec"><div class="eb">{eyebrow}</div><h2>{title}</h2>{d}</div>',
                unsafe_allow_html=True)

def kpi(col, label, value, delta=None, tone="pos", theme=""):
    d = f'<div class="kpi-d {tone}">{delta}</div>' if delta else ''
    col.markdown(f'<div class="kpi {theme}"><div class="kpi-l">{label}</div>'
                 f'<div class="kpi-v">{value}</div>{d}</div>', unsafe_allow_html=True)

def delay_color(x):
    """delay ratio (1..4) -> RGB on a green->amber->red ramp."""
    x = max(1.0, min(4.0, float(x))); t = (x - 1) / 3.0
    g, a, r = (5, 150, 105), (217, 119, 6), (225, 29, 72)
    if t < 0.5:
        u = t / 0.5; lo, hi = g, a
    else:
        u = (t - 0.5) / 0.5; lo, hi = a, r
    return [int(lo[i] + (hi[i] - lo[i]) * u) for i in range(3)]

def hbar(data, cat, val, suffix="", height=300, color=INDIGO,
         color_field=None, color_scale=None, sort="-x"):
    d = data.copy()
    d["_lbl"] = d[val].map(lambda v: f"{v:,.0f}{suffix}")
    base = alt.Chart(d).encode(
        y=alt.Y(f"{cat}:N", sort=sort, title=None,
                axis=alt.Axis(labelLimit=280, labelFontSize=13, labelColor=INK)))
    xx = alt.X(f"{val}:Q", title=None, axis=alt.Axis(labelFontSize=11, labelColor=MUTED))
    if color_field:
        bars = base.mark_bar(cornerRadiusEnd=6, height=22).encode(
            x=xx, color=alt.Color(f"{color_field}:N", scale=color_scale, legend=None))
    else:
        bars = base.mark_bar(cornerRadiusEnd=6, height=22, color=color).encode(x=xx)
    text = base.mark_text(align="left", dx=6, color=MUTED, fontSize=12, font="Inter").encode(
        x=f"{val}:Q", text="_lbl:N")
    return ((bars + text).properties(height=height).configure_view(strokeWidth=0)
            .configure_axis(grid=False, domainColor=LINE, tickColor=LINE)
            .configure(background="white", font="Inter"))


@st.cache_data
def load():
    hubs = pd.read_csv(p("outputs/tables/bottleneck_hubs.csv"))
    corr = pd.read_csv(p("outputs/tables/chronic_corridors.csv"))
    rt = pd.read_csv(p("outputs/tables/route_type_framework.csv"))
    mc = pd.read_csv(p("outputs/tables/model_comparison.csv"))
    memo = json.load(open(p("outputs/tables/memo_numbers.json")))
    shap_g = pd.read_csv(p("outputs/tables/shap_group_importance.csv"))
    shap_g.columns = ["group", "pct"]
    return hubs, corr, rt, mc, memo, shap_g

@st.cache_resource
def load_model():
    bundle = joblib.load(p("processed/eta_model.joblib"))
    feats = pd.read_parquet(p("processed/features_emb.parquet"))
    return bundle, feats

def prettify(s):
    # "Gurgaon_Bilaspur_HB" -> "Gurgaon Bilaspur HB" (keep abbreviations as-is)
    return (s.astype(str).str.replace("_", " ", regex=False)
            .str.replace(r"\s+", " ", regex=True).str.strip())

@st.cache_data
def load_map():
    fac = pd.read_csv(p("outputs/tables/facility_coords.csv"))
    arc = pd.read_csv(p("outputs/tables/top_corridor_arcs.csv"))
    fac["name"] = prettify(fac["name"])
    fac[["r", "g", "b"]] = fac["out_delay_ratio"].apply(lambda x: pd.Series(delay_color(x)))
    fac["radius"] = (fac["throughput"].clip(1, 4000) ** 0.5) * 230 + 700
    fac["delay_txt"] = fac["out_delay_ratio"].map(lambda v: f"{v:.2f}")
    arc["src"] = prettify(arc["src"]); arc["dst"] = prettify(arc["dst"])
    arc["name"] = arc["src"] + "  →  " + arc["dst"]
    arc["w"] = 1 + 6 * arc["sla_breach_contrib"] / arc["sla_breach_contrib"].max()
    return fac, arc

hubs, corr, rt, mc, memo, shap_g = load()
NM = {**dict(zip(corr["source_center"], corr["src"])),
      **dict(zip(corr["destination_center"], corr["dst"]))}
def label(c): return NM.get(c, c)

# ---------------- hero ----------------
st.markdown("""
<div class="hero">
  <div class="eb">Graph Intelligence · ETA</div>
  <h1>Delhivery — Graph-Based ETA Intelligence</h1>
  <div class="sub">The logistics network modelled as a directed graph of <b>1,657 facilities</b>
  and <b>2,783 corridors</b> — turning network structure into more accurate delivery ETAs.
  Held-out data 12 Sep – 3 Oct 2018.</div>
  <div class="pills">
    <span class="pill"><span class="dot"></span>1,657 facilities</span>
    <span class="pill"><span class="dot"></span>2,783 corridors</span>
    <span class="pill g"><span class="dot"></span>GraphSAGE embeddings</span>
    <span class="pill g"><span class="dot"></span>LightGBM</span>
    <span class="pill a"><span class="dot"></span>Held-out Sep–Oct 2018</span>
  </div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["Overview", "Network Map", "Bottleneck Hubs", "Corridors", "ETA Predictor",
                "Route Type", "Strategy Memo"])

sage = mc[mc.model.str.contains("SAGE")].iloc[0]
base = mc[mc.model.str.contains("baseline")].iloc[0]

# ============================ OVERVIEW ============================
with tabs[0]:
    section("Signal", "At a Glance")
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Trips Analysed", f"{memo['total_trips']:,}", "Full network", "mut", "blue")
    kpi(c2, "Late vs OSRM", f"{memo['late_pct']}%", "Actual > 1.6× OSRM", "neg", "rose")
    kpi(c3, "Graph Model · Within 15%", f"{sage['trip_within15']:.0f}%",
        f"+{sage['trip_within15']-base['trip_within15']:.0f}pp vs baseline", "pos", "green")
    kpi(c4, "Top-3 Hubs · Share of Delay", f"{memo['top3_share_pct']}%", "Concentration", "mut", "amber")

    section("Model Performance", "OSRM vs Baseline vs Graph-Enhanced",
            "% of trips whose predicted ETA lands within 15% of actual (trip grain = the business metric).")
    mcc = mc[["model", "trip_within15"]].copy()
    st.altair_chart(hbar(mcc, "model", "trip_within15", suffix="%", height=240, color=INDIGO),
                    use_container_width=True)
    show = mc[["model", "MAE", "within15", "trip_MAE", "trip_within15"]].round(1)
    show.columns = ["Model", "Hop MAE", "Hop w15%", "Trip MAE", "Trip w15%"]
    st.dataframe(show, width="stretch", hide_index=True)

    section("Geographic View", "The Network Across India",
            "A static snapshot — open the Network Map tab for the full interactive map.")
    _, mid, _ = st.columns([1, 2.4, 1])
    with mid:
        st.markdown('<div class="imgwrap">', unsafe_allow_html=True)
        st.image(p("outputs/figures/network_geo.png"))
        st.markdown('</div>', unsafe_allow_html=True)

    section("Attribution", "What Drives the ETA Model",
            "Share of total SHAP impact by feature group — network/graph-derived features in green.")
    NET = {"corridor/node delay history", "GraphSAGE embeddings",
           "node2vec embeddings", "graph centrality"}
    sg = shap_g.copy()
    sg["kind"] = sg["group"].apply(lambda g: "net" if g in NET else "other")
    scale = alt.Scale(domain=["net", "other"], range=[GREEN, "#cbd5e1"])
    st.altair_chart(hbar(sg, "group", "pct", suffix="%", height=260,
                         color_field="kind", color_scale=scale), use_container_width=True)

# ============================ NETWORK MAP ============================
with tabs[1]:
    section("Network Map", "Explore the Logistics Network",
            "Pan, zoom and hover. Dots = facilities (size = throughput, colour = delay severity); "
            "red arcs = the worst SLA-breach corridors.")
    fac, arc = load_map()
    scatter = pdk.Layer(
        "ScatterplotLayer", data=fac, get_position="[lon, lat]", get_radius="radius",
        get_fill_color="[r, g, b, 170]", pickable=True, radius_min_pixels=2,
        radius_max_pixels=24, stroked=True, get_line_color=[255, 255, 255, 120],
        line_width_min_pixels=0.3)
    arcs = pdk.Layer(
        "ArcLayer", data=arc, get_source_position="[s_lon, s_lat]",
        get_target_position="[d_lon, d_lat]", get_source_color=[225, 29, 72, 150],
        get_target_color=[225, 29, 72, 150], get_width="w", pickable=True, get_height=0.3)
    view = pdk.ViewState(latitude=22.6, longitude=80.5, zoom=3.7, pitch=38, bearing=0)
    tip = {"html": "<b>{name}</b><br/>Delay {delay_txt}× OSRM<br/>Throughput {throughput}",
           "style": {"backgroundColor": "#0f172a", "color": "white", "fontSize": "12px",
                     "borderRadius": "8px", "padding": "8px"}}
    st.pydeck_chart(pdk.Deck(layers=[scatter, arcs], initial_view_state=view,
                             map_provider="carto", map_style="light", tooltip=tip),
                    use_container_width=True)
    lc1, lc2, lc3 = st.columns(3)
    kpi(lc1, "Facilities Mapped", f"{len(fac):,}", "Real PIN-code locations", "mut", "blue")
    worst = fac.sort_values("out_delay_ratio", ascending=False).iloc[0]
    kpi(lc2, "Worst-Delay Facility", worst["name"][:22], f"{worst['out_delay_ratio']:.1f}× OSRM", "neg", "rose")
    kpi(lc3, "SLA-Breach Corridors", f"{len(arc)}", "Shown as red arcs", "mut", "amber")

# ============================ HUBS ============================
with tabs[2]:
    section("Bottlenecks", "Hubs Ranked by SLA-Breach Contribution",
            "Structural risk blends network centrality with SLA-breach impact (volume × severity).")
    n = st.slider("Show top N", 5, 30, 12)
    top = hubs.dropna(subset=["structural_risk"]).head(n).copy()
    top["hub"] = top["name"].str.replace(r" \(.*\)", "", regex=True).str.slice(0, 30)
    st.altair_chart(hbar(top, "hub", "hub_sla_contrib", height=max(240, n * 26), color=RED),
                    use_container_width=True)
    cols = ["name", "betweenness", "throughput", "out_trips", "out_delay_ratio",
            "hub_sla_contrib", "structural_risk"]
    t2 = top[cols].copy()
    t2["betweenness"] = t2["betweenness"].round(3)
    t2["out_delay_ratio"] = t2["out_delay_ratio"].round(2)
    t2["structural_risk"] = t2["structural_risk"].round(3)
    t2.columns = ["Hub", "Betweenness", "Throughput", "Out Trips", "Out Delay Ratio",
                  "SLA-Breach Contrib", "Structural Risk"]
    st.dataframe(t2, width="stretch", hide_index=True)

# ============================ CORRIDORS ============================
with tabs[3]:
    section("Corridors", "Chronic Delay Corridors",
            "Lanes where actual time exceeds OSRM, ranked by SLA-breach contribution.")
    states = sorted(set(corr["state_src"].dropna()) | set(corr["state_dst"].dropna()))
    f = st.selectbox("Filter by state (source or destination)", ["All"] + states)
    d = corr.copy()
    if f != "All":
        d = d[(d.state_src == f) | (d.state_dst == f)]
    d = d.sort_values("sla_breach_contrib", ascending=False).head(200)
    view = d[["src", "dst", "n_trips", "w_median", "med_excess", "sla_breach_contrib"]].copy()
    view.columns = ["From", "To", "Trips", "Delay Ratio", "Excess Min (Median)", "SLA-Breach Contribution"]
    view["Delay Ratio"] = view["Delay Ratio"].round(2)
    st.dataframe(view, width="stretch", hide_index=True)

# ============================ PREDICTOR ============================
with tabs[4]:
    section("Predictor", "Calibrated ETA for a Corridor",
            "Pick a lane in the network; the graph-enhanced model predicts actual delivery time vs raw OSRM.")
    bundle, feats = load_model()
    model, FEATS = bundle["model"], bundle["feats"]
    lane = feats.groupby(["source_center", "destination_center"]).size().reset_index(name="n")
    lane = lane.sort_values("n", ascending=False)
    lane["label"] = lane.apply(lambda r: f"{label(r['source_center'])} -> "
                                         f"{label(r['destination_center'])} ({r['n']} trips)", axis=1)
    pick = st.selectbox("Corridor", lane["label"].head(300).tolist())
    row = lane[lane.label == pick].iloc[0]
    rec = feats[(feats.source_center == row.source_center) &
                (feats.destination_center == row.destination_center)].iloc[[0]].copy()
    rt_opt = st.radio("Route type", ["(as observed)", "FTL", "Carting"], horizontal=True)
    if rt_opt != "(as observed)":
        rec["route_type"] = pd.Categorical([rt_opt], categories=feats["route_type"].cat.categories)
    pred = float(model.booster_.predict(rec[FEATS])[0])
    osrm = float(rec["osrm_time"].iloc[0]); actual = float(rec["actual_time"].iloc[0])
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    # visual side-by-side comparison — OSRM vs Model vs Actual
    _order = ["OSRM Estimate", "Calibrated ETA · Model", "Actual · Historical"]
    comp = pd.DataFrame({"metric": _order, "minutes": [osrm, pred, actual]})
    comp["lbl"] = comp["minutes"].map(lambda v: f"{v:,.0f} min")
    _cscale = alt.Scale(domain=_order, range=["#94a3b8", GREEN, AMBER])
    _b = alt.Chart(comp).encode(
        y=alt.Y("metric:N", sort=_order, title=None,
                axis=alt.Axis(labelFontSize=14, labelColor=INK, labelLimit=320)))
    _bars = _b.mark_bar(cornerRadiusEnd=7, height=34).encode(
        x=alt.X("minutes:Q", title=None, axis=alt.Axis(labelFontSize=11, labelColor=MUTED)),
        color=alt.Color("metric:N", scale=_cscale, legend=None))
    _txt = _b.mark_text(align="left", dx=8, color=INK, fontSize=14, font="Inter",
                        fontWeight=600).encode(x="minutes:Q", text="lbl:N")
    _chart = ((_bars + _txt).properties(height=180).configure_view(strokeWidth=0)
              .configure_axis(grid=False, domainColor=LINE, tickColor=LINE)
              .configure(background="white", font="Inter"))
    st.altair_chart(_chart, use_container_width=True)
    k1, k2, k3 = st.columns(3)
    kpi(k1, "OSRM Estimate", f"{osrm:.0f} min", "Routing engine", "mut", "blue")
    kpi(k2, "Calibrated ETA · Model", f"{pred:.0f} min", f"{pred-osrm:+.0f} min vs OSRM", "pos", "green")
    kpi(k3, "Actual · Historical", f"{actual:.0f} min", "Ground truth", "mut", "amber")
    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    st.info(f"OSRM under-predicts this lane by **{(actual/osrm-1)*100:.0f}%** historically. "
            f"The calibrated model lands within **{abs(pred-actual)/actual*100:.0f}%** of actual.")

# ============================ ROUTE TYPE ============================
with tabs[5]:
    section("Route Type", "FTL vs Carting Recommendations",
            "Counterfactual time–cost trade-off per corridor; toggle to see only recommended changes.")
    segs = rt["segment"].dropna().unique().tolist()
    fseg = st.multiselect("Segment", segs, default=segs)
    only_flip = st.checkbox("Only show recommended changes (flips)", value=True)
    d = rt[rt.segment.isin(fseg)].copy()
    if only_flip and "flip" in d.columns:
        d = d[d.flip == True]
    d["src"] = d["source_center"].map(label)
    d["dst"] = d["destination_center"].map(label)
    view = d[["src", "dst", "n", "med_dist", "segment", "cur", "rec"]].copy()
    view.columns = ["From", "To", "Trips", "Median km", "Segment", "Current", "Recommended"]
    st.dataframe(view.sort_values("Trips", ascending=False), width="stretch", hide_index=True)

# ============================ MEMO ============================
with tabs[6]:
    section("Strategy", "Network Operations Memo")
    st.markdown(open(p("outputs/strategy_memo.md")).read())

# ---------------- footer ----------------
st.markdown("""
<div class="foot">
  <div class="who">Built by <b>Anshuman Vijayvargiya</b> · Graph-based ETA intelligence for logistics networks ·
    <a href="https://github.com/BradCage-afk/Delhivery-ETA-Dashboard" target="_blank">GitHub ↗</a></div>
  <div class="stack">
    <span class="chip">LightGBM</span>
    <span class="chip">GraphSAGE</span>
    <span class="chip">node2vec</span>
    <span class="chip">Streamlit</span>
    <span class="chip">PyDeck</span>
  </div>
</div>
""", unsafe_allow_html=True)
