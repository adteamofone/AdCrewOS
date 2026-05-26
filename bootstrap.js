#!/usr/bin/env node

/**
 * AdCrewOS Project Bootstrap Script
 * Creates all necessary directories and foundational files
 */

const fs = require('fs');
const path = require('path');

const projectRoot = __dirname;

// Define all directories to create
const directories = [
  'apps/api/src/config',
  'apps/api/src/controllers',
  'apps/api/src/middleware',
  'apps/api/src/models',
  'apps/api/src/routes',
  'apps/api/src/services',
  'apps/api/src/utils',
  'apps/api/src/types',
  'apps/api/prisma',
  'apps/api/tests',
  'apps/web/src/components/layout',
  'apps/web/src/components/dashboard',
  'apps/web/src/components/auth',
  'apps/web/src/components/campaigns',
  'apps/web/src/components/alerts',
  'apps/web/src/components/reports',
  'apps/web/src/components/common',
  'apps/web/src/pages',
  'apps/web/src/hooks',
  'apps/web/src/services',
  'apps/web/src/store',
  'apps/web/src/types',
  'apps/web/src/styles',
  'apps/web/src/utils',
  'apps/web/public',
  'packages/shared/src/types',
  'packages/shared/src/constants',
  'packages/shared/src/utils',
  'packages/sdk/src',
  'docs',
];

console.log('🚀 Creating AdCrewOS project structure...\n');

// Create all directories
directories.forEach(dir => {
  const fullPath = path.join(projectRoot, dir);
  if (!fs.existsSync(fullPath)) {
    fs.mkdirSync(fullPath, { recursive: true });
    console.log(`✅ Created: ${dir}`);
  }
});

console.log('\n✨ Project structure created successfully!');
console.log('\nNext steps:');
console.log('1. npm install');
console.log('2. cp .env.example .env.local');
console.log('3. npm run dev');
