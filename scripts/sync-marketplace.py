#!/usr/bin/env python3

"""
Sync Marketplace Script

Generates marketplace.json from marketplace.extended.json by removing
extended fields that are not part of the CLI-compatible schema.

Extended fields removed:
- featured
- mcpTools
- pluginCount
- pricing
- components
"""

import json
import sys
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
EXTENDED_FILE = ROOT_DIR / ".claude-plugin" / "marketplace.extended.json"
OUTPUT_FILE = ROOT_DIR / ".claude-plugin" / "marketplace.json"

# Fields to remove from plugin entries (extended metadata)
EXTENDED_PLUGIN_FIELDS = ["featured", "mcpTools", "pluginCount", "pricing", "components"]


def sanitize_plugin(plugin):
    """Remove extended fields from plugin entry."""
    sanitized = plugin.copy()

    for field in EXTENDED_PLUGIN_FIELDS:
        sanitized.pop(field, None)

    return sanitized


def sync_marketplace():
    """Sync marketplace catalogs."""
    try:
        print("📦 Syncing marketplace catalog...\n")

        # Read extended marketplace
        print("📖 Reading marketplace.extended.json...")
        with open(EXTENDED_FILE, "r") as f:
            extended = json.load(f)

        # Create sanitized version
        print("🔧 Sanitizing plugin entries...")
        sanitized = {
            **extended,
            "plugins": [sanitize_plugin(p) for p in extended["plugins"]]
        }

        # Validate
        print("✅ Validating catalog...")
        if not all(k in sanitized for k in ["name", "id", "plugins"]):
            raise ValueError("Invalid marketplace structure")

        print(f"   Found {len(sanitized['plugins'])} plugins")

        # Check for duplicates
        names = [p["name"] for p in sanitized["plugins"]]
        duplicates = [name for name in set(names) if names.count(name) > 1]
        if duplicates:
            raise ValueError(f"Duplicate plugin names found: {', '.join(duplicates)}")

        # Write sanitized marketplace.json
        print("💾 Writing marketplace.json...")
        with open(OUTPUT_FILE, "w") as f:
            json.dump(sanitized, f, indent=2)
            f.write("\n")

        print("\n✨ Sync complete!\n")
        print("📊 MARKETPLACE STATS:")
        print(f"   Total plugins: {len(sanitized['plugins'])}")

        # Count categories
        categories = {}
        for p in sanitized["plugins"]:
            cat = p.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        print(f"   Categories: {len(categories)}")

        # Count featured (from extended)
        featured = sum(1 for p in extended["plugins"] if p.get("featured", False))
        if featured > 0:
            print(f"   Featured: {featured}")

        print("\n✅ Ready to commit:")
        print("   git add .claude-plugin/marketplace.extended.json .claude-plugin/marketplace.json")
        print('   git commit -m "chore: Update marketplace catalog"')

    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e.filename}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"\n❌ Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sync_marketplace()
