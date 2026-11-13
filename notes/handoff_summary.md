# Groww BA/SBA Assignment — Full Handoff Summary (as of 13 Nov 2026)

Paste or attach this into a new chat to continue. Everything agreed, computed, QC-verified and still open is below. Companion project docs (same content in more detail): `claude/data_notes.md`, `claude/q1_decisions.md`, `claude/hv_definition_comparison.md`, `claude/q2_watchlist.md`, `claude/q3_channels.md`, `claude/q4_concentration.md`.

---

## 0. How we've been working (keep doing this)
- **Role:** act as an analytics head at Groww; analytical + finance mindset; **don't make assumptions without asking**.
- **Style Utkarsh wants:** plain, simple language (he asked several times to "explain better/simplify"); compact structured answers with concrete examples; direct answers; source-verified; precise.
- **QC agent:** a background agent independently recomputes every number from the raw CSVs (own code, never the analyst's scripts) and checks formula/method logic; marks MATCH / MINOR / MISMATCH / LOGIC ISSUE / UNVERIFIABLE. After every answer with numbers, send the numbers to the QC agent and relay its findings. 21 batches run so far; zero outright wrong numbers, but many method/wording corrections (all applied below). **In a new chat, re-create the QC agent** with the same instructions.
- **Data files must be re-uploaded in the new chat** (users.csv, stocks_orders.csv, fno_orders.csv, mf_orders.csv, ipo_orders.csv, commodity_orders.csv, data_dictionary.md, read_me.md). Working scripts/outputs from this chat will not carry over.
- **Output format for the final deliverable: NOT yet decided** (slide deck vs document vs HTML page). Slide-style plans exist for Q1 and Q2 (below). Max 10 pages total. AI prompt history must be submitted with the assignment.

## 1. The assignment (read_me.md)
Groww BA / Senior BA hiring assignment. Data: users.csv + order tables (stocks, F&O, MF, IPO, commodity), joined on `third_party_id`. Signups Apr–Sep 2026; orders to 31 Oct 2026. Output any format, ≤10 pages, approach clearly explained; AI allowed but full prompt history must be submitted.
- **Q1 Who is worth focusing on?** Retention can focus on a small slice. Define "high value" (no single right answer, wrong answers exist), show with evidence how HV differ, end with the 2–3 differences strong enough to act on.
- **Q2 The watchlist.** Each week pick ~20 newly signed-up users using only their first 7 days, so the most of them turn out high value (Q1 definition) by day 90. Value can change over time.
- **Q3 Where should the next marketing rupee go?** Which acquisition channels get more / less budget.
- **Q4 Revenue concentration and the next bet.** How concentrated is revenue, and what's the next bet if that source shrank significantly?

## 2. Data structure
Star schema: users.csv (one row per user) + 5 order tables (one row per order), joined many-to-one on `third_party_id`. 0 orphan IDs, 0 duplicate order IDs, 0 orders before signup.

| Table | Rows | Users | Revenue column | Counts as revenue when |
|---|---|---|---|---|
| users | 20,000 | 20,000 | — | — |
| fno_orders | 59,464 | 411 | `brokerage_inr` flat ₹20 | EXECUTED |
| stocks_orders | 34,469 | 1,965 | `original_brokerage` (actual) | SUCCESS |
| commodity_orders | 6,260 | 101 | `brokerage_inr` flat ₹20 | EXECUTED |
| mf_orders | 8,693 | 1,177 | `brokerage_inr` flat ₹2 (incl. 362 redemptions) | COMPLETED |
| ipo_orders | 11,302 | 1,272 | `brokerage_inr` flat ₹1 | successfully applied (brokerage_inr>0) |

- Signups 1 Apr–30 Sep 2026 (Apr 3,064; May 2,841; Jun 3,044; Jul 3,554; Aug 4,079; Sep 3,418). Orders 1 Apr–31 Oct 2026 (Oct is a complete month).
- users.csv: demographics (age/gender/income/occupation 51–65% blank; kyc_tier '-' 61%; 1,331 blank signup_platform; ages 2–90, 21 under 18), acquisition (33 channels, 103 subchannels; organic 7,477, google adwords 6,795), onboarding timestamps (bank added 8,432; e-sign 6,331; stock onboarded 6,293; first investment fid_ts 2,423), fid_product (cnc 1,155, sip 660, mis 250, lumpsum 156, fno 154).
- F&O: 59,404 options rows; NIFTY+SENSEX 89% of F&O orders; P&L only on executed entry rows (19,150), no double count; P&L is GROSS (before brokerage/charges); `avg_fill_price` is in paise (÷100).
- Revenue excludes `charges` (pass-through statutory/exchange fees).
- Total revenue Apr–Oct (with stock fix): **₹14,62,798** — F&O 70.7%, stocks 20.4%, commodity 7.4%, MF 0.8%, IPO 0.6%. Revenue per revenue user: F&O ₹3,682 (281), commodity ₹1,252 (87), stocks ≈₹161 (1,847), MF ₹13.6 (910), IPO ₹7.5 (1,190). ~₹73 per signup overall. 3,107 users earned any revenue.

## 3. Data quality issues & AGREED treatments
1. **Stock brokerage blanks:** 7,880 of 27,267 SUCCESS stock orders (29%) have blank brokerage (≈50% of Sep, 78% of Oct). `charges` is blank on exactly the same rows → data gap, not free trades.
   - **Agreed rule (Utkarsh):** non-SUCCESS orders (CANCELLED/REJECTED/FAILED/OTHERS, 7,202 — all blank) = ₹0. SUCCESS + blank = impute. SUCCESS + recorded ₹0 (7 orders, all a user's 11th+ order, charges populated) = keep ₹0.
   - **Pricing rule:** CNC/MIS = min(₹20, max(₹5, 0.1%×turnover), 2.5%×turnover); MTF = 0.1%×turnover, uncapped. Matches recorded fees on 99.95% CNC, 99.91% MIS, 100% MTF (±₹0.5). (First version without the 2.5% term only matched 76–81% — QC caught it.)
   - **Source:** derived from the data and confirmed by Groww's help centre ("₹20 or 0.1% of trade value per order, whichever is lower… if less than ₹5, the minimum charge will be the lower of ₹5 or 2.5% of your trade value"); SEBI caps brokerage at 2.5%; Groww pricing page: MTF brokerage 0.1% per order + 14.95% p.a. interest on funded amount. F&O flat ₹20 also matches Groww's published pricing. Caveat: Groww pages show today's pricing; the 99.9% match is the evidence for Apr–Oct.
   - Imputed stock revenue ₹2,97,848 (vs ₹1,96,929 raw).
   - **Pattern check (user asked):** blanks are NOT linked to any user attribute (occupation, channel, bank, age, income, tier, gender, KRA) or order type; they occur in **processing time windows from 2 Sep 2026** (e.g., blank before ~13:00 on 7/10 Sep, after 13:00 on 28 Sep). Logistic AUC: features 0.59, 30-min window 0.972, window+features 0.972. Slide wording: "Blank fees come from a data-recording gap in certain time windows from 2 Sep; neither user nor order type explains them; filled using Groww's pricing rule (matches 99.9%)."
   - **No free-brokerage period for new users** (user asked): first orders/first days match the rule 100%; low day-0 fees are small orders (median ₹116). Only testable for stocks; F&O/commodity/MF/IPO fees are flat assumptions; off-order cashback wouldn't appear.
2. **fid_ts** blank for 700 revenue users (517 IPO-only — expected, FID excludes IPO; 183 non-IPO, 160 stocks) → derive first trade from orders. 7 users have fid_product='ipo'.
3. **Right-censoring:** only signups ≤ 2 Aug 2026 (12,734 users) have a full 90 days → the cohort for all D90 analysis.
4. **kra_flag:** dictionary says kra_not_checked = "KYC pre-existing with another broker", but data shows those 5,493 users mostly never reached KYC (98% blank demographics, 1% onboarded). Compare KRA only among onboarded users. kra_flag has no timestamp — assumed known by day 7.
5. Channel field mixes groups with partner IDs (regrouped, see Q3). signup_platform uses 'desktop' not 'web'. No CAC/spend data anywhere (confirmed by Utkarsh: none available).

## 4. Exploratory work (done before the questions)
### Monthly signup cohorts (M1 = days 0–29, M2 = 30–59, M3 = 60–89 after signup; retained = ≥1 successful order)
| Signup month | Apr | May | Jun | Jul | Aug | Sep |
|---|---|---|---|---|---|---|
| Signups | 3,064 | 2,841 | 3,044 | 3,554 | 4,079 | 3,418 |
| M1 / M2 / M3 retention | 8.7/6.5/5.6% | 10.2/6.8/6.1% | 10.8/7.6/7.3% | 12.7/9.2/8.7% | 17.8/11.4/– | 13.5/–/– |
| M1 actives still active M2 / M3 | 56/45% | 56/48% | 57/48% | 59/53% | 56/– | – |
| Revenue M1 / M2 / M3 (₹k) | 52.9/72.5/37.8 | 63.8/43.6/24.7 | 105.2/77.4/68.7 | 80.0/61.0/70.9 | 52.1/74.4/– | 93.7 |
- Any-order-placed retention is 1–2 pts higher; same picture.
- Pooled Apr–Jul by instrument, M3 vs M1 revenue: F&O −37%, commodity −42%, stocks −19%, MF −16%, IPO +25%; total ₹3.02L → ₹2.55L → ₹2.02L (−33%).
- QC corrections: Aug's high M1 retention is IPO-only users (313 of 725; without them 10.1%), but Aug's low ₹/signup is weak F&O (₹25k vs ₹36–83k), not IPO. IPO rise is the IPO calendar (busy **Aug–Oct**: successful applications Jun 90, Jul 422, Aug 3,084, Sep 3,345, Oct 2,032). Rising stock revenue per remaining user (₹82→₹143) is partly survivorship ("heavier traders stay"). ~3–4% of "MF active" users only redeemed. F&O cohort cells driven by 17–40 users (top user 13–46%).

### Pareto (all months Apr–Oct, F&O + stocks + commodity = ₹14.41L, 1,987 users)
| Revenue mark | Users | % of revenue users | % of 20k signups | Smallest user |
|---|---|---|---|---|
| 50% | 33 | 1.7% | 0.17% | ₹10,781 |
| 80% | 107 | 5.4% | 0.53% | ₹3,083 |
| 90% | 181 | 9.1% | 0.91% | ₹1,044 |
| 95% | 297 | 14.9% | 1.49% | ₹340 |
| 99% | 883 | 44.4% | 4.42% | ₹34 |
- Top 10 users = 25%; top user ₹67k (4.7%). F&O = 79% of the top-107 group's revenue.
- Time concentration (top 107): spread across days (median 33 trading days; top day ≈12%; best 7 days ≈33%) but in month-long spells: **best 30-day stretch median 74%; 76% earn ≥50% in one 30-day stretch** (QC corrected from calendar-month 58%/65%). "Steady/burst" patterns only valid for users with ≥90 days history (80 of 107: 37 steady / 33 in between / 10 burst).
- October check: 29 of 107 top users had zero October revenue ("inactive in October", not "churned" — 19 had earlier 31+ day gaps).

## 5. Q1 — Who is worth focusing on (AGREED)
### Definition (primary, agreed)
**High value (HV) = top ~1% of users by all trading revenue (F&O + stocks + commodity; MF/IPO add ₹0 here) in the first 90 days after signup (bar ₹733.8), AND ≥1 revenue-earning order in days 60–89 (month 3).**
- Cohort 12,734 (signups ≤ 2 Aug). **94 HV users (0.74% of signups) = 69.5% of 90-day revenue.** Mix F&O 72%, stocks 19%, commodity 9%. Main instrument F&O 63, stocks 27, commodity 4.
- On the 90-day Pareto curve the ₹734 bar (top 1% = 127 users) sits at ≈ the **90% revenue mark**; the activity rule splits them into 94 HV (69.5%) + 33 lapsed (20.5%).
- Use wording "days 60–89 / month 3" (calculation is 60 ≤ d < 90), not "61–90".
- Proof activity rule works: 80% of HV earned again after day 90 vs 24% of lapsed (fixed window days 90–120: 77.6% vs 18.5%).
- **Why not F&O-only (state on slide):** F&O-only filter = 61 users / 55.9% of revenue, drops 33 of 94 HV (35%) and 19.5% of HV revenue — mostly active intraday/MTF stock traders (median 116 orders/90 days; MIS 56%, MTF 25%). Holds at ₹500 (38%/19.8%) and ₹1,000 (35%/19.7%) bars. **Fallback:** if retention can target only one instrument, use F&O-only (61 users, 56%).
- **Wrong definitions to call out:** MF money invested (₹2/order), number of orders or IPO applications (₹1 counts like ₹20), top 5% (bar only ≈₹30), one busy week.

### Lapsed top earners (exact definition, show on slide 3)
Signed up ≤ 2 Aug; ≥ ₹733.8 in days 0–89; NO revenue-earning successful order in any instrument in days 60–89 (cancelled/rejected don't count). 33 users, 20.5% of 90-day revenue; 25 mainly F&O; median last revenue order ≈ day 41; ~1 in 4 earned again after day 90. Of 33: 8 never traded F&O (7 stocks-only, 1 commodity-only); 7 of the 25 F&O users did all F&O inside their final 14 days.

### Alternative definitions tested (keep current) — appendix table
Fair comparison = days 90–120 window, users with ≥30 days observed after day 90. Base: 6.3% of all users earn in days 90–120.
| # | Definition | Users | % 90d revenue | Still earning d90–120 | Median ₹ | Avg ₹ |
|---|---|---|---|---|---|---|
| 0 | **Current: top 1% + active month 3** | 94 | 69.5% | 52 of 67 (78%) | 480 | 1,573 |
| 1 | Top 1%, no activity rule | 127 | 90.0% | 57 of 94 (61%) | 62 | 1,135 |
| 2 | Pareto 80% of 90d revenue | 71 | 80.2% | 33 of 53 (62%) | 480 | 1,832 |
| 3 | ≥₹1,000 + active m3 | 81 | 68.0% | 43 of 58 (74%) | 417 | 1,735 |
| 4 | Top 1% by month-3 revenue | 127 | 69.4% | 74 of 97 (76%) | 220 | 1,190 |
| 5 | Revenue in all 3 months, top 1% among them | 127 | 63.0% | 72 of 88 (82%) | 120 | 1,048 |
| 6 | ≥20 trading days + ≥₹300 | 94 | 75.0% | 48 of 70 (69%) | 242 | 1,219 |
| 7 | ≥2 instruments + ≥₹500 | 88 | 61.0% | 43 of 66 (65%) | 62 | 1,017 |
| 8 | Current minus F&O users losing >₹5 per ₹1 brokerage | 65 | 52.0% | 36 of 44 (82%) | 564 | 1,943 |
| 9 | Top 1% + active month 1 | 115 | 84.7% | 52 of 85 (61%) | 61 | 1,178 |
| 10 | Top 1% + active month 2 | 106 | 81.4% | 51 of 80 (64%) | 117 | 1,134 |
| 11 | Top 1% + active months 2 and 3 | 83 | 64.1% | 48 of 60 (80%) | 500 | 1,491 |
| 12 | Top 1% + active all 3 months | 78 | 60.8% | 45 of 55 (82%) | 560 | 1,570 |
Notes: rules requiring month-3 activity win on persistence partly by construction; revenue-ranked definitions win on "% revenue" by construction. Recency (month 3) drives persistence; month-1 rule ≈ no rule; stricter rules' gains not significant (p=0.12–0.18) and cost 5–9 pts revenue. 12 top earners weren't active in month 1; **7 of 94 HV only started after day 60** (uncatchable by a day-7 list). Finance point for Q4: ~a quarter of HV revenue (69.5%→52.0%) comes from F&O users losing >₹5 per ₹1 brokerage. Not measurable: MF AUM/trail, MTF interest, cost/margin. Slide line: "Tested 8 alternatives; ours keeps 70% of revenue and is tied-best on revenue in the following month."

### Slide 3 — economics of HV vs rest (90-day window; HV / lapsed / other revenue users / avg signup)
- **Avg monthly revenue ₹1,888 / ₹1,585 / ₹17 / ₹20 (≈94× avg signup).** Revenue per order ₹19.6 / ₹19.7 / ₹4.9.
- Active M1 87% / 100% / 81% / 11%; M2 88% / 70% / 56% / 8%; M3 not shown (true by definition). Earns after day 90: 80% / 24% / 47% / 8%.
- Orders in 90 days 290 / 241 / 10 / 4; trading days 27 / 18 / 3 / 4; products used 2.0 / 1.6 / 1.3.
- Median stock turnover (stock traders) ₹7.7L / ₹5.2L / ₹3.4k. MTF users 13% / 12% / 3%.
- HV F&O users: median gross loss ₹3.5 per ₹1 brokerage, 84% net losers, −₹26.4L gross in 90 days. (Lapsed total P&L looks positive only due to one +₹6.2L user — don't show.)
- Margin-related share of F&O rejections (90-day): 81% / 96% / 87%.
- First revenue in week 1: 62% / 79% / 58% — not a differentiator.
- **Demographics (small strip):** no strong signature (age 30 vs 28; income ≥₹5L 24% vs 19%; city tier/channel ≈ same). KYC registry: 62% of HV vs 41% of onboarded users; HV rate among onboarded 3.7% (kra_verified) vs 1.5% → "already in KYC registry → 2.4× more likely HV".
- **2–3 differences to act on:** (1) they trade often and steadily (290 orders, 27 trading days, ~₹20/order); (2) multi-product incl. margin (13% use MTF vs 3%) → cross-sell; (3) heavy trading intensity as a risk marker (see below).

### Why did lapsed users stop? (tested; final conclusions)
- **Out of capital — NOT supported:** 0 of 33 placed ANY order (all 5 products, any status) in days 60–89 → they stopped, weren't blocked; margin rejections in last 10 derivative orders 7.3% vs 7.4% earlier (HV same flat pattern); commodity "Available margin" remarks: only 5 lapsed users, inconclusive (all their rejections days 11–30). The phrase "many are likely out of capital" was an un-tested inference and was dropped — don't use it.
- Final-14-day P&L (fair windows ending at last executed trade): lapsed −₹3,580 (80% negative) vs HV −₹1,432 (71%), p=0.16 — not significant (first biased version p=0.015 rejected). Lapsed median P&L before that spell ≈ ₹0.
- **Losing streak — NO robust evidence:** win rate final 14 days 45% vs HV own final weeks 49% (p=0.51); no drop vs own earlier (same 18 users 54%→44%, p=0.44); vs HV same dates looked significant but HV is survivor-biased; vs all non-lapsed F&O traders same dates 45% vs 46–50% (ns). Streaks: slightly longer than chance but ~half mechanical; fails multiple-testing (Holm) correction.
- **AGREED slide comparison (Utkarsh's choice): Group 1 (lapsed last 2 weeks, 25 F&O users) vs Group 3 (HV on the same calendar dates, median HV user per window):**
  | Metric | Lapsed last 2 wks | HV same dates | p | Holm (4 tests) |
  |---|---|---|---|---|
  | Win rate | 45% | 53% | 0.039 | fails |
  | Avg P&L per trade | −₹163 | −₹82 | 0.49 | fails |
  | Trades per trading day | 6.7 | 3.4 | 0.006 | passes |
  | Avg losing streak | 2.6 | 1.8 | <0.001 | passes |
  Caveats: win-rate gap depends on peer choice (HV survivor bias); streak gap ≈ half mechanical (residual p=0.076); trades/day robust only vs the median HV user (vs mean 5.8/day p=0.38; lapsed sit ~70th–77th percentile of traders on same dates → "heavy, not outliers"). Lapsed didn't speed up at the end (same 18 users 5.5 vs 5.5 trades/day). Extended table also had "lapsed before 2 weeks" (18 users: win 54%, avg loss −₹1,205, 5.5 trades/day, streak 2.5) and all non-lapsed traders (~46–50%, −₹860, 2.8/day, 1.8).
  Slide line: "In their final fortnight, lapsed top earners traded more per day and lost slightly more often than HV users on the same dates — heavy traders but not outliers; the win-rate gap isn't conclusive with 25 users. They didn't get blocked; they stopped placing orders altogether. Why isn't visible in this data (no balance/withdrawal records)." Never claim "out of capital" or "losing streak".
- Only 18 of 33 have a "before" period because 8 never traded F&O (no P&L data) and 7 did all F&O in the final 14 days.

### Retention focus (agreed; state on slide 3)
- **Primary focus: HV users showing early signs of slipping** (prevention — catch them while still in the 94; ~₹1.8L/month at stake; ~1 in 5 HV still stop after day 90).
- **Lapsed: lighter, low-cost automated win-back** (reminders/offers), not personal attention.
- Early-warning signals: trading drops well below own recent peak (not yet validated); heavy trading intensity (a trait from the start, borderline-robust). "Run of losses" NOT supported. Retention should mean better tools/education/risk controls, not "trade more" (they lose ₹3.5 per ₹1 brokerage). No campaign data → priority based on revenue size and natural return rates.

### Q1 slide plan (3 of 10 slides)
- Slide 1 "Fewer than 1 in 100 signups bring 90% of trading revenue" — Pareto curve + marks table.
- Slide 2 Definition + "why not F&O-only" + fallback + wrong definitions; lapsed definition.
- Slide 3 Economics table (+ small demographics strip) + 2–3 actionable differences + retention focus + lapsed comparison line.
- Appendix: revenue measurement, stock-fee gap & pricing rule, QC method, alternative-definitions table, methodology lessons.

## 6. Q2 — Weekly watchlist (scorecard CHOSEN)
### Framing
- Target fixed by the brief = HV (Q1 definition) by day 90; report D90 revenue held by picks and lapsed picked alongside.
- Signup weeks Mon–Sun; 18 weeks with full data; **HV per week 2–10, mean 5.2** → a perfect 20-pick list catches ~5 (max ≈26% precision). Goal: "catch as many of the week's HV as possible."
- Features only known by day 7 (orders 0≤d<7, onboarding timestamps <168h, FID if within 7d, kra_flag, kyc_at_signup, platform, channel, demographics only if e-signed by day 7). Excluded: current kyc_status, digilocker_status, fid_product, bank_name. Leakage audit clean; minor: 228 MF/IPO day-7 rows (₹383) completed after day 7.
- Validation: leave-one-week-out (points learned without that week) + strict test (train only on matured labels; last 5 weeks).

### Results
| Method | HV caught (of 94) | Share | Lapsed picked | 90d revenue held |
|---|---|---|---|---|
| A. Top 20 by week-1 revenue | 50 (49–51 by ties) | 53% | 25 | 57% |
| **B. Points scorecard (chosen)** | 52 (52–54 by ties; upper bound) | 55% | 23 | 59% |
| C1. Logistic, all features | 45 | 48% | 24 | 58% |
| C2. Gradient boosting | 48 (45–49 by seed) | 51% | 24 | 59% |
Strict test (30 HV): A 13, B 11, C1 6, C2 5. Random = 0.15 hits/week; scorecard ≈2.9/week (~19× random). B vs A within noise → fair claim "as good as ranking by revenue, and explainable". Hits per week: 0,1,2,5,2,3,2,3,5,2,7,4,4,1,2,7,2,0.
- Hits sit in the top 10 slots: slots 1–5 hit 34%, 6–10 17%, 11–15 3.3%, 16–20 1.1% (46 of 50 hits in top 10).
- Silent HV: 36 of 94 earn nothing in week 1 (33 place no order); rankable (83% had stock account set up by day 7 vs 20%) but too rare (0.31% base rate); no zero-revenue user scores above 7.

### How the scorecard was built ("back-engineered from the characteristics of HV users")
1) 10 yes/no week-1 signals from Q1 findings; 2) check each alone; 3) logistic regression (C=1) weighs them together (no double counting); 4) points = weight×2, rounded (each point ≈1.65× odds; rank corr 0.9998 with raw); 5) tested as above; points stable ±1 across 18 refits (stock setup always +5). Freeze one set of points for deployment.
| Week-1 signal | Users | % of HV with it | % of others | Chance of HV: with / without | Weight | Odds× | Points |
|---|---|---|---|---|---|---|---|
| Stock account set up | 3,300 | 94% | 25.4% | 2.7% / 0.06% | 2.49 | 12.0 | **+5** |
| Earned ₹200+ | 55 | 24% | 0.3% | 42% / 0.6% | 1.27 | 3.6 | +3 |
| Earned ₹50–200 | 90 | 21% | 0.6% | 22% / 0.6% | 0.88 | 2.4 | +2 |
| Traded F&O | 81 | 30% | 0.4% | 35% / 0.5% | 0.78 | 2.2 | +2 |
| Traded on 2+ days | 335 | 50% | 2.3% | 14% / 0.4% | 0.81 | 2.3 | +2 |
| Revenue on days 3–6 | 550 | 56% | 3.9% | 9.6% / 0.3% | 1.19 | 3.3 | +2 |
| KYC registry | 2,927 | 62% | 22.7% | 2.0% / 0.4% | 0.86 | 2.4 | +2 |
| Earned only ₹1–50 | 830 | 16% | 6.4% | 1.8% / 0.7% | −0.68 | 0.5 | −1 |
| 2+ products | 95 | 15% | 0.6% | 14.7% / 0.6% | 0.00 | 1.0 | 0 |
| Intraday / margin | 181 | 15% | 1.3% | 7.7% / 0.6% | −0.16 | 0.9 | 0 |
Base rate 0.74%. Column label for slides: "Chance of becoming HV: with this signal / without it". Caveat: ₹1–50 carries little signal; the −1 only partly offsets activity points → scorecard slightly overrates small-ticket multi-day traders (predicted ~7% vs observed ~2%). Optional fix: ₹1–50 = −2, or activity points only if week-1 revenue ≥ ₹50 (not decided). Max score 16.

### Tiers (corrected: "≥10 = clear calls" was withdrawn)
| Score | Users/week | Share becoming HV (LOWO / in-sample) | Use |
|---|---|---|---|
| ≥13 | ~4–5 | ~32% / 37% | Must-pick (≈1 in 3; also ≈1 in 3 are future lapsed heavy starters → retention priority) |
| 10–12 | ~5 | ~20% / 12% | Likely |
| ≤9 (fill to 20) | ~10 | ~3% | Filler |
Weekly use: score on day 7, take top 20 by score, ties → higher week-1 revenue. The 20th pick usually scores 8 (7–9). ≥10 group 5–15/week, never >20.

### Where the 360 picks land (90-day revenue Pareto of the 12,734 cohort)
| Bracket | 90d revenue | Users in bracket | Picks | HV | Lapsed | % of picks | Share of bracket picked |
|---|---|---|---|---|---|---|---|
| Top→50% | ₹9,260–40,880 | 23 | 14 | 9 | 5 | 4% | 61% |
| 50–75% | ₹3,296–9,110 | 33 | 23 | 16 | 7 | 6% | 70% |
| 75–80% | ₹2,540–3,252 | 14 | 7 | 6 | 1 | 2% | 50% |
| 80–90% | ₹734–2,501 | 57 | 31 | 21 | 10 | 9% | 54% |
| 90–95% (near miss) | ₹194–725 | 101 | 54 | 0 | 0 | 15% | 53% |
| 95–99% | ₹22–192 | 500 | 137 | 0 | 0 | 38% | 27% |
| 99–100% | ₹0.3–22 | 945 | 87 | 0 | 0 | 24% | 9% |
| No revenue | ₹0 | 11,061 | 7 | 0 | 0 | 2% | 0.1% |
≤90% brackets = exactly the top 1% (127); picks hold 75 (59%) = 52 HV + 23 lapsed. Picks hold 58.6% of 90-day revenue: **₹1,247 per pick vs ₹60 per average user (≈21×)**. Slide line: "Of every 20 users we pick, about 4 become top-1% earners and 3 more just miss the bar; a pick is worth ~21× a typical new user."

### Example week (6–12 July: 823 signups, 6 HV) — 2 hits: slot 1 (score 14, ₹600 week-1, 30 F&O trades → HV ₹9,420) and slot 7 (score 10, ₹315 → HV ₹1,227); slot 3 (score 14) became a lapsed top earner; slots 11–20 scored 8–9, ₹2–25 week-1.

### Q2 slide plan (2 slides)
- Slide 4 "How we pick 20 a week": constraint (~5 HV/week), points table + tiers, results (~52 of 94, ~19× random, 59% of revenue), why scorecard not model, how it was back-engineered (signal table).
- Slide 5 "What it can't do & how to use it": top 10 slots carry the hits; silent HV & 7 late starters; 1/3 of 13+ tier are future lapsed → retention attention; landing-bracket table; example week.

### Q2 open items
- Fill rule for tied last slots (8 of 360 picks effectively random, 7 of them = the "no revenue" row): add tie-breaks (more week-1 orders, then earliest stock-account setup) or leave to team judgement — not decided.
- Optional ₹1–50 fix — not decided.
- Slots 11–20 as a test group to measure whether personal attention works — not decided.
- Day-14/30 second scoring for silent users (beyond brief) — not decided.
- Optional: do near-miss picks grow into HV after day 90? — offered, not run.

## 7. Q3 — Where the next marketing rupee goes (FINAL tiers)
- Cohort 12,734; metric = 90-day revenue per signup (+ HV rate, % earning anything, first investment ≤90d). Utkarsh: metrics in the table are good; **no CAC/spend data** → value per signup = break-even ceiling, not ROI. Rule: "Shift budget only where a channel costs less per signup than it earns in 90 days."
- **Grouping (verified online):** OfferDeck is a Vserv product → merged; Jampp (mobile DSP, Affle-owned) and Mobavenue (Indian programmatic DSP/SSP) → Programmatic with Moloco (mobile DSP) and DV360 (Google DSP); NDTV Convergence = NDTV's digital arm → publisher; publishers reported individually; Appnext = app-install/CPI network (Adzinsight, Marvelofin, Radian, FuelMyApp not verifiable online — inferred). Label Programmatic without InMobi (its 1 user sits in "Ad partner other"). "affiliate" subchannels look like internal pages; "navi" cross-promo.

| Channel | Signups | ₹/signup (90d) | Without top user | Top user's share | HV | % earning |
|---|---|---|---|---|---|---|
| Apple Search Ads | 141 | 384 | 230 (155 w/o top 2) | 41% | 6 | 24% |
| News Nation | 70 | 131 | 25 | 81% | 2 | 17% |
| Referral | 61 | 125 | 62 (26 w/o top 3) | 51% | 1 | 44% |
| HT | 516 | 124 | 77 | 38% | 6 | 17% |
| Zee | 339 | 103 | 70 | 33% | 4 | 17% |
| Ad partner: other | 88 | 92 | 12 | 87% | 1 | 11% |
| Programmatic / DSPs | 408 | 77 | 23 | 70% | 2 | 16% |
| Web / mobile site | 563 | 73 | 40 | 45% | 4 | 9% |
| Others | 54 | 67 | 21 | 69% | 2 | 19% |
| Vserv (incl. OfferDeck) | 384 | 60 | 26 | 57% | 2 | 14% |
| Google Ads | 4,250 | 53 | 48 | 10% | 31 | 15% |
| Organic | 4,760 | 52 | 44 | 16% | 31 | 11% |
| Social (Snapchat, X) | 82 | 30 | 23 | 24% | 0 | 29% |
| Times Internet | 80 | 21 | 6 | 73% | 1 | 10% |
| NDTV | 534 | 10 | 5 | 47% | 1 | 15% |
| App-install / affiliate networks | 404 | 10 | 3 | 71% | 0 | 7% |
Overall ₹60/signup, HV 0.74%. 30-day revenue on all 20,000 signups confirms order (ASA 127, Referral 83, Media 31, Organic 23, Google 21, NDTV 8, networks 12). Google: main campaign (uac_android_v3_all_fid_troas, 3,642 users) ₹60 with 30 of Google's 31 HV; other campaigns ₹1–19 (~560 users, 1 HV) incl. F&O-targeted fno_3transaction ₹6 (0 HV).
- **ASA:** +₹332/signup vs Organic (90% CI +60 to +650); HV 4.26% vs 0.65% (p=0.001); median earner ₹46 vs ₹18.6; not an iOS effect (other iOS ₹14–18). Strong but concentrated (top 3 = 78%).
- **HT/Zee:** % earning 17% vs 11% (p<0.001); trimmed top-1% ₹10.6/₹9.0 vs Organic ₹4.6 (~2×); HV lift not significant (p=0.17/0.29); ₹ gap CIs include zero. Wording: "More users start trading (17% vs 11%, significant), and revenue per signup is roughly 2× Organic after trimming outliers. The HV-rate lift is not significant at this size; scale up gradually and keep measuring."
- **Final tiers:** MORE (robust): **Apple Search Ads** (worth up to ~₹155–385/signup; scale stepwise). MORE gradually & measure: **HT, Zee, Referral** (activation). HOLD: **Google main campaign**. UNCLEAR (whale-driven): News Nation, Vserv+OfferDeck, Programmatic (at most capped Moloco iOS test), Ad partner other, Social, Others, Web. LESS: **NDTV, Times Internet, app-install networks, small Google sub-campaigns**.

## 8. Q4 — Concentration & the next bet (DRAFT, QC-verified)
- Decisions (Utkarsh): stress-test **F&O as a whole** (SEBI rules apply to instruments, not specific indices); **30% shrink**; use online SEBI context.
- **SEBI context (sources checked):** 1 Oct 2024 circular, six measures (contract size ₹15–20L, one weekly expiry per exchange, extra expiry-day margin from 20 Nov 2024; upfront premium and no calendar-spread benefit on expiry from 1 Feb 2025; intraday position-limit monitoring from 1 Apr 2025). FY25: 91% of individual F&O traders lost money; unique traders 61.4L (Q1) → 42.7L (Q4). FY26: SEBI annual report — options volumes down >50%; higher STT (futures 0.05%, options premium 0.15%); 87.7% of individual traders loss-making. SEBI chair (Feb 2026): no near-term new curbs; June 2026: exploring longer-term contracts. → 30% is realistic, not extreme.
- **Concentration (Apr–Oct, ₹14.63L, 3,107 revenue users):** F&O 70.7% (HHI 5,474; F&O share by month 55–75%). Top 10 users 24.9%, top 50 60.1%, top 100 77.4%, top 200 90.0%. Inside F&O (₹10.35L, 281 users): index options 92.9% (NIFTY 64%, SENSEX 26%, BANKNIFTY 2%); expiry-day orders 36%; top 10 F&O users 33%, top 30 57%. **Hidden dependence:** 95% of commodity revenue and 33% of stock revenue come from F&O users → "F&O trader" pocket ≈ 84% of revenue. F&O traders: 79% of those with recorded P&L are net losers (211/267); gross loss ₹38.5L ≈ ₹3.7 per ₹1 brokerage.
- **Stress (F&O −30%) = −21% to −25% of total revenue:** everyone trades 30% less −₹3.10L (−21%); top 9 F&O traders (30.6% of F&O) leave −₹3.32L (−23%); spread-out exit taking other products −₹3.71L (−25%). HV: 88 of 94 still above bar; HV revenue −22%.
- **Candidate bets (sized from data):**
  | Bet | Base today | ₹/user | To replace ₹3.1L |
  |---|---|---|---|
  | MTF | 94 users, ₹53k (43% imputed fees); 4.6% of 1,707 delivery traders use it | ₹567 brokerage (+14.95% p.a. interest not in data) | ~550 MTF users (≈1 in 3 delivery traders), brokerage only |
  | Deeper stock trading (non-F&O traders) | 1,701 users, ₹2.0L | ₹118 (median ₹20) | +₹182/user (≈2.5×) |
  | Activation | 3,187 onboarded never earned anything (4,446 never earned from stocks) | — | 10% activating adds ₹6–53k |
  | IPO-only → trading | 474 users (56% of IPO users already trade) | — | 10% converting adds ₹1–6k |
  | Commodity | 87 users | ₹1,252 | Not a hedge — 95% from F&O users |
  | Mutual funds | 910 users | ₹13.6 | Too small in this data |
- **Draft answer:** no single bet replaces a 30% F&O drop (revenue is effectively one bet on retail derivatives traders). **Next bet = MTF** (highest ₹/user + interest, low adoption, moves traders toward stocks which F&O rules don't touch); **broadest support = deeper stock trading** among non-F&O traders; activation/IPO conversion small; commodity same pocket.
- **OPEN DECISION:** MTF interest — (a) estimate with clearly labelled assumptions (funded share, average holding days) as a sensitivity range, or (b) keep qualitative "extra upside, not counted".

## 9. Methodology lessons (appendix material)
Compare like with like (windows must contain activity for both groups); use per-user medians, not pooled rates; adjust streaks for trade counts; never pick a comparison group based on the outcome (HV = stayed active → survivor bias); treat overlapping windows as non-independent; check median vs mean peers; use fixed observation windows, not per-day rates over unequal periods; correct for multiple tests on small n; break ties deterministically; whale-check channel/cohort averages; state imputation shares.

## 10. Open decisions & next steps
1. Q4: MTF interest — estimate (a) or qualitative (b).
2. Q2: tie-break/fill rule; optional ₹1–50 fix; slots 11–20 test group; day-14/30 second look; near-miss growth check.
3. Final output format (slide deck / doc / HTML) and page allocation (proposed: Summary 1 · Q1 2–3 · Q2 4–5 · Q3 6–7 · Q4 8–9 · Data & assumptions 10).
4. Build the final deliverable; keep QC checks on every number; prepare prompt-history export for submission.