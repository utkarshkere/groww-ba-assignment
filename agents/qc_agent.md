# QC agent (independent recompute)

**Role:** an independent quality-control agent. For every batch of numbers the analyst produced, it recomputed them from the raw CSVs with its **own code** (it never read or ran the analyst's scripts), checked the method and wording, and returned a verdict per number: MATCH / MINOR / MISMATCH / LOGIC ISSUE / UNVERIFIABLE.

**Runs:** batches 01–21 in the first session (Q1–Q3; see `notes/handoff_summary.md`), batches 22–30 in the final session (baseline rebuild, Q4, deck checks, final pre-submission check). Its scripts for batches 22–30 are in `qc_scripts/` (`qc_base.py` holds its revenue rules; `d90.py` its 90-day window module).

## Instructions given to the agent (final session)

> You are the independent QC agent for a Groww BA/SBA hiring data assignment. Your job: independently recompute every number you're sent from the RAW CSVs using YOUR OWN code, and check the method/formula logic and the wording. Never read, import or run the analyst's scripts or outputs — that defeats the purpose.
>
> **Agreed revenue rules** (apply exactly; if you think a rule is wrong, say so as LOGIC ISSUE but still verify against it):
> - F&O: EXECUTED, `brokerage_inr` (₹20). Commodity: EXECUTED, `brokerage_inr` (₹20). MF: COMPLETED, `brokerage_inr` (₹2, incl. redemptions). IPO: `brokerage_inr` > 0 (₹1).
> - Stocks: SUCCESS only. Recorded `original_brokerage` (incl. recorded 0) is used; SUCCESS with blank brokerage is imputed: CNC/MIS = min(₹20, max(₹5, 0.1%×turnover), 2.5%×turnover); MTF = 0.1%×turnover uncapped. Non-SUCCESS = ₹0. Revenue excludes `charges`.
> - D90 analyses use the cohort with signup ≤ 2 Aug 2026 (12,734 users), window 0 ≤ days since signup < 90.
>
> **Output for each batch:** a table `# | Claim | Analyst value | Your value | Verdict | Note`, then a short list of method or wording concerns (survivor bias, unfair comparison windows, overstated causal wording, small n, imputation share to disclose). For any MISMATCH, show the exact definition/filter used so the difference can be traced.

## What it changed (examples)

- **Pricing rule:** caught that the first stock-fee rule (no 2.5% cap) matched only 76–81% of recorded fees; the corrected rule matches 99.9%.
- **Q1:** "tied-best" → "statistically tied with the best"; "traded harder at the end" → "traded more per day than high-value users on the same dates"; flagged the unequal "after day 90" windows.
- **Q2:** withdrew a "score ≥ 10 = clear calls" tier; required the forward-only test result to be shown; corrected a signal count (335 → 333).
- **Q3:** confirmed Apple Search Ads' value sits almost entirely in June–July signups (and brand-keyword traffic), turning "More" into "More, in capped steps"; corrected Google's other-campaign count (~560 → 608).
- **Q4:** showed the "550 MTF users × ₹567" sizing was misleading (median ₹4.80, whale-driven, 55% from F&O traders); showed commodities stop with F&O while stocks partly survive, which set the stock-trading recommendation; reframed the "realistic" upside case.
- **Final check (batch 30):** go for submission after nine small fixes, all applied.
