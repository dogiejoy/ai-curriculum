# Depot RTB — AI Integration for Laravel Apps

---

## HERO SECTION

### Headline
**Ship AI features into your Laravel app in 2-3 weeks.**

### Subheadline
Package A: complete RAG integration (retrieval + generation + safety guardrails + cost monitoring). $2,500 flat fee. Built by a solo dev who ships production Laravel apps daily.

### Primary CTA
[Book a 30-min discovery call →]

### Trust bar (below CTA)
Proven on Depot RTB Assistant (production) · 100% retrieval accuracy · $0.038/query verified · Full Docker deployment

---

## PROBLEM SECTION

### Section header
Your client wants AI. You don't have an AI engineer.

### Body copy
The usual paths hurt:

- **Hire an AI engineer**: 3-6 months to onboard, $80-150K/year, may leave in 12 months
- **DIY with ChatGPT plugin**: works for demos, breaks in production (no citations, no guardrails, no cost tracking)
- **Wait for AI to "settle down"**: your competitor ships it this quarter

You need production-ready AI that fits your existing Laravel stack — without becoming an AI shop yourself.

---

## SOLUTION SECTION

### Section header
Package A: turnkey RAG integration, delivered.

### 3-column feature grid

**🎯 Retrieval that works**
Voyage AI embeddings + Postgres/pgvector. 100% retrieval accuracy on our benchmark dataset. Sub-second search across your corpus.

**🛡️ Safety built-in**
PII redaction (Thai national ID, phone, email). Prompt injection detection (regex + LLM classifier). Medical/legal scope boundaries you can trust.

**💰 Cost transparency**
Every query logged: input tokens, cache hits, model routed, cost per response. Dashboard endpoint + CLI stats. Client sees real economics.

**⚡ Streaming responses**
SSE-based, first token in ~2s. Cache hits save ~40% on bursty traffic. Smart routing sends simple queries to cheaper models.

**🐳 Production infrastructure**
Docker Compose stack: nginx + php-fpm + Postgres. Health checks, monitoring, secrets management. Ships as `docker compose up`.

**📚 Full documentation**
README + operations runbook + failure playbook + client onboarding checklist. Your team maintains it after handoff.

---

## PROOF SECTION

### Section header
Depot RTB Assistant — measured, not promised.

### Case study block

**What it is**  
Production RAG assistant for veterinary clinic warehouse management. Handles product queries, SOP lookups, business process questions in Thai + English.

**Real metrics (not projections)**  

| Metric | Value |
|---|---|
| Retrieval accuracy | 100% hit@1 (30-question golden set) |
| Cost per query | $0.038 (measured) |
| Cache hit rate | 41.4% (bursty workload) |
| Cache cost savings | 29% off baseline |
| Latency p50 | 20s (full markdown answer) |
| Onboarding time | <10 min fresh install (README verified) |

**Screenshots** (embed 4-6 from Weeks 8/10):
- Metacam dose calculation with citations
- Cold chain temperature reference
- PII block (national ID)
- Medical advice redirect
- Injection block
- Cost dashboard CLI output

---

## PROCESS SECTION

### Section header
How Package A works.

### 3-step timeline

**Week 1 — Discovery + Setup**
- 90-min kickoff call: understand your app + data + use cases
- Provision Docker stack in your infrastructure
- Load your content into the indexing pipeline
- Configure API keys (Anthropic, Voyage)

**Week 2 — Integration + Guardrails**
- Wire assistant endpoint into your Laravel routes
- Customize system prompts for your domain
- Configure PII patterns + safety rules for your users
- Build 15-30 question golden dataset with you

**Week 3 — Launch + Handoff**
- Full monitoring + cost dashboard live
- Documentation walkthrough with your team
- 30-day post-launch support included
- You own the code + infrastructure

---

## PRICING SECTION

### Section header
Simple pricing. No surprises.

### Package A card

**Package A — RAG Integration**  
**$2,500 flat fee** (85,000 THB)

Everything included:
- Full retrieval + generation pipeline
- 3 safety layers (PII, injection, scope)
- Prompt caching + smart routing (30%+ cost savings)
- Docker deployment stack
- Complete documentation package
- 30-day post-launch support

Not included (you pay direct to providers):
- Anthropic API usage (~$0.02-0.05/query at your scale)
- Voyage AI embeddings (typically <$0.50/month)
- Your server hosting

**Payment**: 50% upfront, 50% on delivery

[Book discovery call →]

---

## FAQ SECTION

**Q: What Laravel version is supported?**  
A: Laravel 10, 11, 12, 13. Uses standard Eloquent + service pattern — no exotic dependencies.

**Q: What if I use MySQL instead of Postgres?**  
A: I add Postgres to your Docker stack for vector storage. Your existing MySQL keeps its role.

**Q: Can I use models other than Claude?**  
A: Package A ships with Claude (best quality + safety I've measured). OpenAI/Gemini adapters available as add-on ($500 extra).

**Q: What language does the assistant support?**  
A: Thai + English out of the box. Other languages possible — depends on Voyage's coverage for your language.

**Q: Do you support ongoing changes after 30 days?**  
A: Yes — monthly retainer options: $500/mo (basic support), $1,500/mo (feature additions + monitoring), $3,000/mo (dedicated).

**Q: What if I need something not in Package A?**  
A: Book a call — custom scope quoted separately. Common add-ons: multi-language, custom UI, API-first integration, on-premise deployment.

**Q: Why should I trust you?**  
A: I built Depot RTB Assistant in 12 weeks — every metric measured, every bug transparent. See notes-week*.md across all 12 weeks: real development story, real trade-offs. No AI expertise theater.

---

## ABOUT SECTION

### Section header
About [Depot Assistant]

### Body copy
Built by a solo developer in Bangkok. First deployed at Depot RTB (veterinary clinic warehouse platform). Every feature measured, every bug transparent.

12 weeks of focused development produced v0.3 — production-ready RAG that ships with monitoring, safety guardrails, and cost transparency built in.

Depot Assistant is what should have existed when I started: a RAG platform you can trust because it already runs in production.

---

## FINAL CTA

### Section header
Ready to ship AI in 3 weeks?

### CTA block
Book a 30-minute discovery call. No pitch — I'll ask about your app, your data, your users. If Package A fits, we'll talk timeline. If not, I'll tell you what would work better.

[Book discovery call →]

Or email: [dogie.joy@gmail.com]