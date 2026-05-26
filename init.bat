@echo off
REM AdCrewOS - Complete Project Initialization Script (Windows)

echo.
echo ============================================
echo 🚀 AdCrewOS - Project Initialization
echo ============================================
echo.

setlocal enabledelayedexpansion

REM Create all directories
echo Creating directory structure...
echo.

mkdir "apps\api\src\config" 2>nul
mkdir "apps\api\src\controllers" 2>nul
mkdir "apps\api\src\middleware" 2>nul
mkdir "apps\api\src\models" 2>nul
mkdir "apps\api\src\routes" 2>nul
mkdir "apps\api\src\services" 2>nul
mkdir "apps\api\src\utils" 2>nul
mkdir "apps\api\src\types" 2>nul
mkdir "apps\api\prisma" 2>nul
mkdir "apps\api\tests" 2>nul

mkdir "apps\web\src\components\layout" 2>nul
mkdir "apps\web\src\components\dashboard" 2>nul
mkdir "apps\web\src\components\auth" 2>nul
mkdir "apps\web\src\components\campaigns" 2>nul
mkdir "apps\web\src\components\alerts" 2>nul
mkdir "apps\web\src\components\reports" 2>nul
mkdir "apps\web\src\components\common" 2>nul
mkdir "apps\web\src\pages" 2>nul
mkdir "apps\web\src\hooks" 2>nul
mkdir "apps\web\src\services" 2>nul
mkdir "apps\web\src\store" 2>nul
mkdir "apps\web\src\types" 2>nul
mkdir "apps\web\src\styles" 2>nul
mkdir "apps\web\src\utils" 2>nul
mkdir "apps\web\public" 2>nul

mkdir "packages\shared\src\types" 2>nul
mkdir "packages\shared\src\constants" 2>nul
mkdir "packages\shared\src\utils" 2>nul

mkdir "packages\sdk\src" 2>nul
mkdir "docs" 2>nul

echo ✅ Directory structure created successfully!
echo.
echo Next steps:
echo 1. npm install
echo 2. copy .env.example .env.local
echo 3. cd apps\api ^&^& copy .env.example .env
echo 4. cd ..\web ^&^& copy .env.example .env
echo 5. npm run dev
echo.
echo ✨ Project initialization complete!
echo.
