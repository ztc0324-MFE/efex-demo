"""
EFEX Payment Flow Monitor & AML Detection
A sketch tool for cross-border B2B account-to-account payment risk monitoring.

Built as follow-up to the discussion with Dimitri Zaninovich, May 2026.
Focus: payment flow mapping + AML/fraud detection layer + treasury linkage.

Author: Tianchi (Alex) Zhang
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="EFEX Payment Flow & AML Monitor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
.disclaimer-banner {
    background-color: #FFF3CD;
    border-left: 4px solid #FFC107;
    padding: 12px 16px;
    margin-bottom: 16px;
    border-radius: 4px;
    color: #856404;
    font-size: 13px;
}
.alert-high { background-color: #F8D7DA; color: #721C24; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }
.alert-med  { background-color: #FFF3CD; color: #856404; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }
.alert-low  { background-color: #D1ECF1; color: #0C5460; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }
.metric-tile {
    background: #F8F9FA;
    border: 1px solid #E9ECEF;
    border-radius: 8px;
    padding: 16px;
}
.rule-card {
    background: #FAFAFA;
    border-left: 3px solid #1F77B4;
    padding: 12px 16px;
    margin: 8px 0;
    border-radius: 4px;
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# HEADER
# ============================================================
st.title("🛡️ EFEX Payment Flow Monitor & AML Detection")
st.caption(
    "Cross-border B2B account-to-account payment risk layer · "
    "US ↔ MX corridor · USD / MXN"
)

st.markdown(
    """
<div class="disclaimer-banner">
<b>Sketch artifact — not affiliated with EFEX.</b> Built as a discussion piece for the conversation
with Dimitri, May 2026. All accounts and transactions shown are <b>synthetic data</b> designed to
illustrate payment-flow integrity tooling. Demonstrates the type of operational risk layer
I'd build for a cross-border payment platform.
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# SYNTHETIC DATA GENERATION
# ============================================================
US_CLIENTS = [
    # (name, segment, avg_daily_volume_usd, tx_per_day, primary_corridor)
    ("ACME_INDUSTRIES_US",      "Importer",  28_000,  1.2, "US→MX"),
    ("PACIFIC_ELECTRONICS",     "Importer",  62_000,  0.8, "US→MX"),
    ("MIDWEST_AUTOPARTS",       "Importer",  18_000,  1.5, "US→MX"),
    ("TEXAS_AGRO_LLC",          "Mixed",     34_000,  1.0, "Mixed"),
    ("BAY_AREA_LOGISTICS",      "Mixed",     22_000,  1.3, "Mixed"),
    ("HOUSTON_OILFIELD_SVCS",   "Exporter",  48_000,  0.6, "US→MX"),
    ("CALIF_PRODUCE_CO",        "Importer",  15_000,  2.0, "US→MX"),
    ("ARIZONA_FREIGHT",         "Mixed",     12_000,  1.8, "Mixed"),
]

MX_CLIENTS = [
    ("MEXICANA_TEXTILES_SA",    "Exporter",  30_000,  1.1, "MX→US"),
    ("MONTERREY_STEEL_SA",      "Exporter",  72_000,  0.7, "MX→US"),
    ("GUADALAJARA_FOODS",       "Exporter",  16_000,  1.6, "MX→US"),
    ("BAJA_AUTOMOTIVE",         "Mixed",     40_000,  0.9, "Mixed"),
    ("CDMX_DISTRIBUIDORA",      "Importer",  19_000,  1.4, "MX→US"),
    ("PUEBLA_MAQUILA_SA",       "Exporter",  55_000,  0.8, "MX→US"),
    ("YUCATAN_EXPORTS",         "Exporter",  11_000,  1.7, "MX→US"),
    ("TIJUANA_LOGISTICS",       "Mixed",     26_000,  1.2, "Mixed"),
]

ALL_CLIENTS = [(*c, "US") for c in US_CLIENTS] + [(*c, "MX") for c in MX_CLIENTS]

COUNTERPARTIES_US = [
    "DELTA_SUPPLY_CHAIN", "WEST_COAST_BANK", "NORTHRIDGE_LLC",
    "PACIFIC_TRUST_BANK", "EAGLE_TRADING_INC", "SUMMIT_CAPITAL",
    "REDWOOD_FINANCIAL", "ATLANTIC_COMMERCE",
]
COUNTERPARTIES_MX = [
    "BANCO_BAJIO_SA", "EMPRESA_DEL_NORTE", "GRUPO_INDUSTRIAL_MTY",
    "CASA_DE_CAMBIO_CDMX", "TRANSPORTES_ZAPATA", "BANCO_REGIO",
    "PROVEEDORA_NACIONAL", "COMERCIAL_DEL_SUR",
]


@st.cache_data(show_spinner=False)
def generate_transactions(n_days: int = 180, seed: int = 42) -> pd.DataFrame:
    """Build synthetic cross-border payment ledger with embedded suspicious patterns."""
    rng = np.random.default_rng(seed)
    start_date = pd.Timestamp.now().normalize() - pd.Timedelta(days=n_days)

    records = []
    fx_rate = 17.5  # USD/MXN baseline for value computation

    # ---------- Baseline organic flow ----------
    for name, segment, avg_vol, tx_per_day, corridor, country in ALL_CLIENTS:
        cp_pool = COUNTERPARTIES_MX if country == "US" else COUNTERPARTIES_US

        for day_offset in range(n_days):
            ts_base = start_date + pd.Timedelta(days=day_offset)
            if ts_base.weekday() >= 5:  # mostly weekday business
                if rng.random() > 0.15:
                    continue
            n_tx_today = rng.poisson(tx_per_day)
            for _ in range(n_tx_today):
                # Log-normal amount around client's typical size
                amount_usd = float(rng.lognormal(np.log(avg_vol), 0.6))
                amount_usd = max(500, min(amount_usd, 500_000))
                # Currency decision: USD for US clients sending, MXN for MX clients sending
                if country == "US":
                    currency = "USD"
                    amount_native = amount_usd
                    direction = "US→MX"
                else:
                    currency = "MXN"
                    amount_native = amount_usd * fx_rate
                    direction = "MX→US"
                counterparty = rng.choice(cp_pool)
                hours = rng.integers(8, 18)
                minutes = rng.integers(0, 60)
                ts = ts_base + pd.Timedelta(hours=int(hours), minutes=int(minutes))
                records.append({
                    "timestamp": ts,
                    "client": name,
                    "client_segment": segment,
                    "client_country": country,
                    "counterparty": counterparty,
                    "direction": direction,
                    "currency": currency,
                    "amount_native": round(amount_native, 2),
                    "amount_usd": round(amount_usd, 2),
                    "tx_id": f"TX{len(records):07d}",
                })

    df = pd.DataFrame(records)

    # ---------- Inject suspicious patterns ----------
    pattern_meta = {}

    # 1. STRUCTURING — client splits ~$70K into 8 transactions of $8.5K–$9.8K within 4 days
    struct_client = "MIDWEST_AUTOPARTS"
    struct_start = start_date + pd.Timedelta(days=n_days - 35)
    struct_rows = []
    for i in range(8):
        ts = struct_start + pd.Timedelta(days=i // 2, hours=int(10 + i), minutes=int(rng.integers(0, 59)))
        amt = float(rng.uniform(8_500, 9_850))
        struct_rows.append({
            "timestamp": ts, "client": struct_client, "client_segment": "Importer",
            "client_country": "US", "counterparty": "EAGLE_TRADING_INC",
            "direction": "US→MX", "currency": "USD",
            "amount_native": round(amt, 2), "amount_usd": round(amt, 2),
            "tx_id": f"TX{len(records) + i:07d}",
        })
    df = pd.concat([df, pd.DataFrame(struct_rows)], ignore_index=True)
    pattern_meta["MIDWEST_AUTOPARTS"] = "Injected: structuring (8x $8.5-9.8K in 4 days)"

    # 2. VELOCITY SPIKE — client's daily volume 10x normal on one day
    spike_client = "GUADALAJARA_FOODS"
    spike_day = start_date + pd.Timedelta(days=n_days - 20)
    spike_rows = []
    for i in range(6):
        ts = spike_day + pd.Timedelta(hours=int(9 + i), minutes=int(rng.integers(0, 59)))
        amt_usd = float(rng.uniform(35_000, 65_000))
        spike_rows.append({
            "timestamp": ts, "client": spike_client, "client_segment": "Exporter",
            "client_country": "MX", "counterparty": "REDWOOD_FINANCIAL",
            "direction": "MX→US", "currency": "MXN",
            "amount_native": round(amt_usd * fx_rate, 2),
            "amount_usd": round(amt_usd, 2),
            "tx_id": f"TX{len(records) + 100 + i:07d}",
        })
    df = pd.concat([df, pd.DataFrame(spike_rows)], ignore_index=True)
    pattern_meta["GUADALAJARA_FOODS"] = "Injected: velocity spike (10x daily volume)"

    # 3. SLEEPER ACTIVATION — dormant 75+ days, then 4 large transactions
    sleeper_client = "YUCATAN_EXPORTS"
    df = df[~((df["client"] == sleeper_client) &
              (df["timestamp"] > start_date + pd.Timedelta(days=n_days - 90)) &
              (df["timestamp"] < start_date + pd.Timedelta(days=n_days - 10)))]
    sleeper_rows = []
    sleeper_day = start_date + pd.Timedelta(days=n_days - 8)
    for i in range(4):
        ts = sleeper_day + pd.Timedelta(days=i // 2, hours=int(10 + i * 2))
        amt_usd = float(rng.uniform(45_000, 95_000))
        sleeper_rows.append({
            "timestamp": ts, "client": sleeper_client, "client_segment": "Exporter",
            "client_country": "MX", "counterparty": "SUMMIT_CAPITAL",
            "direction": "MX→US", "currency": "MXN",
            "amount_native": round(amt_usd * fx_rate, 2),
            "amount_usd": round(amt_usd, 2),
            "tx_id": f"TX{len(records) + 200 + i:07d}",
        })
    df = pd.concat([df, pd.DataFrame(sleeper_rows)], ignore_index=True)
    pattern_meta["YUCATAN_EXPORTS"] = "Injected: sleeper account activation (75-day dormancy → 4x large)"

    # 4. NEW LARGE COUNTERPARTY — first-ever transaction to a new entity, very large
    new_cp_client = "BAY_AREA_LOGISTICS"
    new_cp_day = start_date + pd.Timedelta(days=n_days - 12)
    new_cp_row = {
        "timestamp": new_cp_day + pd.Timedelta(hours=14),
        "client": new_cp_client, "client_segment": "Mixed",
        "client_country": "US", "counterparty": "SHELL_HOLDINGS_BVI",
        "direction": "US→MX", "currency": "USD",
        "amount_native": 185_000.00, "amount_usd": 185_000.00,
        "tx_id": f"TX{len(records) + 300:07d}",
    }
    df = pd.concat([df, pd.DataFrame([new_cp_row])], ignore_index=True)
    pattern_meta["BAY_AREA_LOGISTICS"] = "Injected: first-ever counterparty + large amount ($185K)"

    # 5. ROUND-TRIP — USD out and similar back within 48h via different counterparty
    rt_client = "TEXAS_AGRO_LLC"
    rt_day = start_date + pd.Timedelta(days=n_days - 25)
    rt_amt = 72_000.0
    rt_rows = [
        {
            "timestamp": rt_day + pd.Timedelta(hours=11),
            "client": rt_client, "client_segment": "Mixed",
            "client_country": "US", "counterparty": "PROVEEDORA_NACIONAL",
            "direction": "US→MX", "currency": "USD",
            "amount_native": rt_amt, "amount_usd": rt_amt,
            "tx_id": f"TX{len(records) + 400:07d}",
        },
        {
            "timestamp": rt_day + pd.Timedelta(days=1, hours=15),
            "client": rt_client, "client_segment": "Mixed",
            "client_country": "US", "counterparty": "EMPRESA_DEL_NORTE",
            "direction": "MX→US", "currency": "MXN",
            "amount_native": round(rt_amt * 0.98 * fx_rate, 2),
            "amount_usd": round(rt_amt * 0.98, 2),
            "tx_id": f"TX{len(records) + 401:07d}",
        },
    ]
    df = pd.concat([df, pd.DataFrame(rt_rows)], ignore_index=True)
    pattern_meta["TEXAS_AGRO_LLC"] = "Injected: round-trip pattern ($72K out / $70K back in 28h)"

    df = df.sort_values("timestamp").reset_index(drop=True)
    df["date"] = df["timestamp"].dt.date
    return df, pattern_meta


# ============================================================
# AML DETECTORS
# ============================================================
def detect_structuring(df, threshold=10_000, band_pct=0.85, window_days=7, min_count=3):
    """Flag clients with multiple transactions just below reporting threshold ($10K)."""
    sub = df[(df["amount_usd"] >= threshold * band_pct) & (df["amount_usd"] < threshold)].copy()
    if sub.empty:
        return pd.DataFrame()
    sub = sub.sort_values("timestamp")
    flags = []
    for client, g in sub.groupby("client"):
        g = g.sort_values("timestamp")
        for i, row in g.iterrows():
            window_end = row["timestamp"]
            window_start = window_end - pd.Timedelta(days=window_days)
            in_window = g[(g["timestamp"] >= window_start) & (g["timestamp"] <= window_end)]
            if len(in_window) >= min_count:
                flags.append({
                    "tx_id": row["tx_id"],
                    "client": client,
                    "timestamp": row["timestamp"],
                    "amount_usd": row["amount_usd"],
                    "counterparty": row["counterparty"],
                    "rule": "STRUCTURING",
                    "severity": "HIGH",
                    "detail": f"{len(in_window)} tx in {window_days}d below ${threshold:,} threshold",
                    "score": min(100, 40 + len(in_window) * 7),
                })
    return pd.DataFrame(flags)


def detect_velocity_spike(df, lookback=30, z_threshold=3.0, min_baseline_days=10):
    """Flag daily volume spikes per client (z-score against trailing baseline)."""
    daily = df.groupby(["client", "date"])["amount_usd"].sum().reset_index()
    daily = daily.sort_values(["client", "date"])
    daily["mean_t"] = daily.groupby("client")["amount_usd"].transform(
        lambda x: x.rolling(lookback, min_periods=min_baseline_days).mean().shift(1)
    )
    daily["std_t"] = daily.groupby("client")["amount_usd"].transform(
        lambda x: x.rolling(lookback, min_periods=min_baseline_days).std().shift(1)
    )
    daily["z"] = (daily["amount_usd"] - daily["mean_t"]) / daily["std_t"]
    flagged = daily[daily["z"] > z_threshold].copy()

    flags = []
    for _, row in flagged.iterrows():
        day_tx = df[(df["client"] == row["client"]) & (df["date"] == row["date"])]
        biggest = day_tx.loc[day_tx["amount_usd"].idxmax()] if not day_tx.empty else None
        if biggest is None:
            continue
        flags.append({
            "tx_id": biggest["tx_id"],
            "client": row["client"],
            "timestamp": pd.Timestamp(row["date"]),
            "amount_usd": row["amount_usd"],
            "counterparty": "—",
            "rule": "VELOCITY_SPIKE",
            "severity": "HIGH" if row["z"] > 5 else "MEDIUM",
            "detail": f"Daily volume ${row['amount_usd']:,.0f} vs baseline ${row['mean_t']:,.0f} (z={row['z']:.1f})",
            "score": min(100, 50 + int(row["z"] * 6)),
        })
    return pd.DataFrame(flags)


def detect_sleeper_activation(df, dormancy_days=60, min_amount=30_000, lookforward_days=7):
    """Flag dormant account reactivation. A real attacker often warms up with small tx,
    then ramps to large. So: find the dormancy gap, then flag any large tx within the
    next `lookforward_days` of activity resumption."""
    df_sorted = df.sort_values(["client", "timestamp"]).copy()
    df_sorted["gap_days"] = df_sorted.groupby("client")["timestamp"].diff().dt.total_seconds() / 86400

    # Find "wake-up" events: first tx after a gap > dormancy_days
    wake_events = df_sorted[df_sorted["gap_days"] > dormancy_days][["client", "timestamp", "gap_days"]]

    flags = []
    for _, w in wake_events.iterrows():
        client = w["client"]
        window_end = w["timestamp"] + pd.Timedelta(days=lookforward_days)
        # All tx for this client in the next `lookforward_days`, plus the wake tx itself
        followup = df[
            (df["client"] == client) &
            (df["timestamp"] >= w["timestamp"]) &
            (df["timestamp"] <= window_end) &
            (df["amount_usd"] >= min_amount)
        ]
        for _, row in followup.iterrows():
            flags.append({
                "tx_id": row["tx_id"],
                "client": client,
                "timestamp": row["timestamp"],
                "amount_usd": row["amount_usd"],
                "counterparty": row["counterparty"],
                "rule": "SLEEPER_ACTIVATION",
                "severity": "HIGH",
                "detail": f"Account dormant {w['gap_days']:.0f}d, large tx ${row['amount_usd']:,.0f} within {lookforward_days}d of wake",
                "score": min(100, 50 + int(w["gap_days"] / 4)),
            })
    return pd.DataFrame(flags)


def detect_new_large_counterparty(df, history_days=30, amount_threshold=50_000):
    """Flag first-ever transaction to a new counterparty above threshold."""
    df_sorted = df.sort_values("timestamp").copy()
    flags = []
    for client, g in df_sorted.groupby("client"):
        seen = set()
        for _, row in g.iterrows():
            if row["amount_usd"] >= amount_threshold and row["counterparty"] not in seen:
                # First time seeing this counterparty for this client
                flags.append({
                    "tx_id": row["tx_id"],
                    "client": client,
                    "timestamp": row["timestamp"],
                    "amount_usd": row["amount_usd"],
                    "counterparty": row["counterparty"],
                    "rule": "NEW_LARGE_COUNTERPARTY",
                    "severity": "MEDIUM",
                    "detail": f"First-ever payment to {row['counterparty']} at ${row['amount_usd']:,.0f}",
                    "score": min(100, 35 + int(row["amount_usd"] / 5000)),
                })
            seen.add(row["counterparty"])
    return pd.DataFrame(flags)


def detect_round_trip(df, hours=72, tol=0.08, min_amount=20_000):
    """Flag potential round-trip patterns: large outflow + similar inflow within window."""
    flags = []
    for client, g in df.groupby("client"):
        g = g.sort_values("timestamp").reset_index(drop=True)
        outs = g[(g["direction"] == "US→MX") & (g["amount_usd"] >= min_amount)]
        ins = g[(g["direction"] == "MX→US") & (g["amount_usd"] >= min_amount)]
        for _, out_row in outs.iterrows():
            window_end = out_row["timestamp"] + pd.Timedelta(hours=hours)
            window = ins[
                (ins["timestamp"] > out_row["timestamp"]) &
                (ins["timestamp"] <= window_end)
            ]
            for _, in_row in window.iterrows():
                ratio = in_row["amount_usd"] / out_row["amount_usd"]
                if abs(ratio - 1.0) <= tol:
                    flags.append({
                        "tx_id": in_row["tx_id"],
                        "client": client,
                        "timestamp": in_row["timestamp"],
                        "amount_usd": in_row["amount_usd"],
                        "counterparty": in_row["counterparty"],
                        "rule": "ROUND_TRIP",
                        "severity": "HIGH",
                        "detail": f"${out_row['amount_usd']:,.0f} out → ${in_row['amount_usd']:,.0f} back in {(in_row['timestamp'] - out_row['timestamp']).total_seconds()/3600:.0f}h",
                        "score": 85,
                    })
    return pd.DataFrame(flags)


# ============================================================
# TREASURY AGENT (FX DECISION ENGINE)
# ============================================================
def run_treasury_agent(state: dict, recent_flags: pd.DataFrame) -> dict:
    """
    Transparent rule-based treasury decision agent.

    Combines inventory position, directional signal, vol regime, flow forecast,
    and AML status into a recommended FX action with a full reasoning trace.

    Inputs:
        state: dict with current inventory, signal, regime, flow forecast, target
        recent_flags: AML alerts in recent window (used as guardrail)

    Returns:
        dict with action, size_usd, confidence, rationale, reasoning, warnings
    """
    reasoning = []
    warnings = []

    # ---- Step 1: AML guardrail ----
    high_recent = recent_flags[recent_flags["severity"] == "HIGH"]
    if len(high_recent) > 0:
        affected_clients = high_recent["client"].nunique()
        affected_amount = high_recent["amount_usd"].sum()
        reasoning.append(
            f"🛡️ **AML check**: {len(high_recent)} high-severity flags in window, "
            f"{affected_clients} clients, ${affected_amount:,.0f} restricted. "
            f"Restricted-pool funds excluded from sizing."
        )
        warnings.append(f"${affected_amount:,.0f} in restricted pool")
        aml_size_penalty = max(0.5, 1 - (affected_amount / max(state["total_inventory"], 1)))
    else:
        reasoning.append("🛡️ **AML check**: no high-severity flags. Full inventory available.")
        aml_size_penalty = 1.0

    # ---- Step 2: Vol regime ----
    regime = state["vol_regime"]
    if regime == "Stressed":
        reasoning.append("🌡️ **Vol regime: Stressed** → reduce sizing to 40%, prefer hedging over directional.")
        size_multiplier = 0.4
    elif regime == "Calm":
        reasoning.append("🌡️ **Vol regime: Calm** → lean into carry, sizing 120%.")
        size_multiplier = 1.2
    else:
        reasoning.append("🌡️ **Vol regime: Normal** → standard sizing.")
        size_multiplier = 1.0

    # ---- Step 3: Inventory vs target ----
    total_inv = state["mxn_inventory_usd"] + state["usd_inventory"]
    mxn_share = state["mxn_inventory_usd"] / max(total_inv, 1)
    target = state["target_mxn_share"]
    inv_skew = mxn_share - target  # positive = MXN-heavy

    if abs(inv_skew) < 0.04:
        reasoning.append(
            f"📦 **Inventory**: MXN share {mxn_share:.1%} ≈ target {target:.1%}. No rebalance pressure."
        )
    elif inv_skew > 0:
        reasoning.append(
            f"📦 **Inventory**: MXN-heavy ({mxn_share:.1%} vs {target:.1%} target). "
            f"Rebalance pressure → reduce MXN."
        )
    else:
        reasoning.append(
            f"📦 **Inventory**: MXN-light ({mxn_share:.1%} vs {target:.1%} target). "
            f"Rebalance pressure → add MXN."
        )

    # ---- Step 4: Directional signal ----
    signal = state["signal"]
    if signal > 0.3:
        reasoning.append(
            f"📈 **Signal**: MXN-positive ({signal:+.2f}). Carry + momentum favor holding/adding MXN."
        )
    elif signal < -0.3:
        reasoning.append(
            f"📉 **Signal**: MXN-negative ({signal:+.2f}). Macro favors converting to USD."
        )
    else:
        reasoning.append(f"➖ **Signal**: neutral ({signal:+.2f}). No strong directional conviction.")

    # ---- Step 5: Flow forecast ----
    flow = state["next_7d_net_flow"]
    if abs(flow) > 75_000:
        if flow > 0:
            reasoning.append(
                f"🔮 **Flow forecast**: +${flow/1000:.0f}K MXN net incoming next 7d. "
                f"Account for incoming inventory before sizing."
            )
        else:
            reasoning.append(
                f"🔮 **Flow forecast**: -${abs(flow)/1000:.0f}K MXN net outgoing next 7d. "
                f"Reserve inventory for client outflows."
            )
    else:
        reasoning.append(f"🔮 **Flow forecast**: ~flat (${flow/1000:+.0f}K). No forecast adjustment.")

    # ---- Step 6: Spot / Forward / Carry ----
    spot = state.get("spot_rate", 17.50)
    forward_1m = state.get("forward_1m", 17.65)
    forward_premium_pct = (forward_1m / spot - 1) * 100  # annualized roughly = *12
    annualized_carry = forward_premium_pct * 12  # 1m forward annualized

    if forward_premium_pct > 0.05:
        reasoning.append(
            f"💱 **Spot/Forward**: spot = {spot:.4f}, 1m fwd = {forward_1m:.4f} → "
            f"+{forward_premium_pct:.2f}% premium (≈ {annualized_carry:.1f}% annualized carry on MXN). "
            f"Holding MXN earns carry; market prices in MXN depreciation."
        )
        carry_signal = 0.3  # carry favors holding MXN
    elif forward_premium_pct < -0.05:
        reasoning.append(
            f"💱 **Spot/Forward**: spot = {spot:.4f}, 1m fwd = {forward_1m:.4f} → "
            f"{forward_premium_pct:.2f}% discount. Negative carry — holding MXN loses to forwards."
        )
        carry_signal = -0.3
    else:
        reasoning.append(
            f"💱 **Spot/Forward**: spot = {spot:.4f}, 1m fwd = {forward_1m:.4f} → flat curve, neutral carry."
        )
        carry_signal = 0.0

    # If user has a directional view, compare to market-implied (forward)
    # If signal > 0 (expect MXN to strengthen) and forward shows weakening → strong divergence = alpha
    market_implied_direction = -1 if forward_premium_pct > 0.05 else (1 if forward_premium_pct < -0.05 else 0)
    if signal > 0.3 and market_implied_direction < 0:
        reasoning.append(
            f"⚡ **Alpha opportunity**: Your view ({signal:+.2f}) disagrees with forward curve "
            f"({market_implied_direction:+.0f}). If correct, this is alpha — market underprices MXN."
        )
    elif signal < -0.3 and market_implied_direction > 0:
        reasoning.append(
            f"⚡ **Alpha opportunity**: Your view ({signal:+.2f}) disagrees with forward curve. "
            f"If correct, market overprices MXN — short MXN via forward."
        )

    # ---- Decision combination ----
    # Weighted combination: inventory rebalance + directional signal + flow pre-positioning + carry
    combined_score = (
        -inv_skew * 1.5             # Pull toward target inventory
        + signal * 1.0               # Directional view
        + (flow / 1_000_000) * 0.5   # Pre-position for forecast flow
        + carry_signal * 0.5         # Carry (forward premium) factor
    )

    base_size = 80_000  # base trade size USD
    effective_multiplier = size_multiplier * aml_size_penalty

    if combined_score > 0.45:
        action = "BUY MXN"
        size = int(base_size * min(combined_score, 1.5) * effective_multiplier)
        rationale = "Multi-signal alignment for MXN accumulation."
    elif combined_score < -0.45:
        action = "SELL MXN"
        size = int(base_size * min(abs(combined_score), 1.5) * effective_multiplier)
        rationale = "Multi-signal alignment for MXN reduction."
    elif regime == "Stressed":
        action = "HEDGE ONLY"
        size = int(base_size * 0.5 * effective_multiplier)
        rationale = "Stressed regime → neutralize exposure via forwards rather than take directional bet."
    else:
        action = "HOLD"
        size = 0
        rationale = "No strong signal. Maintain current inventory."

    # Override: pause if restricted pool exceeds critical share of inventory
    restricted_share = 0.0
    if len(high_recent) > 0:
        restricted_share = high_recent["amount_usd"].sum() / max(state["total_inventory"], 1)
    if restricted_share > 0.30:
        action = "PAUSE"
        size = 0
        rationale = (
            f"Restricted pool (${high_recent['amount_usd'].sum():,.0f}) exceeds 30% of total inventory — "
            f"pausing directional activity pending review."
        )
        warnings.append("Operator review required before resuming")

    # ---- Confidence ----
    signals_aligned = sum([
        abs(inv_skew) > 0.05,
        abs(signal) > 0.3,
        abs(flow) > 75_000,
    ])
    if signals_aligned >= 2 and len(warnings) == 0:
        confidence = "HIGH"
    elif signals_aligned >= 1:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "action": action,
        "size_usd": size,
        "confidence": confidence,
        "rationale": rationale,
        "reasoning": reasoning,
        "warnings": warnings,
        "combined_score": combined_score,
        "size_multiplier": effective_multiplier,
    }


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.header("⚙️ Configuration")
n_days = st.sidebar.slider("History window (days)", 90, 365, 180)

st.sidebar.markdown("**Detector thresholds**")
struct_threshold = st.sidebar.number_input("Structuring threshold ($)", 5_000, 50_000, 10_000, 1000)
struct_window = st.sidebar.slider("Structuring window (days)", 3, 14, 7)
struct_min_count = st.sidebar.slider("Structuring min count", 2, 6, 3)
velocity_z = st.sidebar.slider("Velocity spike z-score", 2.0, 5.0, 3.0, 0.1)
dormancy_days = st.sidebar.slider("Sleeper dormancy threshold (days)", 30, 120, 60)
new_cp_amount = st.sidebar.number_input("New-counterparty threshold ($)", 10_000, 200_000, 50_000, 5000)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Built by Tianchi (Alex) Zhang**  \n"
    "Follow-up sketch for EFEX  \n"
    "May 2026 · Synthetic data only"
)

# ============================================================
# LOAD DATA + RUN DETECTORS
# ============================================================
with st.spinner("Generating synthetic payment ledger..."):
    df, injected_patterns = generate_transactions(n_days=n_days)

with st.spinner("Running AML detectors..."):
    flags_struct = detect_structuring(df, threshold=struct_threshold,
                                       window_days=struct_window, min_count=struct_min_count)
    flags_velocity = detect_velocity_spike(df, z_threshold=velocity_z)
    flags_sleeper = detect_sleeper_activation(df, dormancy_days=dormancy_days)
    flags_newcp = detect_new_large_counterparty(df, amount_threshold=new_cp_amount)
    flags_rt = detect_round_trip(df)

all_flags = pd.concat([flags_struct, flags_velocity, flags_sleeper, flags_newcp, flags_rt],
                       ignore_index=True)
if not all_flags.empty:
    all_flags = all_flags.sort_values(["score", "timestamp"], ascending=[False, False])

# ============================================================
# TOP KPI ROW
# ============================================================
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Total transactions", f"{len(df):,}")
with c2:
    st.metric("Total volume", f"${df['amount_usd'].sum()/1e6:.1f}M")
with c3:
    st.metric("Active clients", f"{df['client'].nunique()}")
with c4:
    st.metric("⚠️ Flagged transactions", f"{len(all_flags)}",
              delta=f"{len(all_flags)/max(len(df),1)*100:.2f}% of total", delta_color="inverse")
with c5:
    high = len(all_flags[all_flags["severity"] == "HIGH"]) if not all_flags.empty else 0
    st.metric("🚨 High-severity alerts", f"{high}", delta_color="inverse")

st.markdown("")

# ============================================================
# TABS
# ============================================================
tab1, tab2 = st.tabs([
    "🛡️ AML Detection & Investigation",
    "🤖 Treasury Agent — When to Buy / When to Sell",
])

# ============================================================
# TAB 1 — AML DETECTION & INVESTIGATION (simplified)
# ============================================================
with tab1:
    st.subheader("AML detection")
    st.caption(
        "Five rule-based detectors flag suspicious cross-border payment patterns. "
        "Rule-based for auditability — production version would layer ML on top."
    )

    st.markdown(
        """
**The five detection rules:**

- 🧱 **Structuring** — multiple transactions just below the $10K reporting threshold (CTR avoidance)
- 📈 **Velocity spike** — sudden daily volume jump vs. the client's own baseline (z-score > 3σ)
- 💤 **Sleeper activation** — dormant account suddenly transacts large (shell-company / takeover)
- 🆕 **New large counterparty** — first-ever payment to a new entity above threshold
- 🔁 **Round-trip** — outflow + similar inflow within 72h via different counterparty (layering)
"""
    )

    st.markdown("---")

    if all_flags.empty:
        st.info("No flagged transactions at current thresholds. Adjust in the sidebar.")
    else:
        # Headline summary
        n_clients = all_flags["client"].nunique()
        n_total = len(all_flags)
        n_high = len(all_flags[all_flags["severity"] == "HIGH"])
        total_amt = all_flags["amount_usd"].sum()

        st.markdown(
            f"### 📋 {n_clients} clients flagged · {n_total} suspicious transactions · "
            f"{n_high} high-severity · ${total_amt/1e6:.1f}M flagged"
        )

        st.caption(
            "Ranked by max risk score. Multiple rules firing on the same client is the strongest signal."
        )

        # Centerpiece: ranked client table
        client_summary = (
            all_flags.groupby("client")
            .agg(
                alerts=("tx_id", "count"),
                rules=("rule", lambda x: ", ".join(sorted(set(x)))),
                flagged_amount=("amount_usd", "sum"),
                max_score=("score", "max"),
            )
            .reset_index()
            .sort_values("max_score", ascending=False)
        )
        client_summary["flagged_amount"] = client_summary["flagged_amount"].apply(
            lambda x: f"${x:,.0f}"
        )
        client_summary = client_summary.rename(
            columns={
                "client": "Client",
                "alerts": "Alerts",
                "rules": "Rules triggered",
                "flagged_amount": "Total flagged ($)",
                "max_score": "Risk score",
            }
        )

        st.dataframe(
            client_summary,
            use_container_width=True,
            hide_index=True,
            height=420,
        )

        st.info(
            "💡 **Top clients to investigate first** are the ones with multiple rules triggered — "
            "single-rule alerts are usually noise, but cross-rule overlap is a real signal of layered "
            "suspicious activity."
        )

        # Optional drill-down — collapsed by default to keep the view clean
        with st.expander("📂 See individual flagged transactions"):
            display_df = all_flags[[
                "timestamp", "client", "counterparty", "amount_usd",
                "rule", "severity", "score", "detail",
            ]].copy()
            display_df = display_df.sort_values(["score", "timestamp"], ascending=[False, False])
            display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
            display_df["amount_usd"] = display_df["amount_usd"].apply(lambda x: f"${x:,.0f}")
            display_df = display_df.rename(
                columns={
                    "timestamp": "Time", "client": "Client", "counterparty": "Counterparty",
                    "amount_usd": "Amount", "rule": "Rule", "severity": "Severity",
                    "score": "Risk", "detail": "Detail",
                }
            )
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

            csv = all_flags.to_csv(index=False)
            st.download_button(
                "📥 Download flagged transactions (CSV)",
                csv,
                "efex_aml_flags.csv",
                "text/csv",
            )

    st.info(
        "💡 **How this feeds the Treasury Agent** → flagged funds are excluded from the available pool "
        "the agent can deploy. See Tab 2 to watch the linkage in action."
    )


# ============================================================
# TAB 2 — TREASURY AGENT (renamed)
# ============================================================
with tab2:
    st.subheader("Treasury Agent — FX Decision Engine")
    st.caption(
        "Combines inventory, directional signal, vol regime, flow forecast, and AML status "
        "into a recommended FX action with a full reasoning trace."
    )

    st.markdown("##### 1. Current state")
    st.caption("Edit these inputs to see how the agent's decision changes.")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        mxn_inv = st.number_input(
            "MXN inventory (USD equiv.)",
            min_value=0, max_value=10_000_000, value=1_200_000, step=50_000,
        )
        usd_inv = st.number_input(
            "USD inventory",
            min_value=0, max_value=10_000_000, value=1_800_000, step=50_000,
        )
    with col_b:
        signal = st.slider(
            "Directional signal",
            min_value=-1.0, max_value=1.0, value=0.35, step=0.05,
            help="Your view on MXN. From Layer 3 FX signal (carry, momentum, vol-scaled). "
                 "Positive = expect MXN to strengthen, Negative = expect MXN to weaken.",
        )
        vol_regime = st.selectbox(
            "Vol regime",
            options=["Calm", "Normal", "Stressed"],
            index=1,
            help="From Layer 2 vol regime classifier.",
        )
    with col_c:
        flow_forecast = st.slider(
            "Net MXN flow forecast next 7d (USD)",
            min_value=-500_000, max_value=500_000, value=120_000, step=25_000,
            help="Predicted net MXN inflow (+) or outflow (-) from client activity.",
        )
        target_mxn_share = st.slider(
            "Target MXN inventory share",
            min_value=0.20, max_value=0.60, value=0.40, step=0.05,
            help="Strategic target for MXN as fraction of total liquidity.",
        )

    # Market rates row
    st.markdown("**Market rates** (spot + forward — defines carry and market-implied direction)")
    rate_col1, rate_col2, rate_col3 = st.columns(3)
    with rate_col1:
        spot_rate = st.number_input(
            "USD/MXN spot rate",
            min_value=15.0, max_value=22.0, value=17.50, step=0.01, format="%.4f",
            help="Current market exchange rate. 1 USD = X MXN.",
        )
    with rate_col2:
        forward_1m = st.number_input(
            "USD/MXN 1-month forward",
            min_value=15.0, max_value=22.0, value=17.65, step=0.01, format="%.4f",
            help="1-month forward rate. If forward > spot, market prices in MXN depreciation (positive carry for MXN holders).",
        )
    with rate_col3:
        # Compute and display derived carry
        fwd_premium = (forward_1m / spot_rate - 1) * 100
        annualized_carry = fwd_premium * 12
        st.metric(
            "Implied annualized carry on MXN",
            f"{annualized_carry:+.1f}%",
            help="Forward premium annualized. This is approximately the interest rate differential "
                 "MXN minus USD. Positive = holding MXN earns carry yield.",
        )

    # Use last 7 days of AML flags as the recent window
    if not all_flags.empty:
        cutoff = all_flags["timestamp"].max() - pd.Timedelta(days=7)
        recent_aml = all_flags[all_flags["timestamp"] >= cutoff].copy()
    else:
        recent_aml = pd.DataFrame(columns=["severity", "client", "amount_usd"])

    state = {
        "mxn_inventory_usd": mxn_inv,
        "usd_inventory": usd_inv,
        "total_inventory": mxn_inv + usd_inv,
        "signal": signal,
        "vol_regime": vol_regime,
        "next_7d_net_flow": flow_forecast,
        "target_mxn_share": target_mxn_share,
        "spot_rate": spot_rate,
        "forward_1m": forward_1m,
    }

    # Compute preview (always shows what the agent WOULD recommend)
    preview = run_treasury_agent(state, recent_aml)

    # Initialize decision log in session state
    if "decision_log" not in st.session_state:
        st.session_state.decision_log = []

    # ---- Preview section (live, updates with sliders) ----
    st.markdown("##### 2. Agent recommendation (preview)")
    st.caption(
        "🔍 **Preview only** — updates live as you change inputs. "
        "No decision is recorded until you click **Confirm**."
    )

    preview_styles = {
        "BUY MXN":    ("#28A745", "🟢"),
        "SELL MXN":   ("#DC3545", "🔴"),
        "HOLD":       ("#6C757D", "⚪"),
        "HEDGE ONLY": ("#FD7E14", "🟠"),
        "PAUSE":      ("#17A2B8", "⏸️"),
    }
    p_color, p_icon = preview_styles.get(preview["action"], ("#000", "•"))

    # Preview card — grayscale-ish, dashed border to signal "not yet committed"
    st.markdown(
        f"""
<div style="background: #FAFAFA; border: 2px dashed {p_color}; padding: 16px 20px; border-radius: 6px; margin: 8px 0; opacity: 0.92;">
    <div style="font-size: 12px; color: #888; margin-bottom: 4px; letter-spacing: 0.5px;">PREVIEW · not yet confirmed</div>
    <div style="font-size: 24px; font-weight: 700; color: {p_color};">{p_icon} {preview['action']}</div>
    <div style="font-size: 13px; color: #555; margin-top: 6px;">{preview['rationale']}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    pcol_x, pcol_y, pcol_z, pcol_w = st.columns(4)
    with pcol_x:
        st.metric("Size (USD)", f"${preview['size_usd']:,}")
    with pcol_y:
        pconf_icon = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}[preview["confidence"]]
        st.metric("Confidence", f"{pconf_icon} {preview['confidence']}")
    with pcol_z:
        st.metric("Combined score", f"{preview['combined_score']:+.2f}")
    with pcol_w:
        st.metric("Size multiplier", f"{preview['size_multiplier']:.2f}×")

    if preview["warnings"]:
        st.warning("⚠️ " + " · ".join(preview["warnings"]))

    # ---- Confirm button ----
    confirm_col, _ = st.columns([1, 3])
    with confirm_col:
        confirm_disabled = preview["action"] in ("HOLD", "PAUSE")
        confirm_clicked = st.button(
            f"✅ Confirm: {preview['action']}",
            type="primary",
            use_container_width=True,
            disabled=confirm_disabled,
            help=("HOLD and PAUSE require no action — nothing to confirm."
                  if confirm_disabled else
                  "Commit this decision to the audit log. Simulates submitting to execution."),
        )

    if confirm_clicked:
        # Snapshot the decision for audit log
        st.session_state.decision_log.insert(0, {
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": preview["action"],
            "size_usd": preview["size_usd"],
            "confidence": preview["confidence"],
            "score": preview["combined_score"],
            "spot": state.get("spot_rate", 0),
            "forward": state.get("forward_1m", 0),
            "mxn_inv": state["mxn_inventory_usd"],
            "usd_inv": state["usd_inventory"],
            "signal": state["signal"],
            "regime": state["vol_regime"],
            "warnings": "; ".join(preview["warnings"]) if preview["warnings"] else "—",
        })
        st.success(f"✅ Decision recorded: {preview['action']} · ${preview['size_usd']:,} · {preview['confidence']} confidence")

    # Use preview as the result for the rest of the display
    result = preview

    # ---- Reasoning trace ----
    st.markdown("##### 3. Reasoning trace")
    st.caption("Every decision component, in the order the agent evaluated it.")
    for step in result["reasoning"]:
        st.markdown(f"- {step}")

    # ---- Decision audit log ----
    st.markdown("---")
    st.markdown("##### 4. Decision audit log")
    st.caption(
        "Every confirmed decision is recorded here with full state snapshot. "
        "This is what regulators and risk committees would review post-trade."
    )

    if not st.session_state.decision_log:
        st.info(
            "📝 No decisions confirmed yet. Adjust inputs above and click **Confirm** to record a decision."
        )
    else:
        log_df = pd.DataFrame(st.session_state.decision_log)
        # Format for display
        display_log = log_df.copy()
        display_log["size_usd"] = display_log["size_usd"].apply(lambda x: f"${x:,}")
        display_log["score"] = display_log["score"].apply(lambda x: f"{x:+.2f}")
        display_log["spot"] = display_log["spot"].apply(lambda x: f"{x:.4f}")
        display_log["forward"] = display_log["forward"].apply(lambda x: f"{x:.4f}")
        display_log["mxn_inv"] = display_log["mxn_inv"].apply(lambda x: f"${x/1000:.0f}K")
        display_log["usd_inv"] = display_log["usd_inv"].apply(lambda x: f"${x/1000:.0f}K")
        display_log["signal"] = display_log["signal"].apply(lambda x: f"{x:+.2f}")
        display_log = display_log.rename(columns={
            "timestamp": "Time",
            "action": "Action",
            "size_usd": "Size",
            "confidence": "Conf.",
            "score": "Score",
            "spot": "Spot",
            "forward": "Fwd 1m",
            "mxn_inv": "MXN inv",
            "usd_inv": "USD inv",
            "signal": "Signal",
            "regime": "Regime",
            "warnings": "Warnings",
        })
        st.dataframe(display_log, use_container_width=True, hide_index=True, height=240)

        col_clear, col_count, _ = st.columns([1, 1, 3])
        with col_clear:
            if st.button("🗑️ Clear log", use_container_width=True):
                st.session_state.decision_log = []
                st.rerun()
        with col_count:
            st.metric("Decisions on record", len(st.session_state.decision_log))

    # ---- What-if comparison ----
    st.markdown("---")
    st.markdown("##### 5. What-if: how does AML status affect the decision?")
    st.caption(
        "Compare the recommendation with current AML flags vs. a clean book. "
        "Demonstrates the **Layer 1 → Layer 3 linkage**: AML flags don't just generate alerts, "
        "they constrain treasury action."
    )

    clean_aml = pd.DataFrame(columns=["severity", "client", "amount_usd"])
    result_clean = run_treasury_agent(state, clean_aml)

    cmp_col1, cmp_col2 = st.columns(2)
    with cmp_col1:
        st.markdown("**With current AML flags**")
        st.markdown(f"- Action: **{result['action']}**")
        st.markdown(f"- Size: **${result['size_usd']:,}**")
        st.markdown(f"- Size multiplier: **{result['size_multiplier']:.2f}×**")
        st.markdown(f"- Confidence: **{result['confidence']}**")
    with cmp_col2:
        st.markdown("**With clean AML book (counterfactual)**")
        st.markdown(f"- Action: **{result_clean['action']}**")
        st.markdown(f"- Size: **${result_clean['size_usd']:,}**")
        st.markdown(f"- Size multiplier: **{result_clean['size_multiplier']:.2f}×**")
        st.markdown(f"- Confidence: **{result_clean['confidence']}**")

    size_delta = result_clean["size_usd"] - result["size_usd"]
    if size_delta > 0:
        st.info(
            f"💡 AML constraints are reducing trade size by **${size_delta:,}**. "
            f"This is the protective effect of Layer 1 — funds in restricted pool are not deployed for FX."
        )
    else:
        st.info("💡 AML flags are not currently constraining the trade. Full inventory available for treasury action.")
