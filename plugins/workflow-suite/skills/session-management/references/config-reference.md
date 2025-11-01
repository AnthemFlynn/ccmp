# Configuration Reference

Complete reference for `.session/config.yaml` configuration options.

## Session Configuration

```yaml
session:
  auto_track: true
  auto_checkpoint: false
  checkpoint_interval: 30m
  handoff_on_end: true
  archive_after_days: 30
```

### `auto_track`
**Type:** boolean  
**Default:** `true`  
**Description:** Automatically track file changes during session

### `auto_checkpoint`
**Type:** boolean  
**Default:** `false`  
**Description:** Create automatic checkpoints at intervals

### `checkpoint_interval`
**Type:** string  
**Default:** `30m`  
**Description:** Interval for automatic checkpoints (30m, 1h, etc.)

### `handoff_on_end`
**Type:** boolean  
**Default:** `true`  
**Description:** Generate handoff document when ending session

### `archive_after_days`
**Type:** integer  
**Default:** `30`  
**Description:** Archive completed sessions after N days

---

## Context Configuration

```yaml
context:
  architecture: hexagonal
  patterns:
    - ports-and-adapters
    - repository-pattern
  conventions:
    - type-hints-required
    - docstrings-required
```

### `architecture`
**Type:** string  
**Options:** `hexagonal`, `layered`, `microservices`, `mvc`, `clean`, `ddd`  
**Description:** Primary architecture pattern for the project

### `patterns`
**Type:** list of strings  
**Description:** Code patterns to detect and enforce  
**Common values:**
- `ports-and-adapters`
- `repository-pattern`
- `dependency-injection`
- `factory-pattern`
- `cqrs`
- `event-sourcing`

### `conventions`
**Type:** list of strings  
**Description:** Project conventions  
**Common values:**
- `type-hints-required`
- `docstrings-required`
- `snake-case`
- `pep8-compliant`
- `test-coverage-required`

---

## Tracking Configuration

```yaml
tracking:
  watch_patterns:
    - "src/**/*.py"
    - "tests/**/*.py"
  ignore_patterns:
    - "**/__pycache__/**"
    - "**/node_modules/**"
  annotations:
    - "TODO:"
    - "FIXME:"
    - "DECISION:"
```

### `watch_patterns`
**Type:** list of glob patterns  
**Description:** Files to watch for changes

### `ignore_patterns`
**Type:** list of glob patterns  
**Description:** Files to ignore

### `annotations`
**Type:** list of strings  
**Description:** Code annotations to track

---

## Quality Configuration

```yaml
quality:
  coverage_threshold: 85
  new_code_coverage_threshold: 90
  require_tests: true
  block_merge_on_quality: true
```

### `coverage_threshold`
**Type:** integer (0-100)  
**Default:** `85`  
**Description:** Minimum overall test coverage percentage

### `new_code_coverage_threshold`
**Type:** integer (0-100)  
**Default:** `90`  
**Description:** Minimum coverage for new code

### `require_tests`
**Type:** boolean  
**Default:** `true`  
**Description:** Require tests for new features

### `block_merge_on_quality`
**Type:** boolean  
**Default:** `true`  
**Description:** Prevent merge if quality thresholds not met

---

## Display Configuration

```yaml
display:
  color: true
  verbose: false
  emoji: true
  date_format: "%Y-%m-%d %H:%M"
```

### `color`
**Type:** boolean  
**Default:** `true`  
**Description:** Use colored terminal output

### `verbose`
**Type:** boolean  
**Default:** `false`  
**Description:** Enable verbose output by default

### `emoji`
**Type:** boolean  
**Default:** `true`  
**Description:** Use emoji in output

### `date_format`
**Type:** string  
**Default:** `"%Y-%m-%d %H:%M"`  
**Description:** Date/time format string (Python strftime format)

---

## Complete Example

```yaml
# Session Management Configuration

session:
  auto_track: true
  auto_checkpoint: false
  checkpoint_interval: 30m
  handoff_on_end: true
  archive_after_days: 30

context:
  architecture: hexagonal
  patterns:
    - ports-and-adapters
    - repository-pattern
    - dependency-injection
  conventions:
    - type-hints-required
    - docstrings-required
    - snake-case
    - max-line-length-100

tracking:
  watch_patterns:
    - "src/**/*.py"
    - "tests/**/*.py"
    - "docs/**/*.md"
  ignore_patterns:
    - "**/__pycache__/**"
    - "**/.venv/**"
    - "**/dist/**"
  annotations:
    - "TODO:"
    - "FIXME:"
    - "DECISION:"
    - "BLOCKER:"

quality:
  coverage_threshold: 85
  new_code_coverage_threshold: 90
  require_tests: true
  block_merge_on_quality: true

display:
  color: true
  verbose: false
  emoji: true
  date_format: "%Y-%m-%d %H:%M"
```
