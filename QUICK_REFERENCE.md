# AdCrewOS - Quick Reference Guide

## 🚀 5-Minute Quick Start

### For Windows Users:
```cmd
.\init.bat
npm install
copy .env.example .env.local
cd apps\api && copy .env.example .env
cd ..\web && copy .env.example .env
cd ..\..
cd apps\api && npm run db:generate && npm run db:migrate dev --name init && cd ..\..
npm run dev
```

### For Mac/Linux Users:
```bash
chmod +x init.sh && ./init.sh
npm install
cp .env.example .env.local
cd apps/api && cp .env.example .env
cd ../web && cp .env.example .env
cd ../..
cd apps/api && npm run db:generate && npm run db:migrate dev --name init && cd ../..
npm run dev
```

---

## 📦 What's Included

✅ **Complete Project Setup**
- Monorepo with Turborepo
- TypeScript configuration
- Docker Compose for local dev
- Package.json with all dependencies

✅ **Documentation (8 files)**
- README.md - Project overview
- SETUP_GUIDE.md - Project structure
- FILE_STRUCTURE_COMPLETE.md - All files with contents
- COMPLETE_IMPLEMENTATION_GUIDE.md - Technical guide
- PROJECT_COMPLETE.md - Delivery summary
- This file - Quick reference
- plan.md - 12-week roadmap (session state)
- Architecture docs

✅ **Configuration Files**
- Environment templates (.env.example)
- TypeScript config (tsconfig.json)
- Docker Compose setup
- Git ignore rules
- Initialization scripts

✅ **Task Tracking**
- 26 implementation tasks in SQL
- Phase-based roadmap
- Dependency mapping
- Progress tracking

---

## 📍 File Locations

| What | Where |
|------|-------|
| API Code | `apps/api/src/` |
| Web Code | `apps/web/src/` |
| Shared Code | `packages/shared/src/` |
| Database Schema | `apps/api/prisma/schema.prisma` |
| Documentation | Root directory & `docs/` |
| Configuration | Root directory |
| Environment Vars | `.env.example` & `apps/*/.env.example` |
| Docker Setup | `docker-compose.yml` |

---

## 🛠️ Common Commands

```bash
# Development
npm run dev                    # Start all services
npm run dev:api              # API only
npm run dev:web              # Web only

# Building
npm run build                 # Build everything
npm run build:api            # API build
npm run build:web            # Web build

# Database (from apps/api)
npm run db:generate          # Generate Prisma client
npm run db:migrate dev       # Create migration
npm run db:migrate deploy    # Apply migrations
npm run db:reset             # Reset database (dev only)

# Testing & Quality
npm run test                  # Run tests
npm run lint                  # Lint code
npm run type-check           # Type checking

# Docker
docker-compose up            # Start services
docker-compose down          # Stop services
docker-compose logs -f       # View logs

# Cleanup
npm run clean                # Clean build artifacts
rm -rf node_modules          # Remove dependencies
```

---

## 🔑 Environment Variables You Need to Add

### Add these to `.env` files:

**Payment Processing:**
- `STRIPE_SECRET_KEY` - From stripe.com
- `STRIPE_PUBLISHABLE_KEY` - From stripe.com
- `PAYPAL_CLIENT_ID` - Optional, from paypal.com

**Ad Platforms:**
- `GOOGLE_ADS_CLIENT_ID` - From Google Cloud Console
- `GOOGLE_ADS_CLIENT_SECRET` - From Google Cloud Console
- `META_APP_ID` - From Meta Developer Console
- `META_APP_SECRET` - From Meta Developer Console

**Communications:**
- `TWILIO_ACCOUNT_SID` - From twilio.com
- `TWILIO_AUTH_TOKEN` - From twilio.com
- `SENDGRID_API_KEY` - From sendgrid.com

**Database:**
- `DATABASE_URL` - PostgreSQL connection string
  - Local: `postgresql://postgres:postgres@localhost:5432/adcrewos_dev`
  - Cloud: From AWS RDS, Railway, etc.

**Other:**
- `JWT_SECRET` - Any strong random string
- `SESSION_SECRET` - Another strong random string
- `SENTRY_DSN` - From sentry.io (optional)

---

## 📋 Implementation Phases Overview

**Phase 1 (Weeks 1-2):** Foundation
- Setup infrastructure
- Database & auth
- Payment integration

**Phase 2 (Weeks 3-4):** Dashboard
- UI components
- Ad account connections
- Metrics display

**Phase 3 (Weeks 5-6):** Analytics
- Charts & reporting
- Report generation
- Email delivery

**Phase 4 (Weeks 7-8):** Automation
- Alert rules
- SMS/Email alerts
- Auto-pause/increase

**Phase 5-8:** Onboarding, Team, Testing, Deployment

See `plan.md` for detailed 26-task breakdown.

---

## 🔗 Important Links

- **GitHub:** Your repo here
- **Stripe Dashboard:** https://dashboard.stripe.com
- **Meta Developer:** https://developers.facebook.com
- **Google Cloud:** https://console.cloud.google.com
- **Twilio Console:** https://www.twilio.com/console
- **SendGrid:** https://app.sendgrid.com
- **AWS Console:** https://console.aws.amazon.com

---

## 🚨 Important Notes

1. **Never commit .env files** - They contain secrets
2. **Use .env.example as template** - Copy and fill with real values
3. **Database must be running** - Start PostgreSQL before npm run dev
4. **Clear node_modules if issues** - `npm run clean && npm install`
5. **Check logs for errors** - Watch terminal output carefully
6. **Save your work** - Commit frequently with meaningful messages

---

## 📞 Getting Help

1. Check `COMPLETE_IMPLEMENTATION_GUIDE.md` - Most answers are there
2. Review `FILE_STRUCTURE_COMPLETE.md` - For file organization
3. Check documentation in `docs/` folder
4. Read error messages carefully
5. Search GitHub issues for similar problems
6. Check dependency docs (links in COMPLETE_IMPLEMENTATION_GUIDE.md)

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] `npm run dev` starts without errors
- [ ] Frontend loads at http://localhost:3000
- [ ] API responds at http://localhost:3001/health
- [ ] Database connection successful (check console)
- [ ] Redis connection successful (check console)
- [ ] TypeScript compiles without errors
- [ ] No console errors in browser DevTools
- [ ] Docker containers running (if using Docker)

---

## 🎯 First Development Task

After everything is working:

1. Create a new branch: `git checkout -b feature/setup-verification`
2. Add a simple API endpoint test
3. Verify API calls work
4. Create a Pull Request
5. Push to GitHub

This ensures your development environment is fully functional!

---

## 💬 Useful Terminal Commands

```bash
# Check if ports are in use
netstat -ano | findstr :3000    # Windows
lsof -i :3000                   # Mac/Linux

# Check running Docker containers
docker ps

# View specific container logs
docker logs adcrewos-api        # API logs
docker logs adcrewos-db         # Database logs

# SSH into running container
docker exec -it adcrewos-api sh

# Restart services
docker-compose restart
```

---

## 🎨 Brand Colors Reference

Use these in your UI components:
- Navy (dark bg): `#0B1220`
- Cyan (accent): `#0EA5E9`
- Green (secondary): `#22C55E`
- Orange (alerts): `#F97316`
- Red (errors): `#EF4444`
- Gray (text): `#6B7280`

---

**You're all set! Time to build AdCrewOS! 🚀**
