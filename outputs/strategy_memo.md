# Network Operations Strategy Memo
### Delivery ETAs & Bottleneck Hubs — Graph-Based Network Intelligence

**To:** Head of Network Operations
**From:** Data Science Team
**Re:** Why our ETAs miss, where the network chokes, and the three moves that fix it
**Data window:** 12 Sep – 3 Oct 2018 · 14,817 trips · 1,657 facilities · 2,783 corridors

---

## The bottom line

Our delivery-time problem is **not random noise — it is two fixable, structural issues.**

1. **Our ETA engine is systematically wrong, not occasionally wrong.** OSRM underestimates
   actual delivery time on **97.8%** of legs, by a median factor of **2.0×**. Promising customers
   an OSRM time means we are late before the truck leaves. A network-aware model we built cuts
   this error and **lifts the share of trips predicted within 15% of actual from 4% to 48%.**
2. **The delay is concentrated, not spread evenly.** Just **3 hubs account for 27%** of all excess
   delay in the network; the **top 5 account for 32%.** Fixing a handful of facilities moves the
   whole network.

The three recommendations below follow directly: **recalibrate the promise, upgrade the choke
points, and right-size route types.**

---

## 1. Recalibrate the ETA promise (stop quoting raw OSRM)

OSRM treats every route as an independent, clean-traffic shortest path. Real delivery time depends
on the *network*: which corridor, which hub, what time of day. When we model the network as a
connected graph — learning each corridor's historical delay behaviour and each facility's structural
position — ETA error drops **16%** versus a strong point-to-point baseline, and trips landing within
15% of the true time rise from **4% (OSRM) to 48%.**

**Action:** replace customer-facing OSRM ETAs with the calibrated network model's ETA. This is the
single highest-leverage move — it fixes the "everything is late" problem at the source, because today
**84% of trips breach a 1.6× OSRM promise** purely due to OSRM's bias, not real failure.

---

## 2. Upgrade the top bottleneck hubs (delay is concentrated here)

We ranked every facility by **SLA-breach contribution** = how many excess delay-minutes accumulate on
its outbound corridors. The network's delay is dominated by a short list:

| # | Bottleneck hub | Share of network delay |
|---|----------------|------------------------|
| 1 | **Gurgaon_Bilaspur_HB** (Haryana) | **14.7%** |
| 2 | **Bhiwandi_Mankoli_HB** (Maharashtra) | **6.4%** |
| 3 | **Bangalore_Nelmngla_H** (Karnataka) | **5.5%** |
| 4 | Pune_Tathawde_H (Maharashtra) | 2.6% |
| 5 | Kolkata_Dankuni_HB (West Bengal) | 2.4% |

These are not small facilities with noisy numbers — they are the **highest-throughput, highest-
betweenness hubs** in the network (Gurgaon_Bilaspur alone sits on the most shortest-paths and feeds
7 of the 10 most-delayed corridors nationally). Delay here compounds downstream across every multi-leg
trip that routes through them.

**Projected impact — upgrade the top 3 hubs** (a process/capacity fix that cuts their outbound excess
delay by ~30%):

- **~3,800 delivery-hours of excess delay removed** in a 3-week window — **8% of all network delay**
  (≈ **63,000 hours/year** at this run-rate).
- **~490 fewer late deliveries** in the window against the current SLA (≈ **8,000/year**).
- **Revenue-at-risk recovered ≈ ₹2.5 lakh in-window (≈ ₹40 lakh/year)** at an assumed ₹500 per late
  delivery — this scales linearly with the true penalty/churn cost, which Operations should supply.

**Corridor-specific interventions** for the worst lanes feeding these hubs:

- **Gurgaon_Bilaspur → Bangalore / Kolkata / Hyderabad** (national trunk, median **22+ hours over
  OSRM**): the delay is at the *hub*, not the road — prioritise **facility capacity/dwell-time upgrade**
  at Gurgaon_Bilaspur over re-routing.
- **Guwahati_Hub → Delhi_Airport** (delay ratio **2.5×**): the single most severe corridor by ratio —
  candidate for a **parallel route / dedicated lane** given the North-East connectivity constraint.
- **Bhiwandi_Mankoli ↔ Gurgaon_Bilaspur** (both directions chronic): **scheduled-departure
  discipline** between the two largest hubs.

---

## 3. Right-size route types (FTL vs Carting)

Route type today is chosen almost entirely by distance. The data shows a cleaner rule. Where both are
viable (the **25–235 km "contestable" band, 58% of volume**), **FTL is more reliable than Carting** —
but the gap is *corridor-specific*, not uniform: measured lane-by-lane it ranges from negligible to
**+28%**, where a simple distance-band average would have hidden it.

- **Upgrade to FTL — ~1,230 trips (contestable lanes where FTL is materially faster, +10–28%):**
  lanes like *Delhi_Gateway → Gurgaon_Bilaspur* (+26%), *Bhiwandi → Mumbai_CottonGreen* (+28%), and
  the *Bengaluru* inter-hub shuttles (+14–24%). These are corridors whose Carting performance is far
  worse than typical — the structural risk of the origin makes the reliability worth the premium.
- **Downgrade to Carting — ~1,725 trips (contestable FTL lanes where FTL buys <10%):** shifting to
  consolidated Carting **saves cost at negligible service impact** — pending confirmation against true
  truck-utilisation economics.

*(Recommendations use a corridor-specific reliability prior with a corridor → distance-band → global
back-off, so each lane is judged on its own history where available — 88% of trips at corridor level.)*

---

## What we are asking for

| Move | Owner | Effort | Payoff |
|------|-------|--------|--------|
| Switch customer ETAs to the calibrated model | Product + Data | Low (model built) | within-15% accuracy 4%→48% |
| Capacity/dwell upgrade at Gurgaon_Bilaspur, Bhiwandi, Bangalore | Network Ops | High (capex) | −8% network delay, −8k late/yr |
| Parallel lane: Guwahati→Delhi | Network Ops | Medium | worst-ratio corridor fixed |
| Route-type rule: FTL >75km from risk hubs, Carting on short lanes | Planning | Low (policy) | reliability up, cost down |

**Assumptions to validate with Operations:** SLA promise = 1.6× OSRM; hub upgrade = 30% outbound-excess
reduction; ₹500 revenue-at-risk per late delivery; route-type cost expressed as a tier (FTL = premium)
pending true per-truck economics. Every figure above scales transparently with these inputs.

*Supporting analysis, model benchmarks, and the ranked hub/corridor tables accompany this memo.*
