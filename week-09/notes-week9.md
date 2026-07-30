# Week 9 — Evaluation Framework

## Day 1 (Mon 27 ก.ค.) — Golden Dataset Expansion + Baseline

### Shipped
1. Expanded GoldenQuestion schema:
   - question_type: single_doc, multi_hop, ambiguous, no_answer, precise_value
   - expected_answer_contains: keywords for LLM-as-judge
   - expected_refusal: bool for no_answer questions
2. golden_dataset_v2.json — 30 questions (15 original + 15 new)
3. Baseline retrieval measurement on v2 dataset

### Baseline results (retrieval-only, week6_fixed)
- hit@1: 90.0% (27/30) — down from 100% on v1
- 3 misses all no_answer questions (Q26, Q27, Q28)
- Retrieval can't handle "no answer exists" — need generation refusal

### Question-type performance
- single_doc (15): 100% ✓
- multi_hop (5): 100% hit@1 BUT metric misleading (only checks first doc)
- ambiguous (5): 100% ✓ (better than expected)
- no_answer (3): 0% expected (retrieval will always return top doc)
- precise_value (2): 100% ✓

### Key insights
1. Retrieval hit@1 alone is insufficient — need:
   - Content accuracy (LLM-as-judge)
   - Refusal quality for no_answer
   - All-truth recall for multi-hop
2. v2 dataset breaks 100% ceiling → measurement headroom restored
3. Ambiguous queries actually work well (semantic disambiguation stronger than expected)
4. Broad queries have latency spikes (Q25, Q27) — Week 11 optimization

### Week 9 priorities (revised based on baseline)
Day 2-3: LLM-as-judge implementation
Day 4: Multi-hop all_truth_recall metric + end-to-end eval on v2
Day 5: Semantic chunker fix + comparison (if time)

## Day 1 continued (Thu 30 ก.ค., compressed Tue-Wed-Thu) — LLM-as-Judge core

### Shipped
1. JudgeVerdict readonly DTO (3-dim scores + refusal verdict + costs)
2. LlmJudgeService with 2 judge types:
   - judgeQuality() — 3 dimensions (accuracy/completeness/faithfulness) 1-5 + verdict
   - judgeRefusal() — verdict-only (refused_correctly/hallucinated/partial_refuse)
3. Structured JSON output enforced via strict prompts
4. 5-question multi-type verification run

### Results (5 samples)
- Q06 (single_doc): pass 5/5/5 ✓
- Q19 (multi_hop): pass 5/5/5 ✓ — got both facts (15 นาที + BREACH-RPT-03)
- Q22 (ambiguous): pass 4.67 ✓
- Q26 (no_answer): judge said hallucinated → BUT reality = refused_correctly
- Q29 (precise_value): pass 5/5/5 ✓

### Critical finding: Judge has false-negative bias on refusals
Q26 example:
- Actual answer: graceful refusal citing "ราคาตามใบเสนอราคา" + sales redirect
- Judge verdict: hallucinated (WRONG)
- Root cause: refusal prompt too binary — doesn't recognize nuanced refusals
  that cite source phrases (interprets citation as evidence of "answering")

Judge accuracy: 4/5 = 80% agreement with reality
Direction: too strict (safer than opposite)

### Refusal judge prompt refinement needed (Mon 3 ส.ค. task)
Current binary: refused_correctly / hallucinated / partial_refuse
Add distinction:
- refused_correctly_helpful (refusal + source grounding + next step)
- refused_correctly_bare (just "I don't know")
- partial_refuse (mixes refusal with hallucination)
- hallucinated (makes up data)

### Cost profile
- Quality judge: $0.011/question avg
- Refusal judge: $0.005/question avg (shorter prompt)
- Full 30-question judge run: ~$0.30 estimated
- Total measurement cycle (generation + judge): ~$1/full-eval

### Business impact
LLM-as-judge is a differentiator for Package A:
- "We measure answer accuracy beyond citation match"
- Regression testing budget: $1/full-eval × weekly = $52/year per client
- Prevents shipping regressions when updating chunking/retrieval/prompts

### Deferred to Mon 3 ส.ค.
- Refusal judge prompt refinement (4-category verdict)
- Multi-hop all_truth_recall metric
- Full 30-question run with refined judge
- Semantic chunker fix (Week 6 tech debt)
- Baseline comparison table (retrieval-only vs end-to-end vs with-judge)