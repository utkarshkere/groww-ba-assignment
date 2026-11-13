# Groww BA / SBA Hiring Assignment — New-User Value Analysis

**Live deck:** https://utkarshkere.github.io/groww-ba-assignment/ (the `index.html` in this repo, served by GitHub Pages)

Prepared by Utkarsh Kere · November 2026

---

## The assignment

Groww's Business Analyst / Senior Business Analyst hiring assignment (full brief: [`assignment/read_me.md`](assignment/read_me.md); column definitions: [`assignment/data_dictionary.md`](assignment/data_dictionary.md)).

**Data:** 20,000 users who signed up between April and September 2026 (`users.csv`), and every order they placed until 31 October 2026, split by product: stocks, F&O, mutual funds, IPOs and commodities. All tables join on `third_party_id`.

**Output rules:** any format, at most 10 pages, approach clearly explained. AI tools allowed, but the full prompt history must be submitted.

**The four questions**

1. **Who is worth focusing on?** Define "high value", show how high-value users differ, end with the 2–3 differences strong enough to act on.
2. **The watchlist.** Each week, pick ~20 new signups using only their first 7 days, so that as many as possible are high value by day 90.
3. **Where should the next marketing rupee go?** Which acquisition channels get more budget, and which get less.
4. **Revenue concentration and the next bet.** How concentrated is revenue, and what is the next bet if that source shrinks significantly?

## The answers in one line each

| Q | Answer |
|---|---|
| 1 | High value = the top 1% of new users by revenue in their first 90 days who are still trading in month 3: **94 users (0.74%) bringing 69.5% of 90-day revenue**. |
| 2 | Score every signup on day 7 with a 10-signal points card and pick the top 20: **about 3 of 20 picks become high value, 55% of what a perfect list could catch**. |
| 3 | Grow Apple Search Ads in capped monthly steps; grow HT, Zee and Referral gradually; cut NDTV, Times Internet and app-install networks. |
| 4 | **~84% of revenue rests on retail F&O traders**; a 30% F&O drop costs 21–25% of revenue. The next bet is stock trading: grow it among non-F&O users, and move F&O traders into stocks before they stop. |

## How to read the deck

Open `index.html` in any browser (or the live link above). It has a title cover, one cover per question (covers carry only the question and are **not counted**), and **10 content pages**:

| Pages | Content |
|---|---|
| 1 | Summary of all four answers and how the numbers were built |
| 2–4 | Q1: concentration and the definition · alternative definitions tested · how high-value users differ |
| 5–6 | Q2: the scorecard and how it was built · results and limits |
| 7–8 | Q3: value per signup by channel · where the budget moves |
| 9–10 | Q4: concentration, stress test, what not to bet on · the next bet, the gap, what to track |

Hover the ⓘ icons on table headers for exact column definitions.

## Method notes

- **Revenue** = brokerage Groww earns on successful orders: F&O and commodities ₹20 per executed order; stocks the recorded brokerage; mutual funds ₹2 per completed order; IPOs ₹1 per successful application. Exchange/statutory charges are excluded.
- **Missing stock fees:** 7,880 successful stock orders (29%, almost all Sep–Oct) have a blank fee. They are filled with Groww's published pricing rule, which reproduces 99.9% of recorded fees. Filled fees are ₹1.01L (34% of stock revenue, 6.9% of total).
- **Fair windows:** anything "by day 90" uses only the 12,734 users who signed up by 2 Aug 2026 and so have a full 90 days of data.
- **No spend / cost data** exists, so channel figures are break-even ceilings (the most a channel can cost per signup), not ROI.

## How AI was used

The analysis was done with Claude, with two supporting agents (details in [`agents/`](agents/)):

- **QC agent** — an independent agent that recomputed every number from the raw CSVs with its own code (never the analyst's scripts) and challenged the method. 30 check batches in total; it caught one wrong count, several rounding slips and many wording/denominator issues, all fixed. Its scripts are in [`agents/qc_scripts/`](agents/qc_scripts/).
- **Senior stakeholder reviewer** — an agent playing a senior analytics stakeholder at Groww, which reviewed the deck for UI/UX, unclear numbers, logic a senior reviewer would challenge, slices they would ask for, and alternative methods. Its key finding (Apple Search Ads' value comes almost entirely from June–July signups) changed a Q3 recommendation.

The full prompt history is in [`prompt_history/`](prompt_history/).

## Repository structure

```
index.html            the final deck (GitHub Pages serves this)
assignment/           the brief (read_me.md) and data dictionary
data/                 placeholder: the Groww CSVs are not published (see data/README.md)
analysis/             analysis scripts used in the final session (Q4 + deck numbers)
agents/               the QC agent and stakeholder-reviewer definitions, and the QC agent's own scripts
notes/                handoff summary of the earlier session (Q1–Q3 work, decisions and QC log)
prompt_history/       exported chat transcripts
```

## Reproducing the numbers

Requires Python 3 with pandas and numpy, and the six assignment CSVs placed in `data/` (they are not published here). Run from the repo root:

```bash
pip install pandas numpy
python analysis/base.py            # rebuilds the revenue table (saves analysis/rev_orders.pkl)
python analysis/deck_pareto.py     # Q1 90-day Pareto curve
python analysis/q4_mtf_overlap.py  # Q4 checks
python agents/qc_scripts/b30.py    # the QC agent's final check (uses agents/qc_scripts/qc_base.py)
```

Scripts for Q1–Q3 were written in an earlier session and are not in this repo; their results, definitions and QC log are recorded in `notes/handoff_summary.md`.
