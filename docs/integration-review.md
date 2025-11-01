# CCMP Plugin Integration Review
**Date:** 2025-11-01
**Reviewer:** Claude (Systematic Analysis)
**Scope:** claude-context-manager, session-management, tdd-workflow

## Executive Summary

**Overall Assessment:** 🟡 MODERATE - Plugins work well independently, but significant compounding opportunities are MISSED.

**Key Findings:**
- ✅ All plugins are well-designed individually
- ⚠️ TDD-workflow has one-way integration (detects session-management)
- ❌ Context-manager is completely isolated (ZERO integration)
- ❌ Session-management doesn't leverage context-manager
- 🎯 **Major opportunity:** Context should inform sessions, sessions should update context

---

## 1. Current Integration Status

### Integration Matrix

| From ↓ / To → | context-manager | session-management | tdd-workflow |
|---------------|-----------------|-------------------|--------------|
| **context-manager** | — | ❌ None | ❌ None |
| **session-management** | ❌ None | — | ❌ None |
| **tdd-workflow** | ❌ None | ✅ Detects | — |

### What EXISTS Today

**TDD-Workflow → Session-Management** (One-way detection)
```bash
# TDD detects session and enhances itself
python scripts/session.py start feature/auth --tdd
# TDD workflow provides:
# - Automatic checkpoints (RED/GREEN/REFACTOR)
# - TDD metrics in session report
# - Cycle tracking
```

**Status:** ✅ **WORKING** - TDD successfully detects and uses sessions

**Detection Method:**
```python
# TDD checks:
1. .git/sessions/<branch>/ directory exists
2. Session config has TDD objective or --tdd flag
3. session.py commands available
```

---

## 2. Critical Issues

### Issue #1: Context-Manager is an Island 🏝️

**Severity:** 🔴 HIGH

**Problem:**
- Context-manager has NO knowledge of session-management
- Context-manager has NO knowledge of tdd-workflow
- Operates completely independently

**Impact:**
- Context updates aren't triggered by session checkpoints
- Session handoffs don't include context health
- TDD cycles don't update test documentation context
- Missed compound value: "Context-aware sessions"

**Example of Missed Opportunity:**
```bash
# What SHOULD happen:
python scripts/session.py checkpoint --label "api-complete"
# → Should trigger: python scripts/auto_update.py src/api/

# What ACTUALLY happens:
# Just creates checkpoint. No context update.
```

---

### Issue #2: Session-Management Ignores Context

**Severity:** 🔴 HIGH

**Problem:**
- Sessions don't read `claude.md` files during onboarding
- Session architecture.md duplicates what's in claude.md files
- No context health checks during sessions
- Session handoffs don't recommend context updates

**Impact:**
- Fragmented knowledge (`.session/architecture.md` vs `src/*/claude.md`)
- Context health degrades during long sessions
- New session starts lack codebase intelligence

**Example of Missed Opportunity:**
```bash
# What SHOULD happen:
python scripts/session.py start feature/auth
# → Agent brief includes:
#    - Session architecture.md
#    - ALL relevant claude.md context files
#    - Context health warnings

# What ACTUALLY happens:
# Only loads .session/ files, ignores claude.md
```

---

### Issue #3: TDD Integration is One-Way Only

**Severity:** 🟡 MEDIUM

**Problem:**
- TDD detects sessions (✅)
- But sessions don't know about TDD mode
- Sessions can't provide TDD-specific guidance
- TDD checkpoints use generic session commands (not TDD-aware)

**Impact:**
- Session reports don't highlight TDD violations
- Can't query "show me sessions with poor TDD discipline"
- Session analysis doesn't detect TDD anti-patterns

**Example:**
```bash
# Session doesn't know you're doing TDD
python scripts/session.py status

# Shows:
# - Objectives
# - Blockers
# - Commits

# SHOULD ALSO show (if --tdd session):
# - TDD cycles completed
# - Verification skips (RED flags)
# - Test coverage delta
```

---

## 3. Missed Compounding Opportunities

### Opportunity #1: Context-Aware Session Onboarding

**Current:** Sessions load `.session/architecture.md`

**Could Be:** Sessions load relevant `claude.md` files automatically

**Implementation:**
```python
# In session start/resume:
def load_context(branch, objectives):
    # 1. Load .session/architecture.md (global)
    # 2. Detect relevant directories from objectives
    #    "Add auth" → check src/auth/claude.md
    # 3. Include in agent brief
    # 4. Show context health warnings
```

**Value:**
- Agent starts with FULL codebase intelligence
- No manual context lookup
- Context staleness warnings upfront

---

### Opportunity #2: Checkpoint-Triggered Context Updates

**Current:** Context updates are manual

**Could Be:** Session checkpoints trigger smart context updates

**Implementation:**
```bash
# Session checkpoint detects changed files
python scripts/session.py checkpoint --label "auth-complete"

# If src/auth/* changed:
# 1. Check src/auth/claude.md staleness
# 2. If stale, offer auto-update
# 3. Update context as part of checkpoint

# Command becomes:
python scripts/session.py checkpoint --label "auth-complete" --update-context
```

**Value:**
- Context stays fresh automatically
- Zero cognitive overhead
- Context updates tied to natural checkpoints

---

### Opportunity #3: Test Documentation Auto-Update

**Current:** TDD creates tests, context is separate

**Could Be:** TDD GREEN checkpoints update test documentation

**Implementation:**
```bash
# When GREEN checkpoint (test passes):
1. Detect new test files
2. Check tests/*/claude.md
3. Auto-update with:
   - New test patterns discovered
   - Coverage changes
   - Test strategy updates
```

**Value:**
- Test context never stale
- Patterns documented as discovered
- Future tests follow established patterns

---

### Opportunity #4: Session Handoffs Include Context Health

**Current:** Handoffs show objectives, decisions, blockers

**Could Be:** Handoffs include context health report

**Implementation:**
```python
# In session.py end --handoff:
def generate_handoff():
    # ... existing handoff ...

    # Add context health section:
    health = run_monitor_script(repo_path)
    handoff += f"""
    ## Context Health
    - Overall: {health.score}/100
    - Critical: {health.critical_files}
    - Recommendations: {health.actions}
    """
```

**Value:**
- Next session knows context status
- Context maintenance becomes routine
- No surprise stale context

---

### Opportunity #5: TDD Cycle → Context Update Loop

**Current:** TDD cycles and context are independent

**Could Be:** Successful TDD cycles update relevant context

**Implementation:**
```bash
# After GREEN (tests pass):
if feature_complete:
    # Update implementation context
    auto_update src/feature/claude.md

    # Update test context
    auto_update tests/feature/claude.md

    # Include in TDD handoff:
    "Context updated: src/auth, tests/auth"
```

**Value:**
- Implementation patterns documented immediately
- Test patterns captured while fresh
- Context accuracy compounds with TDD discipline

---

## 4. Design Pattern Issues

### Anti-Pattern #1: Duplicate Architecture Documentation

**Problem:**
```
.session/architecture.md      ← Session architecture
src/*/claude.md               ← Directory-specific context
```

These overlap but don't reference each other.

**Solution:**
- `.session/architecture.md` = High-level architecture decisions
- `src/*/claude.md` = Implementation-level patterns
- Each references the other for full picture

---

### Anti-Pattern #2: Tool Commands in SKILL.md

**Problem:**
All three plugins embed Python script commands directly in SKILL.md:
```markdown
python scripts/session.py start ...
python scripts/monitor.py ...
```

**Issue:**
- Not following "skill = behavior, not tools" principle
- Skills should describe WHEN and WHY, tools are separate
- Makes skills brittle to tool changes

**Better Pattern:**
```markdown
# In SKILL.md (behavior):
When starting a session, I will:
1. Load project context
2. Brief you on objectives
3. Set up checkpoint tracking

# In separate tools/README.md:
To start sessions: python scripts/session.py start
```

---

### Anti-Pattern #3: No Shared Detection Interface

**Problem:**
TDD detects session-management with hardcoded checks:
```python
1. .git/sessions/<branch>/ directory exists
2. Session config has TDD objective
3. session.py commands available
```

**Issue:**
- Brittle coupling
- Every plugin needs custom detection
- No standard "is X active?" interface

**Better Pattern:**
Create `ccmp-integration.json`:
```json
{
  "active_plugins": ["session-management", "claude-context-manager"],
  "session": {
    "active": true,
    "branch": "feature/auth",
    "mode": "tdd"
  },
  "context": {
    "health_score": 87,
    "last_update": "2025-11-01"
  }
}
```

---

## 5. Recommended Improvements

### Priority 1: Bidirectional Context ↔ Session Integration

**What:** Make context and sessions aware of each other

**Changes:**

**1. Session onboarding loads relevant context**
```python
# In session.py start/resume:
- Load .session/architecture.md
+ Scan objectives for directories (e.g., "auth" → src/auth)
+ Load relevant src/*/claude.md files
+ Include context health in agent brief
+ Warn if critical staleness detected
```

**2. Checkpoints trigger context health checks**
```python
# In session.py checkpoint:
+ Detect changed directories
+ Check context staleness for those directories
+ Offer: "src/auth changed, update context? [y/N]"
+ If yes: python scripts/auto_update.py src/auth
```

**3. Handoffs include context health**
```python
# In session.py end --handoff:
+ Run python scripts/monitor.py
+ Add "Context Health" section to handoff
+ Recommend context updates for next session
```

**Impact:** 🔥 HIGH - Transforms isolated plugins into integrated system

---

### Priority 2: Context-Manager Detects Sessions

**What:** Context-manager becomes session-aware

**Changes:**

**1. Detect active sessions**
```python
# In auto_update.py and monitor.py:
+ Check if .git/sessions/<current-branch>/ exists
+ If yes, read session objectives
+ Prioritize directories related to objectives
```

**2. Context updates log to session**
```python
# When context updated:
+ If session active, append to session log:
+   "Updated src/auth/claude.md (staleness: 5 → 1)"
```

**3. Add context commands to session CLI**
```bash
# New session commands:
python scripts/session.py context-health
python scripts/session.py update-context <dir>
```

**Impact:** 🔥 HIGH - Makes context maintenance part of workflow

---

### Priority 3: Bidirectional TDD ↔ Session Integration

**What:** Sessions become TDD-aware, not just detection

**Changes:**

**1. Session knows about TDD mode**
```python
# In session config:
session:
  mode: "tdd"  # or "normal"
  tdd:
    enforce_verification: true
    track_cycles: true
```

**2. TDD metrics in session status**
```bash
python scripts/session.py status

# If TDD session, shows:
## TDD Metrics
- Cycles: 12 (RED→GREEN→REFACTOR)
- Skipped verifications: 0 ✅
- Coverage delta: +8.3%
- Average cycle time: 12m
```

**3. Session analysis detects TDD violations**
```bash
python scripts/session.py analyze

# Reports:
- "3 commits without tests (TDD violation)"
- "Test coverage decreased -2.1% (regression)"
```

**Impact:** 🟡 MEDIUM - Enhances TDD discipline tracking

---

### Priority 4: Unified Integration API

**What:** Standard way for plugins to detect/interact

**Changes:**

**1. Create `.ccmp/state.json`**
```json
{
  "version": "1.0",
  "plugins": {
    "session-management": {
      "active": true,
      "current_session": "feature/auth",
      "mode": "tdd"
    },
    "claude-context-manager": {
      "health_score": 87,
      "last_scan": "2025-11-01T10:30:00Z"
    },
    "tdd-workflow": {
      "cycles_today": 5,
      "discipline_score": 100
    }
  }
}
```

**2. Each plugin reads/writes state**
```python
from ccmp import integration

# Check if session active:
if integration.is_active("session-management"):
    session = integration.get_state("session-management")

# Update own state:
integration.update_state("tdd-workflow", {
    "cycles_today": 6
})
```

**Impact:** 🟢 LOW (but enables future plugins easily)

---

## 6. Compounding Skills Best Practices

### What We're Missing

According to Claude Skills best practices:

**1. Skills should amplify each other**
- ❌ Currently: Each plugin works alone
- ✅ Should: Each plugin makes others more effective

**2. Skills should share context automatically**
- ❌ Currently: No shared context mechanism
- ✅ Should: Session context flows to TDD, context health flows to sessions

**3. Skills should detect each other gracefully**
- 🟡 Partial: TDD detects sessions
- ✅ Should: All plugins detect and enhance each other

**4. Skills should avoid duplication**
- ❌ Currently: `.session/architecture.md` vs `src/*/claude.md`
- ✅ Should: Single source of truth, referenced not duplicated

---

## 7. Action Plan

### Phase 1: Foundation (Week 1)

**1. Create integration API**
- [ ] Add `.ccmp/state.json` mechanism
- [ ] Each plugin reads/writes state
- [ ] Standard detection interface

**2. Session loads context**
- [ ] `session.py start` reads relevant `claude.md` files
- [ ] Agent brief includes context health
- [ ] Warn on critical staleness

**Priority:** 🔴 HIGH
**Impact:** Makes sessions instantly more valuable

---

### Phase 2: Context-Session Bridge (Week 2)

**1. Checkpoint-triggered updates**
- [ ] Detect changed directories in checkpoints
- [ ] Offer context update if stale
- [ ] Log context updates in session

**2. Handoffs include context**
- [ ] Add context health section
- [ ] Recommend updates for next session

**Priority:** 🔴 HIGH
**Impact:** Keeps context fresh automatically

---

### Phase 3: TDD Bidirectional (Week 3)

**1. Sessions become TDD-aware**
- [ ] Add `mode: tdd` to session config
- [ ] Show TDD metrics in `session.py status`
- [ ] Detect TDD violations in analysis

**2. TDD updates test context**
- [ ] GREEN checkpoints update test claude.md
- [ ] Document discovered patterns
- [ ] Include in TDD handoffs

**Priority:** 🟡 MEDIUM
**Impact:** Stronger TDD discipline, better test docs

---

### Phase 4: Cleanup (Week 4)

**1. Refactor skills**
- [ ] Separate behavior (SKILL.md) from tools (docs)
- [ ] Remove command duplication
- [ ] Standardize detection patterns

**2. Documentation**
- [ ] Integration guide for all three plugins
- [ ] Compound workflow examples
- [ ] Updated README

**Priority:** 🟢 LOW (but improves maintainability)

---

## 8. Key Metrics to Track

Once integrated, measure:

**Compounding Effectiveness:**
- % of sessions that load context automatically
- % of checkpoints that trigger context updates
- Context staleness trend over time
- Session onboarding time (should decrease)

**User Value:**
- Do users complete sessions faster?
- Is context more accurate?
- Are TDD violations detected earlier?

---

## 9. Conclusion

**Current State:**
- Three well-designed plugins
- Working independently
- Missing 70% of potential compound value

**With Integration:**
- Context automatically stays fresh
- Sessions have full codebase intelligence
- TDD discipline documented and enforced
- Natural workflow, zero extra effort

**Bottom Line:**
These plugins are like talented musicians playing different songs.
**Integration makes them an orchestra.**

---

## Appendix: Integration Examples

### Example 1: Integrated TDD Session

**Before (current):**
```bash
python scripts/session.py start feature/auth --tdd
# → Session starts
# → You manually check context
# → You do TDD
# → You manually update context
# → Session ends
```

**After (integrated):**
```bash
python scripts/session.py start feature/auth --tdd
# → Session starts
# → Automatically loads src/auth/claude.md
# → Warns: "src/auth context 30 days old (should update)"
# → You do TDD with automatic RED/GREEN checkpoints
# → GREEN checkpoint offers: "Update src/auth context? [Y/n]"
# → Session ends with context health in handoff
```

**Value:** Seamless, zero extra cognitive load

---

### Example 2: Context-Driven Session Onboarding

**Before (current):**
```bash
python scripts/session.py resume feature/payment
# Brief shows:
# - Last checkpoint
# - Objectives
# - Architecture (from .session/)
```

**After (integrated):**
```bash
python scripts/session.py resume feature/payment
# Brief shows:
# - Last checkpoint
# - Objectives
# - Architecture (from .session/)
# + Context from src/payment/claude.md
# + Pattern warnings: "Payment API uses webhook pattern (see claude.md)"
# + Health alert: "tests/payment context stale (15 days)"
```

**Value:** Full situational awareness, no hunting for context

---

**End of Report**

---

**Reviewed by:** Claude (Sonnet 4.5)
**Generated:** 2025-11-01
**Next Review:** After Phase 1 implementation
