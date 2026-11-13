# Senior stakeholder reviewer

**Role:** an agent playing a senior analytics stakeholder at Groww (Head of Analytics level, finance and product sense, experienced hiring panellist). It reviewed the draft deck and sent improvement suggestions back to the main analysis. It did not edit any files.

## Instructions given to the agent

> You are a senior analytics stakeholder at Groww. A candidate's BA / Senior BA hiring-assignment deck has landed on your desk. Review it and send improvement suggestions back. Do not edit any files; only read and report.
>
> Read the brief, the deck (HTML and page screenshots) and the handoff summary of what was already tested. Raw data is available for directional sanity checks only.
>
> Cover all five lenses:
> 1. **UI/UX and visual communication:** hierarchy, readability, density vs clarity, chart choice and labelling, consistency, whether each headline is the takeaway.
> 2. **Unclear methodology or numbers:** where a reader can't tell how a number was computed, which denominator, window or cohort it uses.
> 3. **Logic a senior stakeholder would challenge:** claims that overreach, causal language on correlational data, survivor bias, small n, recommendations that don't follow from the numbers.
> 4. **Detailed slices a senior stakeholder would ask for:** only ones that could change a decision.
> 5. **Where a senior stakeholder might hold a different view or method.**
>
> Output: a 3–5 line verdict; a prioritised table `# | Page | Lens | Issue | Suggested change | Priority (Must/Should/Nice) | Effort`; and 5–8 questions a hiring panel would ask. Respect the constraints: 10 content pages max, plain language, no CAC / MF AUM / MTF interest / cost data exists.

## Outcome

It returned 35 suggestions and 8 panel questions. The candidate reviewed each and chose which to apply. Applied, among others:

- **Layout:** unhid columns cut off by sideways scrolling; one sheet per page in print.
- **Q1:** medians beside averages; plain-language statistics (p-values moved to footnotes); a guardrail that F&O-heavy high-value users get risk tools and education, not trading nudges.
- **Q2:** lead with hit rate (about 3 of 20 picks) rather than "19× random"; state the forward-only test; a holdout to measure whether attention works.
- **Q3:** the Apple Search Ads month-by-month check (verified by the QC agent) that changed the call to "capped steps".
- **Q4:** a realistic and an upside case for the next bet; Part B framed as a test; a safer offer order.
