# 🎤 EFEX Demo — Full Script

**For: Demo call with Dimitri**
**Length: 7-8 minutes**
**Style: Full sentences, simple English, easy to read out loud**

---

## ✅ Before the call

- Water on desk
- App open on Streamlit Cloud URL (NOT localhost)
- Phone on silent
- Take 3 deep breaths
- Count 1 to 10 out loud to warm up

---

## 🎬 PART 1 — Opening

**Share your screen and show the app.**

"Hi Dimitri. Thank you for making time today. After our call last week, I built this small app in about one day. It's just a sketch — synthetic data only, not real EFEX data, just to show how I would think about the problem you described. The app has two tabs, and I'd like to walk you through both. Let me start with tab one."

*[Pause. Look at camera for one second.]*

---

## 📊 PART 2 — Top numbers

**Point at the five numbers at the top of the screen.**

"First, let me explain the numbers at the top. We have two thousand six hundred transactions in this synthetic dataset, with total volume of eighty-five million dollars, across sixteen client companies. Out of all these transactions, eighty-eight are flagged as suspicious — that's about three percent. And thirty-three of them are high-severity alerts."

*[Pause]*

"Three percent flagged is a normal rate for AML systems. In a real production system, we would use machine learning on top to reduce false positives. But we start with rules first, because rules are much easier to explain to regulators."

---

## 🛡️ PART 3 — The five detection rules

**Scroll down to the section called "The five detection rules"**

"Now, the heart of tab one. We have five detection rules, and each one catches a different type of bad behavior."

**Point at Rule 1 — Structuring**

"Rule one is called Structuring. It catches clients who split a large payment into many small ones, each just below ten thousand dollars. Why ten thousand? Because in the US, banks must report any transaction over that amount to the government. So bad actors split payments to stay below the threshold and avoid being reported. This is actually illegal under US law."

*[Pause for one second]*

**Point at Rule 2 — Velocity spike**

"Rule two is Velocity spike. This catches sudden jumps in daily volume. We compare each day's volume to that client's own history. If today is much higher than normal — three standard deviations above the average — we flag it. Sudden volume spikes often mean account takeover or some kind of fraud."

*[Pause]*

**Point at Rule 3 — Sleeper activation**

"Rule three is Sleeper activation. This catches accounts that have been quiet for a long time and then suddenly become active again. Bad actors love these accounts, because they already passed KYC verification, so the system already trusts them."

*[Pause]*

**Point at Rule 4 — New large counterparty**

"Rule four is New large counterparty. This catches the first ever payment to a new entity, when the amount is large. A normal business usually starts with small payments to a new partner, then grows the relationship over time. But money laundering often starts with one big payment to a shell company."

*[Pause]*

**Point at Rule 5 — Round-trip**

"Rule five is Round-trip. This catches money that goes out, and then a similar amount comes back within seventy-two hours, through a different counterparty. This is called layering, and it's used to hide the original source of the money."

*[Pause for two seconds]*

"So we have five rules. Each rule is simple. Each rule catches one specific type of bad behavior."

---

## 📋 PART 4 — The result headline

**Scroll to the big headline that says: "16 clients flagged · 88 suspicious transactions · 33 high-severity · $10.1M flagged"**

"Now let's look at the result. After running all five detectors on the data, we get sixteen flagged clients, eighty-eight suspicious transactions, thirty-three high-severity alerts, and ten million dollars in flagged volume."

*[Pause]*

"But these raw numbers are not the real story. ⭐ **The real story is in the table below.**"

---

## 🔍 PART 5 — The client table (MOST IMPORTANT PART)

**Point at the table**

"Each row in this table is one client. They are sorted by maximum risk score, highest first. Now, I want you to look at the column called 'Rules triggered.' ⭐ **This is where the real story is.**"

*[Pause]*

### Story 1 — MIDWEST_AUTOPARTS

**Point at the MIDWEST_AUTOPARTS row**

"Let's look at the first client — MIDWEST_AUTOPARTS. Risk score one hundred, with nine alerts. The rules triggered are Structuring and Velocity spike. So this client is splitting payments to stay below the reporting threshold, AND they also have sudden volume jumps. This is a textbook structuring pattern."

*[Pause]*

### Story 2 — YUCATAN_EXPORTS ⭐⭐ (THE HERO STORY)

**Point at YUCATAN_EXPORTS row**

"But now look at YUCATAN_EXPORTS. Nine alerts, score ninety. But notice — three rules are triggered together: Sleeper activation, Structuring, and Velocity spike."

*[Slow down here. This is your big moment.]*

"Let me tell you what happened with this account. For three months, this account was normally active. Then it went completely silent for ninety days — no transactions at all. Then suddenly, four large transactions appeared, each between forty-five and ninety-five thousand dollars, all going to one single new counterparty."

*[Pause for one second]*

"Now, each one of these rules alone could be a coincidence. Sleeper activation alone — maybe it's just a seasonal exporter taking a break. Velocity spike alone — maybe they had one big shipment day. Structuring alone — maybe they have weird invoicing practices."

*[Pause for two seconds. Look at camera.]*

"⭐ **But all three rules firing together — that has no normal business explanation. This is the case I would send to compliance to investigate first thing Monday morning.**"

*[Pause for two seconds]*

### Story 3 — MEXICANA_TEXTILES_SA

**Point at a client with only one rule triggered**

"Now compare that to MEXICANA_TEXTILES at the bottom. Score seventy-nine, but only one rule — Velocity spike. One rule alone is usually just noise. Maybe a big shipment day, maybe nothing. So we don't prioritize this for investigation."

*[Pause]*

"And this is the main lesson from tab one:"

"⭐ **Single rule alone usually means noise. Multiple rules together means real signal.**"

"This table tells the compliance team exactly where to spend their time. We don't have to investigate every alert — we focus on clients where multiple rules overlap."

---

## 🧠 PART 6 — Why rule-based, not AI

*[Pause. Look at camera. This is an important moment.]*

"One more important point about tab one before I move on. You might wonder — why am I using rules and not machine learning?"

"The reason is auditability. In AML compliance, regulators ask: 'Why did you flag this transaction?' And we need to give a clear, specific answer. Not 'because the model said so.'"

*[Pause]*

"⭐ **Rules are transparent. Machine learning is a black box. Regulators need transparent.**"

"In production, we can still add machine learning on top of these rules — to improve precision and reduce false positives. But the rules stay as the foundation. The rules are what we can defend in court if needed."

---

## 🔄 PART 7 — Transition to Tab 2

"OK, so that was tab one — the protection layer. Now let me show you tab two, which is the revenue layer — the FX agent. And I want to show you how the two tabs connect."

**Click on Tab 2**

---

## 🤖 PART 8 — The agent setup

"This is the FX agent you described in our call. It decides when to buy MXN, when to sell MXN, when to hold, or when to hedge."

**Point at the inputs in section 1**

"The agent takes eight inputs. On the left side, we have current inventory — how much MXN and how much USD we are holding."

"In the middle, we have the directional signal, between minus one and plus one — this represents our view on MXN. Plus means we think MXN will strengthen. Minus means we think MXN will weaken."

"We also have the volatility regime — calm, normal, or stressed. This comes from market data."

"On the right side, we have the flow forecast — how much MXN we expect to receive from clients in the next seven days. And the target inventory share — what percentage of our money we want to hold in MXN."

**Point at the Market rates section**

"And below those, we have market rates. The spot rate — right now, one US dollar buys seventeen point five Mexican pesos. And the one-month forward rate — seventeen point six five pesos."

*[Pause]*

"You'll notice the forward rate is higher than the spot rate. This is because Mexico has higher interest rates than the United States. The difference works out to about ten percent on an annualized basis, which you can see on the right."

*[Pause]*

"⭐ **What this means is — just by holding MXN in our inventory, we earn about ten percent per year in carry yield. We don't need to be right about direction. We earn this just for holding the position.**"

---

## 👁️ PART 9 — Preview vs Confirm

**Point at the dashed green box "PREVIEW · not yet confirmed"**

"Now, this is a very important design choice. The decision you see here is just a preview. You can see it has a dashed border, and the label clearly says 'preview, not yet confirmed.'"

**Slowly drag the MXN inventory slider — from 1.2M up to 2.5M**

"Watch what happens when I change one of the inputs. As I drag this slider, the preview updates instantly. The size changes. The reasoning updates."

*[Drag back to 1.2M to reset]*

"But notice — nothing has been recorded yet. It's only a preview."

*[Pause. Look at camera. Slow down.]*

"Why does this matter? Because in any real production trading system, you never want a model to execute a trade just because someone moved a slider by accident."

"⭐ **Every real decision needs explicit confirmation. With a timestamp. With the full input state captured. So we have a complete audit record.**"

---

## ✅ PART 10 — Click Confirm and show audit log

**Click the Confirm button**

"Now let me click Confirm. You see the success message — the decision is locked in. Let's scroll down to see the audit log."

**Scroll down to section 4 — Decision audit log**

"Here is the audit log. The decision I just confirmed is now recorded with all the details: the exact timestamp, the action — buy MXN, the size — thirty-three thousand dollars, the confidence level, the spot and forward rates at that moment, our inventory balances, our signal, the volatility regime, and any warnings."

*[Pause]*

"It's a complete snapshot of the decision context."

*[Slow down here. Important moment.]*

"Six months from now, if compliance asks: 'Why did we buy MXN on May twentieth at ten thirty AM?' — we have the complete record. We can reconstruct exactly what the agent saw, why it made that decision, and what the market conditions were at the time."

"⭐ **We can show the regulator that we acted on policy and data. Not on vibes.**"

---

## 🔬 PART 11 — The reasoning trace

**Scroll back up to section 3 — Reasoning trace**

"And let me also show you the reasoning trace. For every decision, the agent shows every step of its thinking."

**Point at each bullet one at a time**

"First, the AML check — how many flagged transactions are in the recent window, and how much money is currently in the restricted pool."

"Then volatility regime — and what sizing multiplier we apply based on it."

"Then inventory pressure — are we MXN-heavy or MXN-light compared to our target."

"Then the directional signal — what's our view on MXN."

"Then flow forecast — how much MXN is coming in or going out this week."

"Then spot and forward — the implied carry yield."

"And finally, alpha opportunity — this fires when our view disagrees with what the market is pricing in."

*[Pause]*

"⭐ **Every number on the screen comes from somewhere. There are no magic numbers. Everything is fully traceable, step by step.**"

---

## 🔗 PART 12 — The killer linkage (THE PUNCHLINE) ⭐⭐

**Scroll to section 5 — What-if AML comparison**

"OK, now I want to show you the most important part of this whole demo. This last section connects tab one and tab two together."

*[Pause]*

**Point at the two-column comparison**

"On the left side, you see the agent's decision with the current AML flags active. On the right side, the same exact inputs, but pretending we have a completely clean book with no AML flags at all."

**Point at the size difference**

"Look at the difference between the two columns. On the left, the trade is smaller, and the confidence is medium. On the right, the trade is bigger, and the confidence is high."

*[Pause]*

"Why is there a difference? Because the AML layer from tab one is holding some of our money in a restricted pool — funds that cannot be deployed until compliance reviews them. So the agent has less inventory available to trade with."

*[Pause for two seconds. Look at camera. This is your big moment.]*

"⭐ **This is the loop. This is the whole point of the demo.**"

*[Pause]*

"⭐ **AML is not a separate compliance tool sitting on the side. AML actively controls how much the agent is allowed to trade.**"

*[Pause for two seconds]*

"⭐ **Tab one is not a side feature. Tab one is the gate for tab two.**"

*[Pause]*

"This is exactly what you described in our call. Agents that make automated decisions about buying and selling — but operational risk constrains them. The two layers must be wired together. And that's what this sketch is trying to demonstrate."

---

## 🎬 PART 13 — Closing

*[Stop touching sliders. Look at camera.]*

"So that's the full sketch. Let me just summarize what you saw."

"Tab one is the AML detection layer. Five rules catching different cross-border patterns. A ranked client queue showing compliance who to investigate first."

"Tab two is the FX agent. With a preview and confirm pattern, a full audit log, and a complete reasoning trace for every decision."

"And the connection between them — AML flags directly constrain what the agent is allowed to do."

*[Pause]*

"It's a rough sketch. About one day of work. All synthetic data. Not a production system. But I wanted to put something concrete on the screen, so we can have a more specific conversation about what a real version of this would look like."

*[Stop talking. Look at camera. Wait for Dimitri to respond. Do NOT keep talking.]*

---

# 🌟 5 Magic Phrases to Memorize

If you forget everything else, just remember these five sentences. They are the heart of your demo:

**1.** "Single rule alone usually means noise. Multiple rules together means real signal."

**2.** "Rules are transparent. Machine learning is a black box. Regulators need transparent."

**3.** "Every number comes from somewhere. There are no magic numbers."

**4.** "Just by holding MXN, we earn about ten percent per year in carry yield."

**5.** "Tab one is not a side feature. Tab one is the gate for tab two."

---

# 🆘 If Something Goes Wrong

**If the app doesn't load:**

"I'm sorry, the live app is having some trouble loading right now. Let me share some screenshots instead, and I can walk you through them."

**If a slider doesn't respond:**

"OK, this slider seems stuck. Let me just describe what would happen — when I increase MXN inventory, the agent would recommend selling more aggressively."

**If you forget a word or sentence:**

"Sorry, let me say that again."

*(That's it. Don't apologize more. Just continue.)*

**If you don't understand Dimitri's question:**

"Sorry, could you say that one more time, please?"

**If you need a moment to think:**

"That's a good question. Let me think for a second."

*(Then pause for three seconds. That's completely OK.)*

**If the internet lags:**

"Sorry about the connection. Let me continue from where I was."

---

# 📞 Common Questions — Full Sentence Answers

### Q1: "How would the agent get its directional signal in production?"

"The directional signal could come from a few different sources. It could be an internal quantitative model, or third-party data from a vendor, or even another set of rules. The important thing is that the agent doesn't care about the source — as long as the signal is normalized to be between minus one and plus one. By decoupling the signal generation from the decision layer, we can swap the model later without changing the agent itself."

### Q2: "Do you have direct FX trading experience?"

"I don't have direct FX trading experience yet. But I studied FX market microstructure during my MFE program at Berkeley. I worked on market-making and arbitrage simulations using EBS and TAQ data. And I built a crypto factor model at Hivemind Capital that uses the same framework — carry, volatility, and momentum factors. So the conceptual framework is very familiar to me. The specifics of FX market plumbing — liquidity provider relationships, settlement, NDFs — those I would need to learn on the job."

### Q3: "What about sanctions screening?"

"Sanctions screening is not in this sketch — it would be a separate layer. Typically that involves OFAC, UN, and EU sanctions list matching, plus fuzzy name matching for similar names. In a real system, that layer would sit before the AML detector. So sanctioned counterparties would be blocked at onboarding, and would never reach the AML detection queue in the first place."

### Q4: "How would you reduce false positives in AML?"

"There are two main approaches. First, tunable thresholds — we can adjust the sensitivity of each rule based on real performance data. Second, a feedback loop from analysts. Every time a compliance officer reviews an alert and marks it as true positive or false positive, that signal goes back to recalibrate the scoring. Over time, that's also how we would train an ML model on top of the rules — eventually replacing them, without losing auditability."

### Q5: "What's the latency requirement?"

"For corporate treasury, latency is not measured in milliseconds. Minutes is acceptable. This is not high-frequency trading. The more interesting latency question for me is flow forecasting — how far ahead can we reliably predict client MXN flows? That determines how aggressively we can pre-position inventory."

### Q6: "Why rule-based and not LLM?"

"Treasury decisions need to be defensible — to the risk committee, to regulators, and to your future self six months later when you need to audit a trade. Rule-based systems are reproducible and inspectable. LLMs are a black box. That doesn't mean LLMs have no role — they can sit on top of the rules, to provide natural language explanations or handle exceptional cases. But the core decision logic should always stay deterministic."

### Q7: "Could this work for other currency corridors, not just US-Mexico?"

"Yes, absolutely. The detectors themselves are corridor-agnostic. The corridor matters for calibration — thresholds and baseline rates would differ for different pairs. And it matters for the directional signal — each currency pair has different macro drivers. But the overall architecture stays the same."

### Q8: "What's missing for this to be production-ready?"

"A few important things. First, live data integration — we need to plug into the real transaction ledger, real market feeds, and the real KYC database. Second, an execution layer that connects to liquidity providers to actually book trades. Third, an approval workflow for trades above a certain size threshold — those need human sign-off. Fourth, a continuous learning system that records every decision and outcome, and uses that to recalibrate the rules. And fifth, a scenario simulator for stress events. The core decision skeleton is what you see here. The rest is engineering work on top."

### Q9: "What is the carry trade exactly?"

"Carry trade means borrowing in a low interest rate currency and holding a high interest rate currency. In our case, US interest rates are around five percent, and Mexican interest rates are around ten percent. So just by holding pesos instead of dollars, we earn the difference — about five to ten percent per year, depending on the exact rates. The forward rate already prices this in mathematically, so we can see the implied carry directly."

### Q10: "Why are you leaving Citi?"

"At Citi, I've been validating other people's models in a regulated environment. That taught me a lot about model risk and governance. But I want to move to the building side, on a smaller team, where I can own a function end to end and see the business impact directly. EFEX is at exactly the stage where that kind of ownership exists."

---

# 💪 Confidence Reminders

Before you start, remind yourself:

- Your English is good enough. Dimitri talks to non-native speakers all the time.
- Speaking slowly makes you look senior, not weak.
- Pausing means you're thinking carefully. That's a strength.
- The work itself is solid — you built a real, working application.
- Your story directly answers what Dimitri said in the call. It's not random.

---

# 🎯 Final Reminders

1. Speak **20% slower** than feels natural.
2. **Pause longer** than feels natural.
3. **Stop when you're done.** Do not fill silence with more words.
4. If Dimitri interrupts with a question, **that's a good sign** — he's engaged.
5. **Look at camera**, not at the screen, when you can.

---

**You are ready, Alex. Good luck.** 🚀

加油 — 你做得很好。明天结束后告诉我怎么样。
