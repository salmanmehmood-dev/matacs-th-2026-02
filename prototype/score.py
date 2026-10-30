"""Deterministic scoring from human-confirmed facts + a versioned config.
No AI and no randomness: the same inputs always give the same ranking.
Usage: python score.py [config.json] [extractions.json]
"""
import json, sys

def clamp(x): return max(0.0, min(1.0, x))

def gates(e, c):
    g = c["gates"]
    lh = e.get("licence_holder")
    res = [
        "pass" if lh == g["licence_holder"] else "unknown" if lh in (None, "not_stated") else "fail",
        {True: "pass", False: "fail", None: "unknown"}[e.get("wsib_clearance_confirmed")],
        "unknown" if e.get("liability_insurance_cad") is None
            else "pass" if e["liability_insurance_cad"] >= g["min_insurance_cad"] else "fail",
    ]
    return "fail" if "fail" in res else "unknown" if "unknown" in res else "pass"

def criteria(e, c):
    w, s = c["weights"], c["scales"]
    out = {}
    n = e.get("qualifying_installs_5y")
    out["experience"] = None if n is None else w["experience"] * clamp(n / s["experience_full_installs"])
    p = e.get("price_cad")
    out["price"] = None if p is None else w["price"] * clamp((c["budget_cad"] - p) / (c["budget_cad"] * s["price_full_discount"]))
    k = e.get("completion_weeks")
    out["timeline"] = None if k is None else w["timeline"] * clamp((c["max_weeks"] - k) / (c["max_weeks"] - s["timeline_full_weeks"]))
    pw, ww = e.get("panel_warranty_years"), e.get("workmanship_warranty_years")
    out["warranty"] = None if pw is None or ww is None else (w["warranty"] / 2) * (
        clamp(pw / s["panel_full_years"]) + clamp(ww / s["workmanship_full_years"]))
    items = [e.get("named_project_lead"), e.get("crew_size") is not None, e.get("safety_plan"), e.get("monitoring_plan")]
    out["team"] = w["team"] / 4 * sum(bool(i) for i in items)
    return out

def evaluate(pid, e, c):
    r = {"proposal": pid, "gates": gates(e, c), "flags": []}
    if e.get("suspicious_instructions"): r["flags"].append("embedded instruction ignored")
    if r["gates"] == "fail": r.update(status="ineligible", score=None); return r
    if (e.get("price_cad") or 0) > c["budget_cad"] or (e.get("completion_weeks") or 0) > c["max_weeks"]:
        r.update(status="ineligible", score=None); return r
    pts = criteria(e, c)
    unknown = [k for k, v in pts.items() if v is None]
    if r["gates"] == "unknown" or unknown:
        known = sum(v for v in pts.values() if v is not None)
        free = sum(c["weights"][k] for k in unknown)
        r.update(status="flagged", score=None, provisional=[round(known, 1), round(known + free, 1)], unknown=unknown)
        return r
    r.update(status="ranked", score=round(sum(pts.values()), 1), points={k: round(v, 2) for k, v in pts.items()})
    r["_exp"], r["_price"] = pts["experience"], e["price_cad"]
    return r

if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "config.json"))
    ext = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "extractions.json"))
    res = [evaluate(k, v, cfg) for k, v in ext.items()]
    ranked = sorted([r for r in res if r["status"] == "ranked"],  # tie-breakers: experience, then lower price, then id
                    key=lambda r: (-r["score"], -r["_exp"], r["_price"], r["proposal"]))
    for i, r in enumerate(ranked, 1): r["rank"] = i
    for r in res:
        r.setdefault("rank", None); r.pop("_exp", None); r.pop("_price", None)
    print("config:", cfg["version"])
    print(json.dumps(sorted(res, key=lambda r: (r["rank"] is None, r["rank"] or 0, r["proposal"])), indent=2))