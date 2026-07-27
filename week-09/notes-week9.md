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