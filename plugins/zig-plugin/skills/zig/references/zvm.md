# ZVM (Zig Version Manager)

ZVM manages multiple Zig versions and their corresponding ZLS installations.

## Installation

### macOS/Linux

```bash
# Using curl
curl -fsSL https://raw.githubusercontent.com/tristanisham/zvm/master/install.sh | bash

# Or download binary directly
curl -L https://github.com/tristanisham/zvm/releases/latest/download/zvm-$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m) -o ~/.local/bin/zvm
chmod +x ~/.local/bin/zvm
```

### PATH Setup

Add to `~/.bashrc`, `~/.zshrc`, or equivalent:

```bash
export ZVM_INSTALL="$HOME/.zvm"
export PATH="$ZVM_INSTALL/bin:$PATH"
```

Reload shell: `source ~/.zshrc`

## Common Commands

### Install Zig Version

```bash
# Install latest master (nightly)
zvm i master

# Install specific release
zvm i 0.13.0

# Install with matching ZLS
zvm i master --zls

# Force reinstall (update nightly)
zvm i master --zls -f
```

### Switch Versions

```bash
# Use a specific version
zvm use 0.13.0

# Use master
zvm use master
```

### List Installed

```bash
zvm ls
```

Output shows installed versions with active marked:
```
0.12.0
0.13.0 ←
master
```

### Remove Version

```bash
zvm rm 0.12.0
```

## Directory Structure

ZVM stores everything in `~/.zvm/`:

```
~/.zvm/
├── bin/           # Symlinks to active version
│   ├── zig        # → ../0.13.0/zig
│   └── zls        # → ../0.13.0/zls
├── 0.12.0/        # Installed version
│   ├── zig
│   └── lib/
├── 0.13.0/        # Another version
│   ├── zig
│   ├── zls
│   └── lib/
└── master/        # Nightly build
    ├── zig
    ├── zls
    └── lib/
```

## Best Practices

### Nightly Development

For bleeding-edge development:

```bash
# Initial setup
zvm i master --zls

# Weekly update
zvm i master --zls -f
```

### Project Pinning

For consistent builds across machines, document in README:

```markdown
## Requirements
- Zig 0.13.0 (install via `zvm i 0.13.0`)
```

### Multiple Projects

When working on projects with different Zig requirements:

```bash
# Switch to project A's version
cd project-a
zvm use 0.12.0

# Switch to project B's version
cd project-b
zvm use master
```

## Troubleshooting

### "zvm: command not found"

PATH not configured. Add to shell config:
```bash
export PATH="$HOME/.zvm/bin:$PATH"
```

### "permission denied"

Fix permissions:
```bash
chmod +x ~/.zvm/bin/*
chmod -R u+w ~/.zvm/
```

### Conflicting Zig Installations

Check for system Zig:
```bash
which -a zig
```

If multiple paths, ensure `~/.zvm/bin` comes first in PATH.

### Old Version Still Used

Shell caches command paths. Refresh:
```bash
hash -r  # bash
rehash   # zsh
```

### Download Failures

- Check network connectivity
- ZVM servers may be temporarily down
- Try direct download from ziglang.org

## Integration with ZLS

ZVM's `--zls` flag is crucial for nightly users:

```bash
# This ensures ZLS matches Zig version
zvm i master --zls
```

Without `--zls`, you must manually ensure ZLS compatibility.

### Version Matching Rules

| Zig Version | ZLS Version | Compatible? |
|-------------|-------------|-------------|
| 0.13.0 | 0.13.0 | ✓ Yes |
| 0.13.0 | 0.12.0 | ✗ No |
| master (dev.1234) | master (dev.1234) | ✓ Yes |
| master (dev.1234) | master (dev.1000) | ⚠ Maybe |

For nightly: Always update both together with `zvm i master --zls -f`.
