#!/usr/bin/env node

/**
 * Sync Marketplace Script
 *
 * Generates marketplace.json from marketplace.extended.json by removing
 * extended fields that are not part of the CLI-compatible schema.
 *
 * Extended fields removed:
 * - featured
 * - mcpTools
 * - pluginCount
 * - pricing
 * - components
 */

const fs = require('fs');
const path = require('path');

const EXTENDED_FILE = path.join(__dirname, '../.claude-plugin/marketplace.extended.json');
const OUTPUT_FILE = path.join(__dirname, '../.claude-plugin/marketplace.json');

// Fields to remove from plugin entries (extended metadata)
const EXTENDED_PLUGIN_FIELDS = ['featured', 'mcpTools', 'pluginCount', 'pricing', 'components'];

function sanitizePlugin(plugin) {
  const sanitized = { ...plugin };

  // Remove extended fields
  EXTENDED_PLUGIN_FIELDS.forEach(field => {
    delete sanitized[field];
  });

  return sanitized;
}

function syncMarketplace() {
  try {
    console.log('📦 Syncing marketplace catalog...\n');

    // Read extended marketplace
    console.log('📖 Reading marketplace.extended.json...');
    const extendedContent = fs.readFileSync(EXTENDED_FILE, 'utf8');
    const extended = JSON.parse(extendedContent);

    // Create sanitized version
    console.log('🔧 Sanitizing plugin entries...');
    const sanitized = {
      ...extended,
      plugins: extended.plugins.map(sanitizePlugin)
    };

    // Validate
    console.log('✅ Validating catalog...');
    if (!sanitized.name || !sanitized.id || !sanitized.plugins) {
      throw new Error('Invalid marketplace structure');
    }

    console.log(`   Found ${sanitized.plugins.length} plugins`);

    // Check for duplicates
    const names = sanitized.plugins.map(p => p.name);
    const duplicates = names.filter((name, index) => names.indexOf(name) !== index);
    if (duplicates.length > 0) {
      throw new Error(`Duplicate plugin names found: ${duplicates.join(', ')}`);
    }

    // Write sanitized marketplace.json
    console.log('💾 Writing marketplace.json...');
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(sanitized, null, 2) + '\n');

    console.log('\n✨ Sync complete!\n');
    console.log('📊 MARKETPLACE STATS:');
    console.log(`   Total plugins: ${sanitized.plugins.length}`);

    // Count categories
    const categories = {};
    sanitized.plugins.forEach(p => {
      categories[p.category] = (categories[p.category] || 0) + 1;
    });
    console.log(`   Categories: ${Object.keys(categories).length}`);

    // Count featured (from extended)
    const featured = extended.plugins.filter(p => p.featured).length;
    if (featured > 0) {
      console.log(`   Featured: ${featured}`);
    }

    console.log('\n✅ Ready to commit:');
    console.log('   git add .claude-plugin/marketplace.extended.json .claude-plugin/marketplace.json');
    console.log('   git commit -m "chore: Update marketplace catalog"');

  } catch (error) {
    console.error('\n❌ Sync failed:', error.message);
    process.exit(1);
  }
}

// Run sync
syncMarketplace();
