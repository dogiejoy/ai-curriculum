# Phase 4 — Package A Launch Prep

## Week 13 (24-28 Aug 2026) — Landing Page

### Day 1 (Mon 24 Aug) — Copy Draft

**Positioning confirmed**: AI Integration Service ($2,500 flat)
- NOT: Depot RTB SaaS (would require slower vet vertical sales)
- YES: Turnkey RAG for Laravel teams (agencies + product companies)

**Target buyer**: Thai/SEA Laravel dev teams with existing apps + AI need
**Depot RTB Assistant role**: portfolio proof (case study), not product for sale

### Positioning statement
"Ship AI features into your Laravel app in 2-3 weeks. Package A: complete
RAG integration. $2,500 flat fee. Depot RTB Assistant is the proof."

### Value proposition
- Who: Laravel teams (agencies, product companies, in-house dev)
- Problem: client wants AI, no in-house AI expertise
- Solution: turnkey RAG integration in 3 weeks
- Differentiator: everything measured, everything documented,
  real case study with real metrics

### Landing page structure (199-line draft)
- Hero (headline + value prop + CTA + trust bar)
- Problem (3 painful alternatives)
- Solution (6-feature grid)
- Proof (Depot RTB Assistant case study with 6 real metrics + screenshots)
- Process (3-week timeline)
- Pricing ($2,500 flat, itemized inclusion + optional retainer)
- FAQ (7 objections addressed)
- About (personal credibility)
- Final CTA (discovery call)

### Copy refinements applied
1. Hero subheadline shortened (removed jargon parenthetical)
2. Case study opens with "before/after" hook (emotional context)
3. Added "what if you disappear" FAQ (top unspoken solo-dev fear)

### Framework decision
- Static HTML/CSS on Cloudflare Pages
- Reasons: fastest ship, zero hosting cost, full control
- Migrate to Framer/Astro later when copy validated

### Deferred to Tue Day 2
- Company name decision
- Inquiries email setup
- Domain confirmation
- Design implementation
- Deploy to Cloudflare Pages

### For Wed (Day 3)
- Screenshots polish (11 existing from Week 8/10)
- Demo video record (screencast of assistant.html)
- Case study writeup deeper (dedicated case-study.md)

### Business framing lesson
Original curriculum end talked about "$99/$299/$999 tiers" (SaaS thinking)
which drifted from original Package A plan (May 2026: $2,500 flat service).
Corrected today: sell service, not product. Recurring revenue via optional
retainer, not subscriptions.

Package A economics:
- $2,500 upfront × 3 clients Year 1 = $7,500 setup revenue
- + $500-1500/mo retainers = $18-54K/yr recurring potential
- + Year 2 vertical productization option (Depot RTB SaaS later)

## Day 2 (Tue 25 ส.ค.) — Design + Deploy — SHIPPED

### Landing page LIVE
- URL: https://depot-assistant.pages.dev
- Hosted: Cloudflare Pages (free tier)
- Source: github.com/dogiejoy/depot-assistant
- Auto-deploys on git push to master

### Mid-day pivots
1. Fast path chosen (Depot Assistant name, .pages.dev subdomain, Gmail forward)
   - Rationale: momentum > perfection, first landing page ≠ forever
2. Product-first rebrand (B2): "Depot Assistant" as product name
   - Case study reframed: Depot RTB = first production deployment
   - Pricing unchanged: $2,500 install fee
   - Delivery framing: "we install our product for you"

### Cloudflare gotchas caught
- Workers vs Pages confusion (2026 UI defaults to Workers create flow)
- Correct path: create app → "Looking to deploy Pages? Get started" (bottom)
- Then: Import Git repository (not drag-drop for future updates)

### Deferred (Wed-Fri)
- Custom domain purchase (depotassistant.com or similar)
- Screenshots polish for proof section (currently text-only metrics)
- Demo video (screencast of assistant.html)
- Case study deeper writeup (dedicated case-study.md)
- Email forwarding actual setup (Gmail alias)

### Time
- Block 1 (decisions): 15 min (fast path)
- Block 2 (HTML/CSS build): 75 min
- Block 3 (deploy + rebrand mid-session): 60 min
- Total Day 2: 2.5 hours

## Day 3 (Wed 26 ส.ค.) — Screenshots + Case Study

### Shipped
1. Screenshots section on landing page:
   - 4 real product shots (dosage, cold chain, refusal, API)
   - Uniform 240px height + object-fit contain (readable + consistent)
   - Selected from Week 8 portfolio (Week 10 safety shots missing — deferred)
2. Case study page (case-study.html):
   - "Depot RTB Assistant — First Deployment" story
   - Structure: Problem → Alternatives → Approach → Results → Bugs → What ships → Next
   - Real metrics table with "how measured" column
   - "What broke" section: 4 bugs (judge, SDK positional, cache camelCase, ContextBuilder regression)
   - ~1000 words, 5-min read
3. Landing page CTA card linking to case study
4. Auto-deployed via Cloudflare Pages

### Design decision — case study over demo video
- Case study = scannable, shareable, SEO-friendly, dual-use (landing + outreach emails)
- Demo video = requires 60+ min recording + editing + hosting
- Written content = higher ROI for solo dev launch phase
- Video deferred to Phase 5 if prospects request it

### Business framing
Landing page now has:
- Real screenshots (proof at glance)
- Case study (deep dive for serious prospects)
- Metrics table (both landing + case study)
- Transparency signal ("bugs caught + fixed" section)

Case study serves triple duty:
1. Landing page proof for skeptical prospects
2. Standalone URL to paste in outreach emails
3. Content marketing (LinkedIn, forums)

### For Thu (Day 4)
Options:
- Custom domain purchase + setup (depotassistant.com)
- Screenshot polish (annotations, better crops)
- Email address setup (Gmail forwarding for hello@depotassistant.com)
- Case study CSS polish (remove gray background)

### For Fri (Day 5)
Week 13 retrospective + Week 14 (case study extension + blog) planning