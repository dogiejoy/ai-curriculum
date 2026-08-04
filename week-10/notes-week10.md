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