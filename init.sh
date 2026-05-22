#!/bin/bash

# AdCrewOS - Complete Project Initialization Script
# This script creates all directories, files, and initializes the project

set -e  # Exit on error

PROJECT_ROOT="."
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}🚀 AdCrewOS - Project Initialization${NC}"
echo "=========================================="
echo ""

# Function to create directory
create_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        echo -e "${GREEN}✅${NC} Created: $1"
    fi
}

# Function to create file with content
create_file() {
    local filepath=$1
    local content=$2
    
    if [ ! -f "$filepath" ]; then
        mkdir -p "$(dirname "$filepath")"
        echo "$content" > "$filepath"
        echo -e "${GREEN}✅${NC} Created: $filepath"
    fi
}

echo -e "${BLUE}Creating directory structure...${NC}"
echo ""

# Create all directories
create_dir "apps/api/src/config"
create_dir "apps/api/src/controllers"
create_dir "apps/api/src/middleware"
create_dir "apps/api/src/models"
create_dir "apps/api/src/routes"
create_dir "apps/api/src/services"
create_dir "apps/api/src/utils"
create_dir "apps/api/src/types"
create_dir "apps/api/prisma"
create_dir "apps/api/tests"
create_dir "apps/web/src/components/layout"
create_dir "apps/web/src/components/dashboard"
create_dir "apps/web/src/components/auth"
create_dir "apps/web/src/components/campaigns"
create_dir "apps/web/src/components/alerts"
create_dir "apps/web/src/components/reports"
create_dir "apps/web/src/components/common"
create_dir "apps/web/src/pages"
create_dir "apps/web/src/hooks"
create_dir "apps/web/src/services"
create_dir "apps/web/src/store"
create_dir "apps/web/src/types"
create_dir "apps/web/src/styles"
create_dir "apps/web/src/utils"
create_dir "apps/web/public"
create_dir "packages/shared/src/types"
create_dir "packages/shared/src/constants"
create_dir "packages/shared/src/utils"
create_dir "packages/sdk/src"
create_dir "docs"

echo ""
echo -e "${BLUE}Directory structure created successfully!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. npm install"
echo "2. cp .env.example .env.local"
echo "3. cd apps/api && cp .env.example .env"
echo "4. cd ../web && cp .env.example .env"
echo "5. npm run dev"
echo ""
echo -e "${GREEN}✨ Project initialization complete!${NC}"
