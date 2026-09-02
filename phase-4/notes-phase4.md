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
- Email address setup (Gmail forwarding for depot-ai@potissolution.com)
- Case study CSS polish (remove gray background)

### For Fri (Day 5)
Week 13 retrospective + Week 14 (case study extension + blog) planning

## Day 4 (Thu 27 ส.ค.) — Week 14 Prep (planning only)

### Delivered (planning artifacts)
1. Week 14 revised plan:
   - Case study already shipped Day 3 → Week 14 shifts to blog + outreach prep
   - Mon: Technical blog post
   - Tue: LinkedIn case study version + Thai vet forum research
   - Wed: Prospect list build (20-30 targets)
   - Thu: Outreach templates refinement
   - Fri: Retrospective + Week 15 outreach sprint kickoff

2. Ideal Customer Profile (ICP) defined:
   - Must: Laravel-based product, 5-50 devs, Bangkok/SEA, English or Thai
   - Nice: B2B SaaS, existing knowledge base, founder-accessible
   - Avoid: agencies (channel conflict), enterprises (slow), solo devs (no budget)

3. Prospect source channels (3 tiers):
   - Tier 1: LinkedIn Thai tech, Laravel Thailand FB, Blognone Jobs, Product Hunt TH
   - Tier 2: GitHub Thai devs, Twitter #laravel #thailand, meetup organizers
   - Tier 3: Cold email to SaaS company addresses

4. Outreach templates drafted (~/ai-sp/ai-curriculum/phase-4/outreach/templates.md):
   - Template A: SaaS product company
   - Template B: Laravel agency
   - Template C: Post-launch startup
   - Template D: LinkedIn DM (shorter)
   - Follow-up sequence (Day 5 + Day 12)
   - Anti-patterns list

5. Realistic expectations set:
   - 20-30 outreach → 2-4 replies → 1-2 calls → 0-1 pilot
   - First real pilot conversation by mid-Sept realistic

### Decisions for Fri or weekend
- Domain: recommend depotassistant.com via Cloudflare Registrar
- Email: Cloudflare Email Routing (free) → forward to Gmail
- Setup time: ~30 min post-domain-purchase

### Time
Total: 2 hours (light day)
- Block 1 (Week 14 planning): 45 min
- Block 2 (outreach templates): 45 min
- Block 3 (domain/email decisions): 20 min
- Wrap: 10 min

### Business note
Case study on landing page = business asset live in market since Wed.
Can start informal outreach any time now — no need to wait for domain.
Formal outreach begins Week 15 with metrics tracking.

## Day 5 (Fri 28 ส.ค.) — Week 13 Retrospective + Week 14 Kickoff

### Week 13 Summary
Shipped in 4 days (compressed from 5 planned):
- Landing page LIVE (Tue)
- Rebrand mid-session (Tue)  
- Screenshots + case study + auto-deploy (Wed)
- Outreach templates + Week 14 plan (Thu)
- Retrospective + Week 14 Mon plan (Fri, today)

### Wins
1. Fast path decision (.pages.dev + Gmail forward) → 3-day ship vs 3-week wait
2. Product-first pivot caught pre-deploy
3. Case study over demo video (higher ROI, dual-use)
4. Transparency section in case study (differentiator)
5. Planning day rhythm (Thu low-hands, Fri light) → no burnout

### Misses
1. Week 10 safety screenshots assumed but not real (verify assets before planning)
2. Copy has placeholder email (fix Week 14 with domain)
3. No custom domain yet (planned Week 14)
4. Cloudflare UI confusion (Workers vs Pages — documented)
5. Zero real prospect feedback (Week 15 validates)

### Key Learning
"Landing page ≠ perfect copy. Landing page = live URL that generates
conversations." Feedback loop starts Week 15, not Week 13.

### Week 14 Mon Plan (technical blog post)
Title: "Building a production RAG assistant in 12 weeks — what worked,
what didn't"
Word target: 1500-2500
Structure: starting point → foundations → RAG deep dive → 
production concerns → bugs → metrics → what I'd do differently
Publish: /blog/building-thai-rag.html
Cross-post: Medium + Dev.to (canonical to own URL)

### Weekend Optional
- Verify + purchase depotassistant.com if available
- Brainstorm 3 bugs to highlight in blog (reuse case study material)
- Note 5-10 initial prospects (LinkedIn scan)

### Week 13 Time Total
Mon: 3 hrs (copy)
Tue: 3 hrs (design + deploy)
Wed: 3 hrs (screenshots + case study)
Thu: 2 hrs (planning)
Fri: 1.5 hrs (retro + Week 14 plan)
Total: 12.5 hrs (below 13-hr weekly target, healthy pace)

## Week 14 Day 1 (Mon 31 ส.ค.) — Infrastructure Instead of Blog

### Original plan
Technical blog post ("Building a Thai RAG in 12 weeks", 1500-2500 words)

### Actual pivot
Domain + email infrastructure setup (higher ROI for Week 15 outreach)

### Shipped
1. DNS migration: Internet.bs → Cloudflare nameservers
   - potissolution.com fully managed by Cloudflare
   - Existing website preserved (159.223.39.198) via Cloudflare CDN
   - Zero downtime during nameserver swap
2. Custom subdomain live: depot-ai.potissolution.com
   - CNAME → depot-assistant.pages.dev
   - SSL auto-provisioned by Cloudflare
   - Bangkok edge (BKK) datacenter serves locally
3. Cloudflare Email Routing enabled
   - MX + SPF records auto-configured
   - depot-ai@potissolution.com → potissolution@gmail.com
   - End-to-end tested and verified
4. Landing page updated:
   - All hello@depotassistant.com placeholders → depot-ai@potissolution.com
   - Live at depot-ai.potissolution.com
   - Auto-deployed via Cloudflare Pages

### Total time
~2 hours (from decision to production infrastructure)

### Total cost
$0 (leveraged existing potissolution.com + free Cloudflare services)

### Business signal
Before: shareable .pages.dev URL (hobby feel)
After: professional subdomain + functional email (business feel)

Ready for Week 15 outreach with:
- Professional landing URL for email signatures
- Functional inbox for prospect replies
- Consistent branding across all touchpoints

### Blog post: deferred to Tue (Day 2) or Wed (Day 3)
- Structure already planned Fri Day 5 (Week 13)
- Can now include real depot-ai.potissolution.com URL in blog canonical

## Week 14 Day 2 (Tue 1 ก.ย.) — Technical Blog Post SHIPPED

### Shipped
1. blog/building-thai-rag.html — 174 lines, ~2000 words
   - Title: "Building a production RAG assistant in 12 weeks — what worked, what didn't"
   - 8 sections: starting point → foundations → RAG deep dive → production concerns → bugs → metrics → retrospective → product summary
   - Canonical URL: depot-ai.potissolution.com/blog/building-thai-rag.html
   
2. Landing page 2nd CTA card added (blog post below case study)
3. Auto-deployed via Cloudflare Pages

### 3 URLs in market now
- https://depot-ai.potissolution.com (landing)
- https://depot-ai.potissolution.com/case-study.html (product proof)
- https://depot-ai.potissolution.com/blog/building-thai-rag.html (engineering story)

### Content asset triple-purpose
1. SEO discoverability (Thai devs searching "Laravel RAG" / "production RAG")
2. LinkedIn/Twitter shareable (dev-focused audience)
3. Cold outreach credibility ("here's how I built it, not just the pitch")

### Trade-offs made
- Included "What ships as Depot Assistant" section (product mention)
- Chose transparency framing ("what didn't work") over hype
- 3 bugs vs all 4 (skipped cache camelCase — weakest lesson)
- Personal voice ("I", not "we") — solo founder authenticity

### Time
- Block 1 (outline confirmation): 15 min
- Block 2 (draft): 75 min (faster than planned 90)
- Block 3 (cross-link + deploy): 20 min
- Wrap: 15 min
- Total: ~2 hrs (below 3-hr budget, healthy)

### For Day 3 (Wed 2 ก.ย.)
Original plan: LinkedIn version of case study + Thai vet forum research
Better option: Prospect list build (Wed original goal)
- 20-30 target Laravel teams
- LinkedIn scan + FB Laravel Thailand group
- Metrics tracking spreadsheet
- Justification: content assets done, need prospects to send them to

## Week 14 Day 3 (Wed 2 ก.ย.) — LinkedIn Post SHIPPED

### Original plan
Prospect list build (20-30 target Laravel teams)

### Actual pivot #1
Prospect research pushed to Thu — needed more energy for social profiling work

### Actual pivot #2
LinkedIn case study post → Full engineering blog post (from Tue's material)

### Shipped
1. LinkedIn personal post — 800 words English
   - Hook: "I built my first production RAG system and caught 4 bugs..."
   - Bug transparency framing (matches Depot differentiator)
   - Real metrics + retrospective included
   - CTA: engagement question at end
   - URL: https://www.linkedin.com/posts/supatra-dinwong-66216710a_laravel-rag-ai-activity-7500829993598537729-Nnlh
2. First comment with 2 links (blog + case study)
   - Algorithm boost pattern (links suppressed in main post body)

### Key decision — introvert-aware execution
Original: post to LinkedIn + FB Laravel Thailand group + optional Twitter
Revised: LinkedIn ONLY today
- Reason: solo dev introvert = social multi-channel drain
- Better: 1 channel done well vs 3 channels half-effort
- Adjustment matches actual energy, not idealized plan

### Business signal
First public share of Depot Assistant to Thai tech LinkedIn network
- Passive discovery starts NOW (SEO from blog + LinkedIn visibility)
- Early engagement data (24-48 hrs) = signal for content-market fit
- If reactions/comments happen → validation of positioning
- If silent → also data (positioning/audience mismatch)

### For Thu Day 4
Prospect list build (moved from Wed)
- 20-30 target Laravel teams
- LinkedIn Sales Nav / manual scan
- Track in prospects.csv (schema already set)
- Fresh energy after today's public post exposure

### Time
Total: 1.5 hrs (light day, appropriate for social exposure work)