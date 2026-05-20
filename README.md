# EFEX Payment Flow Monitor & AML Detection

A sketch artifact for cross-border B2B account-to-account payment risk monitoring **with an FX decision agent layered on top**.
Built as a discussion follow-up after the conversation with Dimitri.

## What it shows

Two tabs, designed for a clean 5-minute walkthrough:

### 🛡️ Tab 1 — AML Detection & Investigation

Five rule-based detectors layered for cross-border B2B context:

| Detector | What it catches |
|----------|-----------------|
| **Structuring** | Multiple tx just below $10K threshold (CTR-avoidance) |
| **Velocity spike** | Daily volume z-score > 3σ vs baseline (account takeover, mule activity) |
| **Sleeper activation** | Dormant account + large tx within 7d of waking (shell activation) |
| **New large counterparty** | First-ever tx to new entity above threshold (trade-based ML) |
| **Round-trip** | Out + similar inflow within 72h via different CP (layering) |

Plus a ranked, filterable **investigation queue** with severity, risk score, cross-client correlation, and CSV export.

### 🤖 Tab 2 — Treasury Agent (When to Buy / When to Sell)

Transparent rule-based FX decision agent. Inputs:
- **Inventory skew** — current MXN share vs target → rebalance pressure
- **Directional signal** — vol-scaled momentum (Layer 3 FX signal)
- **Vol regime** — Calm/Normal/Stressed → sizing multiplier
- **Flow forecast** — net MXN flow next 7d → pre-positioning
- **AML guardrail** — restricted pool reduces effective inventory; auto-pause if > 30%

Outputs: `BUY MXN` / `SELL MXN` / `HOLD` / `HEDGE ONLY` / `PAUSE` with size, confidence, full reasoning trace.

**The killer feature**: side-by-side "what-if" panel showing how AML status changes the agent's decision. In a verified scenario, AML constraints reduce trade size ~26% and downgrade confidence HIGH → MEDIUM. That's the Layer 1 → Layer 3 linkage made visible.

## How this matches the conversation

Dimitri described the role as two halves:

| Half | What he said | What this sketch covers |
|------|--------------|------------------------|
| **(1)** | "Mapping and redesigning the payment flow" | Tab 1: AML detection + investigation queue |
| **(2)** | "Building agents to decide when to buy and when to sell" | Tab 2: transparent decision agent with reasoning trace + AML-constrained sizing |

**The two halves are wired together.** AML flags don't just produce alerts — they reduce inventory the agent is allowed to deploy. Verified: trade size drops ~26%, confidence drops HIGH → MEDIUM when restricted-pool funds are present.

## The five detectors

| Detector | What it catches |
|----------|-----------------|
| Structuring | Multiple tx just below $10K threshold |
| Velocity spike | Daily volume z-score > 3σ vs baseline |
| Sleeper activation | Dormant account + large tx within 7d of waking |
| New large counterparty | First-ever tx to new entity above threshold |
| Round-trip | Out + similar inflow within 72h via different CP |

Rule-based for transparency and auditability; production version would layer ML scoring on top.

## The treasury agent

Transparent decision logic combining:
- **Inventory skew** — current MXN share vs target → rebalance pressure
- **Directional signal** — vol-scaled momentum from Layer 3 FX signal
- **Vol regime** — Calm/Normal/Stressed → sizing multiplier (1.2× / 1.0× / 0.4×)
- **Flow forecast** — predicted net MXN flow next 7 days → pre-positioning
- **AML guardrail** — restricted pool reduces effective inventory; auto-pause if restricted > 30%

Outputs: `BUY MXN` / `SELL MXN` / `HOLD` / `HEDGE ONLY` / `PAUSE` with size, confidence, full reasoning trace.

**Why rule-based, not LLM?** Treasury decisions need to be reproducible and auditable for risk committee, regulators, and post-trade analysis. An LLM layer can sit *on top* for explanation, scenario simulation, exception handling — but the core decision logic stays deterministic.

## Verification

All five injected suspicious patterns are detected:

```
✓ MIDWEST_AUTOPARTS    → STRUCTURING (8x $8.5-9.8K in 4 days)
✓ GUADALAJARA_FOODS    → VELOCITY_SPIKE (10x daily volume)
✓ YUCATAN_EXPORTS      → SLEEPER_ACTIVATION (75d dormant → 4x large)
✓ BAY_AREA_LOGISTICS   → NEW_LARGE_COUNTERPARTY ($185K to new shell)
✓ TEXAS_AGRO_LLC       → ROUND_TRIP ($72K out / $70K back in 28h)
```

Agent tested across 5 scenarios — produces sensible varied decisions (HOLD / HEDGE ONLY / BUY / SELL) and AML guardrail measurably reduces trade size in active scenarios.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`.

## Deploy to Streamlit Community Cloud

1. Push these files to a public GitHub repo
2. Go to https://share.streamlit.io → "New app" → point to your repo
3. Get a public URL in ~2 minutes

## What this is NOT

- Not a production AML or trading system
- Not based on real EFEX data — all synthetic
- Not affiliated with EFEX

## Author

**Tianchi (Alex) Zhang**
Senior Data Scientist (Model Risk) at Citi · MFE candidate at UC Berkeley Haas · PhD Statistics
Prior: Microsoft Xbox fraud detection · AnChain.AI DeFi threat intelligence (forensics on 500+ attacks, MCP-server agent for Claude Desktop)

May 2026

