# Claude Context Manager

Autonomous context management for codebases through `claude.md` files with monitoring, staleness detection, and intelligent updates.

## Description

This plugin enables Claude to work as an autonomous **context manager** for codebases, maintaining accurate and actionable context intelligence through `claude.md` files.

## Features

- **Behavioral guidance**: Instructions for working proactively as a context manager
- **Monitoring tools**: Scripts to assess context health and detect staleness
- **Update automation**: Intelligent context synchronization based on code changes
- **Quality standards**: Patterns for creating actionable, dense agent context

## Installation

### From Marketplace

```bash
claude-code plugin add AnthemFlynn/ccmp/claude-context-manager
```

### Manual Installation

1. Clone this repository
2. Copy `plugins/claude-context-manager` to your Claude Code plugins directory
3. Restart Claude Code

## Usage

The skill provides four main workflows:

1. **Initial Setup** - First time working in a repository
2. **Continuous Maintenance** - Working in active codebase
3. **Change-Responsive Update** - After significant code changes
4. **Context Exploration** - Exploring existing context

See the full skill documentation in `skills/claude-context-manager/SKILL.md` for detailed instructions.

## Core Concept

`claude.md` files are **cognitive maps** - operational intelligence that helps Claude:
- Navigate faster (know structure and entry points)
- Generate better (follow existing patterns)
- Avoid errors (understand constraints and gotchas)
- Make decisions (know the rules and conventions)

This is **agent context**, not documentation. The goal is making future-Claude more effective.

## Examples

### Example 1: Creating Context for a New Directory

```bash
# Generate initial context for src/auth/
python3 plugins/claude-context-manager/skills/claude-context-manager/scripts/generate_claude_md.py src/auth

# Output: src/auth/claude.md created
```

**Generated Template:**
```markdown
# src/auth/

Authentication and authorization system for the application.

## Overview

Handles user authentication via OAuth2, JWT tokens, and session management.

## Directory Structure

```
src/auth/
├── oauth.py          # OAuth2 provider integration
├── jwt.py            # JWT token generation and validation
├── middleware.py     # Authentication middleware
└── session.py        # Session management
```

## Key Files

- **oauth.py**: Implements OAuth2 flow with Google and GitHub providers
- **jwt.py**: JWT token utilities with RS256 signing
- **middleware.py**: Express-style auth middleware for API routes

## Patterns & Conventions

- All auth functions return `Result<User, AuthError>` for error handling
- Tokens expire after 24 hours, refresh tokens after 30 days
- Use `@require_auth` decorator for protected endpoints

## Dependencies

- Depends on: `src/models/user.py` for User model
- Used by: `src/api/*` for route protection

## Usage

```python
from src.auth.oauth import authenticate_oauth
from src.auth.middleware import require_auth

@app.route('/api/user')
@require_auth
def get_user(user):
    return jsonify(user.to_dict())
```
```

### Example 2: Monitoring Context Health

```bash
# Check if context files are up to date
python3 plugins/claude-context-manager/skills/claude-context-manager/scripts/monitor.py

# Output:
# === CONTEXT HEALTH REPORT ===
#
# ✅ src/auth/claude.md - Healthy (updated 2 days ago)
# ⚠️  src/api/claude.md - Stale (updated 15 days ago)
# ❌ src/utils/claude.md - Outdated (updated 45 days ago)
#
# Recommendations:
# - Review src/api/claude.md (moderate changes detected)
# - Update src/utils/claude.md (significant drift from code)
```

### Example 3: Automatic Context Updates

```bash
# Auto-update context files based on code changes
python3 plugins/claude-context-manager/skills/claude-context-manager/scripts/auto_update.py

# Analyzes git changes and prompts for updates:
#
# Changes detected in src/auth/:
# - Added new file: oauth_providers.py
# - Modified: oauth.py (3 new functions)
#
# Update context? [Y/n]: y
# ✅ Updated src/auth/claude.md with new OAuth provider info
```

### Example 4: Validating Context Quality

```bash
# Validate context file meets quality standards
python3 plugins/claude-context-manager/skills/claude-context-manager/scripts/validate_claude_md.py src/auth/claude.md

# Output:
# ✅ Structure: Valid (all required sections present)
# ✅ Content: No TODO markers remaining
# ⚠️  Freshness: 8 days old (recommend update if active development)
# ✅ Density: High information density
#
# Score: 9/10 (Excellent)
```

### Example 5: Integration with Session Management

When using with the session-management plugin, context files are automatically loaded during session start:

```bash
# Start a session
/session-management:session-start

# Context manager automatically:
# 1. Loads relevant claude.md files based on objectives
# 2. Checks context health
# 3. Suggests updates if stale
# 4. Presents context-aware next actions
```

### Example 6: Creating a Repository Index

```bash
# Generate a master index of all context files
python3 plugins/claude-context-manager/skills/claude-context-manager/scripts/create_index.py

# Output: claude-index.md created with:
# - Directory tree of all claude.md files
# - Summary of each context area
# - Cross-references and dependencies
# - Health status of each context file
```

**Example Index Output:**
```markdown
# Repository Context Index

Last updated: 2025-11-15

## Context Map

```
project-root/
├── src/
│   ├── auth/ ✅ (2 days old)
│   ├── api/ ⚠️ (15 days old)
│   └── utils/ ❌ (45 days old)
└── tests/
    └── integration/ ✅ (1 day old)
```

## Context Areas

### src/auth/ - Authentication System
Status: ✅ Healthy
Last updated: 2 days ago
Summary: OAuth2 and JWT-based authentication

### src/api/ - API Endpoints
Status: ⚠️ Stale
Last updated: 15 days ago
Summary: REST API routes and handlers
Recommendation: Review recent endpoint additions
```

## License

MIT
