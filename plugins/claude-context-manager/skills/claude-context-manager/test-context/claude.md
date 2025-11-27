# Test Context Directory

This is a test context file for validating session integration.

## Overview

This directory is used for testing the claude-context-manager plugin's
session integration capabilities.

## Purpose

- Test staleness detection
- Test health reporting
- Test checkpoint integration
- Test handoff generation

## Key Files

- test_session_integration.py - Main integration test suite
- session_checkpoint.py - Checkpoint health check script
- session_handoff.py - Handoff report generation script

## Important Patterns

**Testing Pattern**: All tests use PYTHONPATH=. to ensure correct module imports

**Integration Pattern**: Scripts communicate via .ccmp/state.json shared state

## Dependencies

- utils/ module for core functionality
- session-management plugin for active session detection
- git for staleness analysis

## Usage

Run tests from plugin root:
```bash
cd plugins/claude-context-manager/skills/claude-context-manager
PYTHONPATH=. python scripts/test_session_integration.py
```

## Notes

Created: 2025-11-27
Last Updated: 2025-11-27
