"""
AdCrewOS Project Bootstrap Script
Generates all necessary project files and directories
"""

import os
import json
from pathlib import Path

def create_dirs_and_files():
    """Create all project directories and files"""
    
    base_path = Path(".")
    
    # Define directory structure
    dirs = [
        "apps/api/src/config",
        "apps/api/src/controllers",
        "apps/api/src/middleware",
        "apps/api/src/models",
        "apps/api/src/routes",
        "apps/api/src/services",
        "apps/api/src/utils",
        "apps/api/src/types",
        "apps/api/prisma",
        "apps/api/tests",
        "apps/web/src/components/layout",
        "apps/web/src/components/dashboard",
        "apps/web/src/components/auth",
        "apps/web/src/components/campaigns",
        "apps/web/src/components/alerts",
        "apps/web/src/components/reports",
        "apps/web/src/components/common",
        "apps/web/src/pages",
        "apps/web/src/hooks",
        "apps/web/src/services",
        "apps/web/src/store",
        "apps/web/src/types",
        "apps/web/src/styles",
        "apps/web/src/utils",
        "apps/web/public",
        "packages/shared/src/types",
        "packages/shared/src/constants",
        "packages/shared/src/utils",
        "packages/sdk/src",
        "docs",
    ]
    
    # Create directories
    for dir_path in dirs:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ {dir_path}")
    
    print("\n✨ All directories created successfully!")

if __name__ == "__main__":
    create_dirs_and_files()
