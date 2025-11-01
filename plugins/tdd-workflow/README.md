# TDD Workflow

Test-Driven Development workflow with session integration. Enforces RED-GREEN-REFACTOR discipline with automatic checkpoints, metrics tracking, and enhanced session reporting.

## Description

Write the test first. Watch it fail. Write minimal code to pass.

This plugin provides comprehensive TDD guidance and **optionally integrates** with session-management for enhanced tracking, metrics, and discipline enforcement.

**Core principle:** If you didn't watch the test fail, you don't know if it tests the right thing.

## Features

### Core TDD Workflow
- **RED-GREEN-REFACTOR enforcement** - Strict discipline, no shortcuts
- **Verification checklists** - Never skip watching tests fail/pass
- **Rationalization detection** - Catches common TDD-avoidance excuses
- **Best practices guidance** - Test quality, naming, structure

### Session Integration (Optional)
When used with session-management plugin:
- 📊 **TDD cycle tracking** - Count RED-GREEN-REFACTOR cycles
- 📍 **Automatic checkpoints** - Phase-specific checkpoints (RED/GREEN/REFACTOR)
- 📈 **Test metrics** - Coverage trends, cycle times, discipline adherence
- 📝 **Enhanced handoffs** - Session reports include TDD statistics
- 🎯 **Enforced verification** - Harder to skip steps in TDD sessions

**Works perfectly standalone** - Full TDD functionality without session-management.

## Installation

### From Marketplace

```bash
claude-code plugin add AnthemFlynn/ccmp/tdd-workflow
```

### Manual Installation

1. Clone this repository
2. Copy `plugins/tdd-workflow` to your Claude Code plugins directory
3. Restart Claude Code

## Usage

### Standalone Mode (No session-management)

Simply implement features/bugfixes, and Claude will guide you through TDD:

```
You: "Add user authentication"
Claude: "Let's start with a failing test first..."
```

Claude enforces:
- Write test first (RED)
- Verify it fails correctly
- Write minimal code (GREEN)
- Verify it passes
- Refactor if needed

### Enhanced Mode (With session-management)

Start a TDD session for automatic tracking:

```bash
# Start TDD session
python scripts/session.py start feature/auth --objective "Add auth (TDD)"

# Or use --tdd flag
python scripts/session.py start feature/payments --tdd
```

#### TDD Checkpoints

```bash
# RED checkpoint (test written, verified failing)
python scripts/session.py checkpoint --label "red-user-validation" --tdd-phase RED

# GREEN checkpoint (minimal code, test passing)
python scripts/session.py checkpoint --label "green-user-validation" --tdd-phase GREEN

# REFACTOR checkpoint (optional)
python scripts/session.py checkpoint --label "refactor-extract-validator" --tdd-phase REFACTOR
```

#### View TDD Metrics

```bash
python scripts/session.py status
```

Shows:
- RED-GREEN-REFACTOR cycles completed
- Tests written vs passing
- Average cycle time
- Coverage trend

#### End TDD Session

```bash
python scripts/session.py end --handoff
```

Generates handoff with:
- Total TDD cycles
- Test files created
- Coverage metrics
- Discipline adherence report

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over. No exceptions.

## RED-GREEN-REFACTOR Cycle

```
RED → Verify RED → GREEN → Verify GREEN → REFACTOR → Repeat
```

### RED - Write Failing Test

Write one minimal test showing what should happen.

```typescript
test('retries failed operations 3 times', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```

### Verify RED - Watch It Fail

**MANDATORY. Never skip.**

```bash
npm test path/to/test.test.ts
```

Confirm test fails for the right reason.

### GREEN - Minimal Code

Write simplest code to pass the test.

```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error('unreachable');
}
```

### Verify GREEN - Watch It Pass

**MANDATORY.**

```bash
npm test path/to/test.test.ts
```

Confirm all tests pass.

### REFACTOR - Clean Up

After green only - remove duplication, improve names, extract helpers.

## Why This Plugin?

**Standalone:**
- Comprehensive TDD guidance
- Catches rationalization and shortcuts
- Enforces discipline
- Best practices built-in

**With session-management:**
- Automatic checkpoint tracking
- TDD metrics and trends
- Cycle time optimization
- Rich session documentation
- Team collaboration insights

## Common Rationalizations (We Catch These!)

| Excuse | Reality |
|--------|---------|
| "I'll test after" | Tests passing immediately prove nothing |
| "Already manually tested" | Ad-hoc ≠ systematic |
| "Deleting X hours is wasteful" | Sunk cost fallacy |
| "TDD is dogmatic" | TDD IS pragmatic - faster than debugging |

## When to Use

**Always:**
- New features
- Bug fixes
- Refactoring
- Behavior changes

**Exceptions (ask first):**
- Throwaway prototypes
- Generated code
- Configuration files

## Integration Detection

Plugin automatically detects if session-management is installed and active:
- ✅ Checks for `.git/sessions/` directory
- ✅ Looks for TDD objective or `--tdd` flag
- ✅ Validates `session.py` availability

**Detected:** Enhanced mode with checkpoints and metrics.
**Not detected:** Standard TDD guidance works perfectly.

## Best Practices

### Good Tests
- **Minimal** - One thing per test
- **Clear** - Name describes behavior
- **Shows intent** - Demonstrates desired API

### Bad Tests
- Multiple behaviors ("and" in name)
- Vague names (`test1`, `test2`)
- Tests mocks instead of real code

## Requirements

- **Python 3.7+** (for session-management integration only)
- **Git** (for TDD checkpoints)
- **session-management plugin** (optional, for enhanced features)

## Examples

See `SKILL.md` for detailed examples including:
- Bug fix workflow
- Feature development
- Refactoring with tests
- Debugging integration

## Credits

Based on `superpowers:test-driven-development` skill with enhancements for:
- Session-management integration
- Checkpoint automation
- Metrics tracking
- Team collaboration

## License

MIT
