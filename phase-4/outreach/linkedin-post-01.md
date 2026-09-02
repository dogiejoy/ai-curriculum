I built my first production RAG system and caught 4 bugs that would have shipped.

One of them made my quality metrics look 40% worse than reality.

Here's the honest 12-week development story:

---

Context: I've been building Laravel apps for years. MySQL, Blade, Docker. Zero production AI experience before this.

The trigger was a real problem at Depot — my warehouse management platform for veterinary clinics in Thailand. Staff kept spending 3-8 minutes per query looking up product info, SOPs, cold-chain policies across scattered docs.

I gave myself 12 weeks to ship production RAG. Not learn RAG — ship it, with monitoring, safety, and cost tracking.

Here's what I actually did:

WHAT I REJECTED (empirically)
→ Reranking: added 500-800ms latency, zero quality gain on my corpus
→ Hybrid search (BM25 + vector): marginal improvement, doubled complexity
→ HyDE query expansion: worse retrieval on Thai queries

WHAT ACTUALLY WORKED
→ Chunk size 400 + overlap 50 for Thai (tested 4 strategies)
→ Voyage voyage-3-large embeddings (better Thai than OpenAI ada)
→ Postgres + pgvector (no separate vector DB needed)
→ Prompt caching (85% savings on repeated queries)
→ Smart model routing (Haiku for refusals, Sonnet for synthesis)

THE 4 BUGS I CAUGHT

Bug 1: My LLM-as-judge scored answers as "hallucinated" because it only received document titles, not full content. Fix revealed real quality was 90%, not 50%.

Bug 2: Anthropic SDK positional args got scrambled by PHP spread operator. Trace showed args in wrong slots. Fix: explicit named arguments.

Bug 3: A refactor left placeholder variables never populated. Sources labeled [doc_1] but content from [doc_5]. LLM refused correct answers.

Bug 4: nginx buffered SSE responses in production. Streaming worked in dev but broke on deploy. Fix required 3 layers: nginx, php-fpm, and frontend rendering.

REAL PRODUCTION METRICS (measured, not projected)
→ Cost per query: $0.038 blended
→ Cache hit rate: 41.4% on bursty workload
→ Cost savings vs baseline: 29%
→ Latency: p50 20s (full markdown), first token ~2s
→ Retrieval: 100% hit@1 on 30-question golden dataset

WHAT I'D DO DIFFERENTLY
→ Build eval framework Week 3, not Week 9 (would catch judge bug earlier)
→ Skip Reranking/HyDE experiments — save a week
→ Ship v0.1 to real user Week 6, not Week 8
→ Write the runbook Week 1

---

The real differentiator isn't "AI expertise." It's measurement discipline + honesty about what breaks.

Every production RAG blog post shows the wins. Very few show the bugs that almost shipped.

Happy to answer questions. What was your biggest surprise building production RAG?

#Laravel #RAG #AI #Thailand #Startup #IndieHacker