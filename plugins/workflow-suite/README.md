# Workflow Suite

**Complete integrated development workflow for Claude Code**

> 🚧 **Pre-release (v0.0.5)**: This is an experimental bundled plugin. Expect breaking changes.

## What is Workflow Suite?

A single plugin that bundles three deeply integrated skills that work better together than apart:

1. **Claude Context Manager** - Autonomous codebase intelligence
2. **Session Management** - Git-native workflow orchestration
3. **TDD Workflow** - Test-driven development with pattern discovery

Install once, get exponential value through automatic integration.

---

## Why Bundle These Together?

These skills **amplify each other**:

| Using Individually | Using Together (Workflow Suite) |
|-------------------|--------------------------------|
| Manually check context health | **Auto-checked at every checkpoint** |
| Remember to update documentation | **Auto-updated on GREEN checkpoints** |
| Track TDD discipline manually | **Automatically analyzed and scored** |
| Context goes stale | **Real-time monitoring and alerts** |
| Session handoffs miss details | **Comprehensive: context + TDD + decisions** |

**Result:** Zero cognitive overhead. Everything happens automatically.

---

## Quick Start

### Installation

```bash
# Install from CCMP marketplace
claude-code plugin add AnthemFlynn/ccmp/workflow-suite
```

### Your First Integrated Session

```bash
# Start a TDD session (activates all three skills)
python plugins/workflow-suite/skills/session-management/scripts/session.py start feature/payment --tdd --objective "Add Stripe integration"

# Integration provides automatically:
# ✅ Loads relevant claude.md context files
# ✅ Shows context health warnings
# ✅ Activates TDD workflow
# ✅ Sets up checkpoint tracking

# Create GREEN checkpoint (magic happens here!)
python plugins/workflow-suite/skills/session-management/scripts/session.py checkpoint --label "stripe-webhook" --tdd-phase GREEN

# Automatically:
# ✅ Analyzes test patterns
# ✅ Updates tests/claude.md with discovered patterns
# ✅ Checks context health
# ✅ Increments TDD cycle counter
# ✅ Creates git commit
```

---

## What's Included

### 1. Claude Context Manager

**Autonomous codebase intelligence through `claude.md` files**

- Context health monitoring
- Automatic staleness detection
- Intelligent context updates
- Real-time monitoring daemon

**Integration:** Sessions auto-load relevant context, checkpoints trigger health checks

### 2. Session Management

**Git-native session lifecycle with context preservation**

- Branch-based sessions
- Objective tracking
- Decision logging
- Checkpoint creation

**Integration:** Auto-loads context on start, includes TDD metrics in status

### 3. TDD Workflow

**Test-driven development with automatic pattern discovery**

- RED-GREEN-REFACTOR enforcement
- Rationalization detection
- Automatic test pattern discovery
- Violation detection and scoring

**Integration:** GREEN checkpoints auto-document patterns, violations tracked in sessions

---

## Integration Architecture

All three skills coordinate through `.ccmp/state.json`:

```
Session Management (Orchestrator)
        ↓
    ┌───┴───┐
    ↓       ↓
Context   TDD
Manager   Workflow
    ↓       ↓
    └───┬───┘
        ↓
  .ccmp/state.json
```

**Shared State:** All skills read/write integration state automatically

**Shared Libraries:** Integration code in `lib/` directory:
- `ccmp_integration.py` - Core integration API
- `context_loader.py` - Context file management
- `context_monitor.py` - Real-time monitoring
- `session_integration.py` - Session orchestration
- `test_pattern_analyzer.py` - Pattern discovery
- `tdd_analyzer.py` - Violation detection

---

## Example Workflows

### Complete TDD Session with Auto-Documentation

```bash
# Morning: Start integrated TDD session
python skills/session-management/scripts/session.py start feature/payment --tdd

# Work: Write test (RED)
python skills/session-management/scripts/session.py checkpoint --label "red-webhook" --tdd-phase RED

# Work: Implement code (GREEN)
python skills/session-management/scripts/session.py checkpoint --label "green-webhook" --tdd-phase GREEN

# Magic happens:
# ✅ Test patterns analyzed
# ✅ tests/claude.md auto-updated
# ✅ Context health checked
# ✅ TDD cycle completed
# ✅ Git commit created

# Check discipline
python skills/session-management/scripts/session.py analyze

# End session with full handoff
python skills/session-management/scripts/session.py end
```

---

## Advanced Features

### Real-Time Context Monitoring

```bash
# Start monitor daemon
python lib/context_monitor.py --watch --interval 300

# Checks every 5 minutes:
# - Context health score
# - Staleness warnings
# - Active session alerts
```

### TDD Violation Detection

```bash
# Analyze git history for TDD anti-patterns
python lib/tdd_analyzer.py

# Detects:
# - Source changes without tests
# - Tests fixed after implementation
# - Discipline score calculation
```

### Test Pattern Discovery

```bash
# Analyze test directory
python lib/test_pattern_analyzer.py tests/

# Discovers:
# - Frameworks used
# - Mocking patterns
# - Assertion styles
# - Test structure
```

---

## Individual Skill Documentation

Each skill has comprehensive documentation:

- [Claude Context Manager](./skills/claude-context-manager/SKILL.md)
- [Session Management](./skills/session-management/SKILL.md)
- [TDD Workflow](./skills/tdd-workflow/SKILL.md)

---

## Benefits by User Type

### Solo Developers
- ✅ Context never goes stale
- ✅ Test patterns self-documenting
- ✅ TDD discipline self-monitoring
- ✅ Comprehensive session notes

### Teams
- ✅ Seamless developer handoffs
- ✅ Shared pattern knowledge
- ✅ Team-wide TDD accountability
- ✅ Consistent code quality

### AI-Assisted Development
- ✅ AI sees full codebase context
- ✅ Tests follow established patterns
- ✅ Context always current
- ✅ Zero onboarding time

---

## Pre-release Status

**Version 0.0.5** - Experimental

**What Works:**
- ✅ All three skills bundled and functional
- ✅ Integration infrastructure complete
- ✅ Shared libraries accessible
- ✅ Basic workflows tested

**Known Limitations:**
- ⚠️ Limited production testing
- ⚠️ API may change in future versions
- ⚠️ Documentation still evolving
- ⚠️ Some edge cases may not be handled

**Feedback Welcome:** Please report issues at [GitHub Issues](https://github.com/AnthemFlynn/ccmp/issues)

---

## License

MIT License - See [LICENSE](../../LICENSE) for details.

---

## Support

- **Issues:** [GitHub Issues](https://github.com/AnthemFlynn/ccmp/issues)
- **Discussions:** [GitHub Discussions](https://github.com/AnthemFlynn/ccmp/discussions)
- **Email:** AnthemFlynn@users.noreply.github.com

---

**The skills that work better together** 🚀

Built with [Claude Code](https://claude.com/claude-code) • Part of [CCMP](https://github.com/AnthemFlynn/ccmp)
