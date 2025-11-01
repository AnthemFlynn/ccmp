# CCMP Plugin Integration Guide

**Version:** 1.0 (Phase 1)
**Last Updated:** 2025-11-01

## Overview

CCMP plugins automatically integrate with each other to provide compound value. This guide explains how the integration works and how to use it effectively.

## Quick Start

All three core plugins work together seamlessly:

```bash
# 1. Start a session (activates session-management)
python scripts/session.py start feature/auth --objective "Add OAuth" --tdd

# Integration automatically:
# ✅ Loads relevant claude.md context files
# ✅ Shows context health warnings
# ✅ Activates TDD workflow
# ✅ Sets up checkpoint tracking

# 2. Work with full context + TDD discipline
# Session briefs include codebase intelligence
# TDD enforces RED-GREEN-REFACTOR
# Context stays current

# 3. Checkpoint with health checks
python scripts/session.py checkpoint --label "oauth-complete"
# ✅ Checks context health for changed directories
# ✅ Offers context updates if stale
# ✅ Logs TDD cycle

# 4. End with comprehensive handoff
python scripts/session.py end --handoff
# ✅ Includes context health report
# ✅ Shows TDD metrics
# ✅ Recommends actions for next session
```

**Result:** Seamless workflow, zero manual integration needed.

---

## Integration Architecture

### State Management (`.ccmp/state.json`)

All plugins share state through `.ccmp/state.json`:

```json
{
  "version": "1.0.0",
  "last_updated": "2025-11-01T10:00:00Z",
  "plugins": {
    "session-management": {
      "active": true,
      "current_session": "feature/auth",
      "mode": "tdd",
      "branch": "feature/auth",
      "objectives": ["Add OAuth2 authentication"]
    },
    "claude-context-manager": {
      "health_score": 87,
      "last_scan": "2025-11-01T09:30:00Z",
      "critical_files": ["src/api/"]
    },
    "tdd-workflow": {
      "active": true,
      "cycles_today": 5,
      "current_phase": "GREEN",
      "discipline_score": 100
    }
  }
}
```

**Location:** `.ccmp/state.json` (git-ignored, local only)

### Integration Library

**Location:** `lib/ccmp_integration.py`

**Key Functions:**
```python
from lib.ccmp_integration import (
    CCMPIntegration,
    is_session_active,
    is_tdd_mode,
    get_context_health
)

# Check if plugins are active
if is_session_active():
    # Session running

if is_tdd_mode():
    # TDD session active

# Get state
integration = CCMPIntegration()
state = integration.get_state("session-management")

# Update state
integration.update_state("tdd-workflow", {
    "cycles_today": 6,
    "active": True
})
```

---

## Integration Patterns

### Pattern 1: Session → Context Loading

**What:** Sessions automatically load relevant context files

**How it works:**
1. Session starts with objectives: `"Add OAuth2 authentication"`
2. Context loader scans for relevant directories: `src/auth/`, `tests/auth/`
3. Loads `claude.md` files from those directories
4. Includes in agent brief

**Benefits:**
- Zero manual context lookup
- Full situational awareness immediately
- Context stays visible throughout session

**Example:**
```python
from lib.context_loader import ContextLoader

loader = ContextLoader()
objectives = ["Add OAuth2 authentication"]

# Find relevant context
contexts = loader.find_relevant_context(objectives)

# Generate brief
brief = loader.generate_context_brief(objectives)
print(brief)
```

**Output:**
```
📚 CODEBASE CONTEXT
==================================================

📁 src/auth/
   Handles authentication and authorization using JWT tokens
   Patterns: JWT provider pattern, Middleware chain, Token rotation
   ⚠️  Always validate tokens server-side, never trust client

📁 tests/auth/
   Integration tests for auth flows using test fixtures
   Patterns: Fixture-based testing, Mock external APIs

💡 Tip: Full context in 2 claude.md files
```

---

### Pattern 2: Checkpoint → Context Health Check

**What:** Checkpoints automatically check context health

**How it works:**
1. Checkpoint created: `python scripts/session.py checkpoint --label "api-complete"`
2. Detects changed directories from git diff
3. Checks `claude.md` age in those directories
4. Warns if stale (>30 days)
5. Offers update

**Benefits:**
- Context never goes stale
- Automatic health monitoring
- Zero extra cognitive load

**Example:**
```python
from lib.session_integration import SessionIntegration

session = SessionIntegration()

# Checkpoint with health check
message = session.checkpoint(
    label="auth-complete",
    changed_directories=[Path("src/auth"), Path("tests/auth")]
)
print(message)
```

**Output:**
```
✅ Checkpoint created: auth-complete

⚠️  CONTEXT HEALTH WARNING:
   • src/auth (stale: 35 days)

💡 Update context? Run: python scripts/auto_update.py src/auth
```

---

### Pattern 3: TDD → Session Metrics

**What:** TDD cycles tracked in session state

**How it works:**
1. TDD session started: `--tdd` flag
2. Each RED/GREEN cycle increments counter
3. Session status shows TDD metrics
4. Handoff includes discipline score

**Benefits:**
- TDD discipline visibility
- Team accountability
- Trend tracking over time

**Example:**
```python
from lib.ccmp_integration import CCMPIntegration

integration = CCMPIntegration()

# Update TDD state after cycle
integration.update_state("tdd-workflow", {
    "cycles_today": 5,
    "current_phase": "GREEN",
    "discipline_score": 100  # No violations
})

# Session can read this
tdd_state = integration.get_state("tdd-workflow")
print(f"Cycles: {tdd_state['cycles_today']}")
```

---

### Pattern 4: Handoff → Context Health

**What:** Session handoffs include context health

**How it works:**
1. Session ends: `python scripts/session.py end --handoff`
2. Reads context health from integration state
3. Includes in handoff document
4. Recommends updates

**Benefits:**
- Next session knows context status
- Context maintenance becomes routine
- No surprise stale context

**Example:**
```python
from lib.session_integration import SessionIntegration

session = SessionIntegration()
handoff = session.end_session(generate_handoff=True)
print(handoff)
```

**Output:**
```
📝 SESSION HANDOFF
============================================================
Branch: feature/auth
Mode: TDD

🏥 CONTEXT HEALTH
   Final score: 87/100
   ⚠️  Attention needed:
      • src/api/ (35 days old)
      • tests/integration/ (28 days old)

🧪 TDD METRICS
   Cycles completed: 12
   Discipline score: 100/100

============================================================
Session complete. Context preserved for next session.
```

---

## Using the Integration

### For End Users

**You don't need to do anything special!** Integration happens automatically:

1. Start sessions normally
2. Create checkpoints normally
3. End sessions normally

The integration adds value silently in the background.

### For Plugin Developers

**To integrate your new plugin:**

1. **Read state from other plugins:**
```python
from lib.ccmp_integration import CCMPIntegration

integration = CCMPIntegration()

# Check if session active
if integration.is_active("session-management"):
    session = integration.get_state("session-management")
    # Your plugin can now adapt to session mode
```

2. **Update your plugin's state:**
```python
# When your plugin activates
integration.update_state("your-plugin", {
    "active": True,
    "your_metric": 42
})

# When your plugin deactivates
integration.set_active("your-plugin", False)
```

3. **Register your plugin in state.json schema:**
```json
{
  "plugins": {
    "your-plugin": {
      "installed": true,
      "active": false,
      "your_custom_fields": {}
    }
  }
}
```

---

## Integration Examples

### Example 1: Full TDD Session with Context

```bash
# Morning: Start TDD session
python scripts/session.py start feature/payment --tdd --objective "Add Stripe integration"

# Integration provides:
# ✅ Loads src/payment/claude.md automatically
# ✅ Shows: "Payment module uses webhook pattern"
# ✅ Warns: "src/payment context 25 days old"
# ✅ Activates TDD workflow
# ✅ Brief includes patterns and gotchas

# Work: Write test first (RED)
# TDD enforces discipline

# Checkpoint: Test passing (GREEN)
python scripts/session.py checkpoint --label "green-stripe-webhook"
# ✅ TDD cycle counted
# ✅ Context health checked
# ✅ No staleness warnings (recently updated)

# End: Generate handoff
python scripts/session.py end --handoff
# ✅ Shows: 8 TDD cycles completed
# ✅ Shows: Context health 95/100
# ✅ Shows: No discipline violations
```

---

### Example 2: Context Update During Session

```bash
# Start session
python scripts/session.py start feature/api-v2

# Integration loads: src/api/claude.md
# Warning: "src/api context 45 days old (critical)"

# You update the API code
# ...

# Checkpoint
python scripts/session.py checkpoint --label "api-refactor"
# ⚠️  CONTEXT HEALTH WARNING:
#    • src/api (stale: 45 days)
#
# 💡 Update context? [y/N]: y

# Integration runs:
python scripts/auto_update.py src/api
# Context updated! Now current.

# Next checkpoint shows healthy context
```

---

### Example 3: Non-TDD Session (Still Gets Integration)

```bash
# Regular session (no TDD)
python scripts/session.py start bugfix/auth-token

# Still gets integration benefits:
# ✅ Loads src/auth/claude.md
# ✅ Shows patterns and gotchas
# ✅ Context health in handoff
# ❌ No TDD enforcement (you didn't ask for it)

# Works great for exploration, debugging, quick fixes
```

---

## Troubleshooting

### Integration Not Working?

**Check 1: Is `.ccmp/` directory present?**
```bash
ls -la .ccmp/
# Should show state.json
```

**Check 2: Is integration library importable?**
```bash
python3 -c "from lib.ccmp_integration import CCMPIntegration; print('OK')"
```

**Check 3: Check state manually:**
```bash
cat .ccmp/state.json | jq '.plugins'
```

### Context Not Loading?

**Check 1: Do claude.md files exist?**
```bash
find . -name "claude.md" -type f
```

**Check 2: Test context loader:**
```bash
python3 -c "from lib.context_loader import ContextLoader; print(ContextLoader().find_all_context_files())"
```

### TDD Not Detecting Session?

**Check 1: Is session active?**
```bash
python3 -c "from lib.ccmp_integration import is_session_active; print(is_session_active())"
```

**Check 2: Check state:**
```bash
cat .ccmp/state.json | jq '.plugins."session-management"'
```

---

## What's Next (Future Phases)

**Phase 2: Enhanced Context-Session Bridge**
- Bidirectional sync
- Real-time staleness monitoring
- Automatic background updates

**Phase 3: Advanced TDD Integration**
- Test pattern discovery
- Auto-documentation of test strategies
- Coverage trend analysis

**Phase 4: PR Review Integration**
- Context-aware code review
- Session objective validation
- TDD verification in PRs

---

## Reference

### Files
- `.ccmp/state.json` - Shared plugin state
- `lib/ccmp_integration.py` - Integration API
- `lib/context_loader.py` - Context file loader
- `lib/session_integration.py` - Session integration helpers

### API Reference
See `lib/ccmp_integration.py` docstrings for full API documentation.

---

**Questions? See the integration review:** `docs/integration-review.md`
