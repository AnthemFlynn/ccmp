# Anthem's Claude Code Marketplace (CCMP)

**The Integrated Development Experience for Claude Code**

A curated collection of deeply integrated plugins that work together to provide compound value: context management, session workflows, and test-driven development that amplify each other's effectiveness.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Plugins: 3](https://img.shields.io/badge/Plugins-3-blue.svg)](#-featured-plugins)
[![Integration: Full](https://img.shields.io/badge/Integration-Full-green.svg)](#-the-integrated-ecosystem)

---

## 🎯 Why CCMP?

Most plugin collections are just that: collections. CCMP plugins are **designed to work together**, providing exponentially more value when used as a system rather than individually.

### The Power of Integration

| Using Individually | Using Together (CCMP) |
|-------------------|----------------------|
| Manually check context health | **Auto-checked at every checkpoint** |
| Remember to update documentation | **Auto-updated on GREEN checkpoints** |
| Track TDD discipline manually | **Automatically analyzed and scored** |
| Context goes stale | **Real-time monitoring and alerts** |
| Session handoffs miss details | **Comprehensive: context + TDD + decisions** |

**Result:** Zero cognitive overhead. Everything happens automatically.

---

## 🚀 Quick Start

### Installation

```bash
# Add the marketplace to Claude Code
claude-code marketplace add AnthemFlynn/ccmp

# Install all three core plugins for full integration
claude-code plugin add AnthemFlynn/ccmp/claude-context-manager
claude-code plugin add AnthemFlynn/ccmp/session-management
claude-code plugin add AnthemFlynn/ccmp/tdd-workflow
```

### Your First Integrated Session

```bash
# 1. Start a TDD session (activates all three plugins)
python scripts/session.py start feature/payment --tdd --objective "Add Stripe integration"

# Integration provides automatically:
# ✅ Loads relevant claude.md context files
# ✅ Shows context health warnings
# ✅ Activates TDD workflow
# ✅ Sets up checkpoint tracking

# 2. Work with full context + TDD discipline
# - Write failing test (RED)
# - Implement minimal code (GREEN)
# - Refactor if needed

# 3. Create GREEN checkpoint (magic happens here!)
python scripts/session.py checkpoint --label "stripe-webhook" --tdd-phase GREEN

# Automatically:
# ✅ Analyzes test patterns
# ✅ Updates tests/claude.md with discovered patterns
# ✅ Checks context health
# ✅ Increments TDD cycle counter
# ✅ Creates git commit

# 4. Analyze TDD discipline
python scripts/session.py analyze

# Shows:
# - TDD score (0-100)
# - Violations detected
# - Cycle timing
# - Recommendations

# 5. End with comprehensive handoff
python scripts/session.py end

# Includes:
# - Context health report
# - TDD metrics and violations
# - Test pattern updates
# - Next session recommendations
```

**Zero manual integration. Everything just works.**

---

## 🔗 The Integrated Ecosystem

CCMP plugins share state through `.ccmp/state.json` and coordinate automatically:

```
┌─────────────────────────────────────────────────────┐
│           Session Management (Orchestrator)         │
│  • Git-native workflows                             │
│  • Checkpoint tracking                              │
│  • Objective management                             │
└──────────────┬─────────────────────┬────────────────┘
               │                     │
       ┌───────▼────────┐    ┌──────▼────────┐
       │  Context       │    │  TDD          │
       │  Manager       │    │  Workflow     │
       │                │    │               │
       │ • Health       │    │ • Cycle       │
       │   monitoring   │    │   tracking    │
       │ • Auto-updates │    │ • Pattern     │
       │ • Staleness    │    │   discovery   │
       │   detection    │    │ • Violation   │
       │                │    │   detection   │
       └────────┬───────┘    └───────┬───────┘
                │                    │
                └────────┬───────────┘
                         │
                    ┌────▼────┐
                    │  .ccmp/ │
                    │ state   │
                    │  .json  │
                    └─────────┘
```

### Integration Patterns

**Pattern 1: Context Loading**
- Sessions auto-load relevant `claude.md` files based on objectives
- Full situational awareness from the start

**Pattern 2: Health Monitoring**
- Checkpoints detect stale context (>30 days)
- Automatic warnings and update recommendations

**Pattern 3: Test Documentation**
- GREEN checkpoints analyze test patterns
- Auto-generate/update `tests/*/claude.md`
- Patterns documented for future tests

**Pattern 4: TDD Analysis**
- Git history analyzed for violations
- Discipline scores calculated
- Cycle timing tracked

**Pattern 5: Comprehensive Handoffs**
- Context health + TDD metrics + decisions
- Next session knows exactly what needs attention

[Read Full Integration Guide →](./docs/guides/plugin-integration.md)

---

## ⭐ Featured Plugins

### 1. Claude Context Manager

**Autonomous codebase intelligence through `claude.md` files**

**Standalone Features:**
- Context health monitoring
- Automatic staleness detection
- Intelligent context updates
- Quality standards enforcement

**Integration Enhancements:**
- Sessions auto-load relevant context
- Checkpoints trigger health checks
- Handoffs include health reports
- Real-time monitoring available

```bash
# Monitor context health
python lib/context_monitor.py

# Watch mode (continuous monitoring)
python lib/context_monitor.py --watch

# Update stale context
python scripts/auto_update.py src/api/
```

[Full Documentation →](./plugins/claude-context-manager/README.md)

---

### 2. Session Management

**Git-native session lifecycle with context preservation**

**Standalone Features:**
- Branch-based sessions
- Objective tracking
- Decision logging
- Blocker management

**Integration Enhancements:**
- Auto-loads context on start
- Health checks at checkpoints
- TDD metrics in status
- Comprehensive handoffs

```bash
# Start session
python scripts/session.py start feature/auth --objective "Add OAuth"

# Check status (shows context + TDD state)
python scripts/session.py status

# Create checkpoint (health check + TDD analysis)
python scripts/session.py checkpoint --label "milestone"

# End with full handoff
python scripts/session.py end
```

[Full Documentation →](./plugins/session-management/README.md)

---

### 3. TDD Workflow

**Test-Driven Development with automatic pattern discovery**

**Standalone Features:**
- RED-GREEN-REFACTOR enforcement
- Rationalization detection
- TDD discipline guidance
- Best practices

**Integration Enhancements:**
- Session-aware checkpoints
- Automatic test pattern discovery
- Test context auto-documentation
- Violation detection and scoring
- Cycle timing analysis

```bash
# Start TDD session
python scripts/session.py start feature/api --tdd

# GREEN checkpoint (auto-documents patterns!)
python scripts/session.py checkpoint --label "green-validation" --tdd-phase GREEN

# Analyze TDD discipline
python scripts/session.py analyze

# View discovered patterns
cat tests/claude.md
```

[Full Documentation →](./plugins/tdd-workflow/README.md)

---

## 📊 Integration Achievements

All plugins fully integrated through **3 implementation phases**:

| Phase | Features | Status |
|-------|----------|--------|
| **Phase 1** | Integration API, Context loading, State management | ✅ Complete |
| **Phase 2** | Bidirectional sync, Real-time monitoring, Health checks | ✅ Complete |
| **Phase 3** | Pattern discovery, Test documentation, Violation detection | ✅ Complete |

[View Integration Review →](./docs/integration-review.md)
[Phase 1 Details →](./docs/guides/plugin-integration.md)
[Phase 2 Details →](./docs/phase2-implementation.md)
[Phase 3 Details →](./docs/phase3-implementation.md)

**Result:** 100% of integration goals achieved. Plugins amplify each other seamlessly.

---

## 🎓 Example Workflows

### Complete TDD Session with Auto-Documentation

```bash
# Morning: Start integrated TDD session
python scripts/session.py start feature/payment --tdd --objective "Add Stripe webhooks"

# Integration shows:
# - Loaded src/payment/claude.md
# - Context health: 92/100
# - TDD mode activated

# Work: Write test (RED)
# src/tests/test_webhook.py created

python scripts/session.py checkpoint --label "red-webhook-signature" --tdd-phase RED

# Work: Implement code (GREEN)
# src/webhook.py updated

python scripts/session.py checkpoint --label "green-webhook-signature" --tdd-phase GREEN

# Magic happens:
# ✅ Test patterns analyzed
# ✅ tests/claude.md auto-updated with:
#    - Framework: pytest
#    - Patterns: Direct assertions, Mocking with Mock()
# ✅ Context health checked
# ✅ TDD cycle: 1 completed
# ✅ Git commit created

# Continue working... (more RED-GREEN cycles)

# Check discipline
python scripts/session.py analyze

# Shows:
# - TDD Score: 95/100
# - Cycles: 5
# - Average cycle time: 15.3 minutes
# - No violations detected

# End session
python scripts/session.py end

# Handoff includes:
# - TDD metrics: 5 cycles, 95/100 score
# - Context health: 92/100
# - Test patterns documented: tests/claude.md
# - Recommendations for next session
```

**Total manual effort:** Running 4 commands. Everything else automatic.

---

### Context-Driven Session Handoff

```bash
# Developer A ends session
python scripts/session.py end

# Output:
# 📝 SESSION HANDOFF
# ============================================================
# Branch: feature/payment
# Mode: TDD
#
# 🏥 CONTEXT HEALTH
#    Final score: 87/100
#    ⚠️  Attention needed:
#       • src/api/ (35 days old)
#
# 🧪 TDD METRICS
#    Cycles completed: 12
#    Discipline score: 95/100
#    Commits with tests: 11
#    Commits without tests: 1
#
# 💡 RECOMMENDATIONS
#    • Update src/api/claude.md before next session
#    • Review commit abc123 (source without tests)

# Developer B resumes
python scripts/session.py resume feature/payment

# Instantly sees:
# - Full project context
# - What needs attention
# - Test patterns established
# - TDD history
```

---

## 🛠️ For Plugin Developers

### Repository Structure

```
ccmp/
├── .ccmp/
│   └── state.json                 # Integration state (git-ignored)
├── .claude-plugin/
│   ├── marketplace.extended.json  # Source of truth (edit this)
│   └── marketplace.json            # Auto-generated (don't edit)
├── lib/
│   ├── ccmp_integration.py        # Integration API
│   ├── context_loader.py          # Context file management
│   ├── context_monitor.py         # Real-time monitoring
│   ├── session_integration.py     # Session orchestration
│   ├── test_pattern_analyzer.py   # Pattern discovery
│   └── tdd_analyzer.py            # Violation detection
├── plugins/
│   ├── claude-context-manager/
│   ├── session-management/
│   └── tdd-workflow/
├── docs/
│   ├── integration-review.md      # Integration analysis
│   ├── guides/
│   │   └── plugin-integration.md  # Integration guide
│   ├── phase2-implementation.md   # Phase 2 docs
│   └── phase3-implementation.md   # Phase 3 docs
└── scripts/
    └── sync-marketplace.py         # Catalog sync
```

### Integration API

Create plugins that leverage the ecosystem:

```python
from lib.ccmp_integration import CCMPIntegration

integration = CCMPIntegration()

# Check if session is active
if integration.is_active("session-management"):
    session = integration.get_state("session-management")
    # Adapt behavior based on session mode

# Update your plugin's state
integration.update_state("your-plugin", {
    "active": True,
    "your_metric": 42
})

# Access other plugins
context_health = integration.get_state("claude-context-manager")
tdd_cycles = integration.get_state("tdd-workflow")
```

[Integration API Reference →](./docs/guides/plugin-integration.md#integration-api)

---

### Adding Your Plugin

1. **Create plugin structure**
2. **Add metadata to marketplace.extended.json**
3. **Implement integration (optional but recommended)**
4. **Run `npm run sync`**
5. **Test and commit**

[Full Developer Guide →](#-for-plugin-developers-detailed-guide)

---

## 📈 Benefits by User Type

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

## 🔍 Advanced Features

### Real-Time Context Monitoring

```bash
# Terminal 1: Start monitor daemon
python lib/context_monitor.py --watch --interval 300

# Checks every 5 minutes:
# - Context health score
# - Recently changed directories
# - Staleness warnings
# - Active session alerts

# Terminal 2: Work normally
# Monitor automatically detects changes and alerts you
```

### TDD Violation Detection

```bash
# Analyze git history for TDD anti-patterns
python lib/tdd_analyzer.py

# Detects:
# - Source changes without tests
# - Tests fixed after implementation
# - Cycle timing issues
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
# - Fixtures and hooks
# - Test structure
```

---

## 📚 Documentation

- **[Integration Guide](./docs/guides/plugin-integration.md)** - How plugins work together
- **[Integration Review](./docs/integration-review.md)** - Design decisions and analysis
- **[Phase 2 Implementation](./docs/phase2-implementation.md)** - Bidirectional sync details
- **[Phase 3 Implementation](./docs/phase3-implementation.md)** - TDD integration details

### Per-Plugin Documentation

- [Claude Context Manager](./plugins/claude-context-manager/README.md)
- [Session Management](./plugins/session-management/README.md)
- [TDD Workflow](./plugins/tdd-workflow/README.md)

---

## 🤝 Contributing

We welcome contributions! Whether it's:

- New plugins that integrate with the ecosystem
- Enhancements to existing plugins
- Documentation improvements
- Bug fixes

### Contribution Process

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Run `npm run sync` (if adding/modifying plugins)
5. Test thoroughly
6. Submit a Pull Request

### Guidelines

- Plugins should integrate with `.ccmp/state.json` when possible
- Follow existing code patterns
- Include comprehensive documentation
- Add tests for new features
- Use semantic versioning

[Full Contribution Guide →](./CONTRIBUTING.md)

---

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details.

Individual plugins may have their own licenses. See plugin directories for specifics.

---

## 🙋 Support

- **Issues:** [GitHub Issues](https://github.com/AnthemFlynn/ccmp/issues)
- **Discussions:** [GitHub Discussions](https://github.com/AnthemFlynn/ccmp/discussions)
- **Email:** AnthemFlynn@users.noreply.github.com

---

## 🎉 Acknowledgments

Built with [Claude Code](https://claude.com/claude-code) • Powered by integration

**The plugins that work better together** 🚀

---

**Maintained by AnthemFlynn** • [GitHub](https://github.com/AnthemFlynn)
