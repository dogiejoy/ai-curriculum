# Week 10 — Guardrails + Safety

## Day 1 (Tue 4 ส.ค.) — PII Redaction + Middleware

### Threat model established
Defense-in-depth layers for Depot RTB v0.1:
1. Input validation (existing)
2. Content screening (PII, prompt injection, off-topic) ← Day 1 focus
3. Retrieval + generation (existing)
4. Output screening (Day 3 target)
5. Logging + audit (Day 1 secondary)

### Shipped
1. PiiRedactor service — regex-based Tier 1 detection:
   - National ID (blocking severity)
   - Credit card (blocking)
   - Thai phone: mobile/landline/no-separator/spaces (redact)
   - Email (redact)
   - Vet license (redact)
2. PiiSafeguard middleware:
   - Applied to POST /api/assistant/chat only
   - Blocks with 400 + Thai message on blocking PII
   - Redacts + proceeds for non-blocking (Option C: log redaction)
   - Attaches redacted version to request for downstream log use
3. AssistantChatController updated:
   - Logs redacted query, not raw
   - Tracks pii_detected count + types for compliance audit

### Verified in production endpoint
- Clean query → passes through, pii_detected=0
- National ID query → 400 error, blocking_types logged (no raw PII in log)
- Regex handles 4 Thai phone formats (dashes, no-separator, spaces, landline)

### Design decisions
- Redact for logs, proceed with original (Option C)
  - Reason: vet staff queries may legitimately include phone/email
  - Blocking = friction for primary use case
  - Log redaction alone satisfies compliance
- Block only national ID + credit card (hard rules)
- Tier 1 (regex) only for v0.1; Tier 2 (LLM classifier) deferred

### Tech debt logged
- Test 2 log entry not visible (verification incomplete but implied working)
- LLM classifier for Thai names / owner+pet contexts (Tier 2)
- Prompt injection detection (Day 2-3 topic)
- Output PII scan (LLM might quote user's PII in refusal)
- Rate limiting (production infra)

### Business framing
"Depot RTB Assistant includes PII safeguards designed for Thai clinic
operations. National ID + credit card blocked outright. Phone/email
redacted from logs (compliance) while user retains full experience.
Attack surface reduced without hurting primary use case."

### For Day 2 (Wed 5 ส.ค.)
Reading: prompt injection patterns + detection strategies
Design: which injection attempts to catch (jailbreak, instruction override,
data exfiltration)

## Day 2 (Wed 5 ส.ค.) — Prompt Injection Threat Model + Design

### Attack pattern catalog (7 categories)
1. Direct instruction override — regex-catchable, medium likelihood
2. Role-play jailbreak — regex + LLM, high impact ⭐
3. System prompt extraction — regex, low priority for vet context
4. Data exfiltration — regex, medium priority
5. Scope violation / medical advice — LLM classifier, ⭐ #1 real threat
6. Encoded / obfuscated — very low frequency, skip for v0.1
7. Multi-turn poisoning — N/A (single-turn stateless)

### Depot RTB priority ranking (P0/P1/P2)
P0 (ship for v0.1):
- Direct override (regex)
- Role-play jailbreak (regex + LLM)
- Scope violation / medical advice (LLM classifier)

P1 (nice to have):
- Data exfiltration (regex)

P2 (defer):
- System prompt extraction
- Encoded attacks

### Key insight — real threat model
Attack surface = staff themselves under time pressure
NOT adversarial hackers (internal system)

Priority: prevent accidental medical-advice scope creep > defend against 
sophisticated attacks. Cost of over-blocking legitimate queries > cost of 
edge case attacks getting through.

### Detection architecture (2-layer)
Layer A: Regex (<1ms, $0) — direct patterns, extraction, exfil
Layer B: LLM classifier Haiku 4.5 (~300ms, ~$0.001) — semantic threats
Layer B only if Layer A didn't catch (skip 90% of queries)

### Response strategy
- Block (400): generic refusal, don't reveal category
- Redirect (200 no LLM): helpful message + what to do
- Proceed: invisible

### Estimated cost for v0.1
Haiku classifier: $0.25/day at 1000 queries (all classified)
Realistic: $0.025/day (only ~10% reach Layer B after regex filter)
Acceptable for production safety layer.

### Thu implementation plan
1. PromptInjectionDetector service class
2. Regex patterns for Layer A (7 patterns above)
3. LLM classifier prompt for Layer B (Haiku 4.5)
4. InjectionSafeguard middleware
5. Test suite: 7 regex tests + 5 LLM tests
6. Integration into /api/assistant/chat middleware chain

## Day 3 (Thu 6 ส.ค.) — Prompt Injection Detection Implementation

### Shipped
1. InjectionDetectionResult DTO (immutable):
   - 7 categories, 3 actions, layer tracking, confidence, cost
   - Static factory: ::clean() for safe pass-through
2. PromptInjectionDetector service (2-layer):
   - Layer A: 9 regex patterns (EN + Thai)
     * jailbreak_instruction_override (ignore/forget/disregard)
     * jailbreak_role_play (you are now, DAN)
     * system_prompt_extraction
     * data_exfiltration (list/dump all)
   - Layer B: Haiku 4.5 semantic classifier
     * Handles: medical_advice_request, subtle jailbreaks, off_topic
     * Fail-open on classifier errors (log warning, don't block legit users)
3. InjectionSafeguard middleware:
   - Chained after PiiSafeguard on /api/assistant/chat
   - Block (400) for adversarial categories
   - Redirect (200 no LLM call) for medical/off_topic
   - Full audit logging per detection

### Layer A verification (regex, $0)
8/8 correct including no false positive on "รายการสินค้าสำหรับแมว"

### Layer B verification (Haiku 4.5 classifier)
9/9 correct — including semantic nuance:
- "หมาผมท้องเสีย รักษายังไง" → medical (user's animal + treatment)
- "สินค้าไหนใช้สำหรับสุนัขที่อาเจียน" → safe (product info about symptom)
- This distinction requires semantic understanding regex can't provide

### Cost profile (verified in production)
- Layer A hits: $0 (regex, fast)
- Layer B hits: ~$0.00141/query (Haiku 4.5)
- Production estimate at 1000 queries/day:
  - ~90% caught by regex or clean = skip LLM
  - ~100 hit Layer B = $0.14/day = ~$4.20/month
  - Acceptable safety layer cost

### Design decisions
- Fail-open on classifier errors — don't block legitimate users due to
  transient API issues, log warning for monitoring
- Generic block message — don't reveal detection category to attackers
- Redirect (200) for medical/off_topic — user retains agency + guidance
- Order: PiiSafeguard → InjectionSafeguard (save Layer B cost when PII blocks)

### End-to-end verified
- Clean query → SSE stream normally
- Direct override → 400 block
- Medical advice → 200 redirect (helpful Thai message)
- Off-topic → 200 redirect
- Full audit trail in logs (category, layer, reason, IP, query preview)

### Deferred to Week 11 / 12
- Output PII scan (LLM might quote user's PII in refusal)
- Multi-turn context poisoning (v0.1 is single-turn)
- Encoded attack detection (base64, leet-speak) — very low frequency
- Rate limiting per IP (production infra concern)
- Prompt caching for classifier (frequent similar patterns)

### Business framing for Package A
"Depot RTB Assistant blocks 3 threat categories transparently:
1. Instruction override attempts (regex, $0 cost)
2. Data exfiltration attempts (regex, $0 cost)
3. Medical scope violations + subtle jailbreaks (LLM classifier, $0.14/day)

Full audit log per detection: category, method, reason, IP.
Attack surface reduced by 3 layers stacked (input validation → PII →
injection). Compliance-ready observability."

## Day 4 (Fri 7 ส.ค.) — Frontend Integration + Week 10 Close

### Shipped
public/assistant.html updates:
1. Content-Type detection before response consumption
2. renderGuardrailBanner() function — 2 visual variants:
   - Block (red 🚫, border-left #ff3b30, bg #fff2f2)
   - Redirect (blue ℹ️, border-left #007aff, bg #f0f7ff)
3. Category/detection metadata display for transparency
4. Sources sidebar clears on guardrail trigger
5. Status bar shows guardrail type for developer debugging

### 5 test scenarios verified end-to-end (screenshots captured)
- Safe query: normal streaming with sources + citations
- PII (national_id): red banner "Detected: national_id"  
- Injection: red banner generic (no category revealed)
- Medical advice: blue banner "Category: medical_advice_request"
- Off-topic: blue banner "Category: off_topic"

### UX design decisions
- Red vs blue color: intuitive severity signal
- Emojis (🚫 vs ℹ️): tone matches action (block vs guide)
- Category transparency ONLY on redirects (informational)
- Generic message on blocks (don't teach attackers)
- Sources cleared on guardrail (clean state prevents confusion)

### Week 10 Retrospective

Shipped 4 days:
- Day 1: PII detection + redaction middleware
- Day 2: Threat model + design (reading)
- Day 3: Injection detection (2-layer regex + Haiku classifier)
- Day 4: Frontend integration + screenshots

Depot RTB Assistant v0.1.2 = safety-hardened:
- PII layer: national_id/credit card blocked, phone/email redacted from logs
- Injection layer: 4 categories blocked, medical/off-topic redirected
- Full audit trail per decision
- Cost impact: ~$4.20/month at 1000 queries/day

### Business framing (Package A pitch material)

"Depot RTB Assistant ships with 3-layer defense stacked:
1. Input validation
2. PII safeguard (Thai national ID, credit card block; phone/email log-redact)
3. Injection safeguard (regex for known attacks + Haiku classifier for
   semantic threats like medical advice or off-topic)

Attack surface reduced without hurting primary use case.
Vet staff still get full product info experience — just protected from
themselves under time pressure and from accidental scope creep.

5 screenshot portfolio available (feature, compliance, security, scope,
focus). Total additional cost for full guardrail: ~$4.20/month per
1000 queries. Package A includes."

### Deferred to Week 11/12
- Output PII scan (LLM might quote user's PII in refusal)
- Rate limiting (production infra concern)  
- Multi-turn state (v0.1 is single-turn)
- Prompt caching for classifier repeat patterns
- pg_bigm for Thai FTS (from Week 7)
- Semantic chunker Thai splitter fix (from Week 6)