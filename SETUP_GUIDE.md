# AdCrewOS - Project Setup & Implementation Guide

This document provides the complete project structure and all necessary files to bootstrap AdCrewOS.

## Directory Structure

```
AdCrewOS/
├── apps/
│   ├── api/                          # Node.js + Express backend
│   │   ├── src/
│   │   │   ├── config/               # Configuration files
│   │   │   ├── controllers/          # Route controllers
│   │   │   ├── middleware/           # Express middleware
│   │   │   ├── models/               # Database models
│   │   │   ├── routes/               # API routes
│   │   │   ├── services/             # Business logic
│   │   │   ├── utils/                # Utility functions
│   │   │   ├── types/                # TypeScript types
│   │   │   └── index.ts              # App entry point
│   │   ├── prisma/
│   │   │   ├── schema.prisma         # Database schema
│   │   │   └── migrations/           # Database migrations
│   │   ├── tests/                    # Jest tests
│   │   ├── .env.example
│   │   ├── tsconfig.json
│   │   ├── package.json
│   │   └── Dockerfile
│   │
│   └── web/                          # React frontend (Next.js)
│       ├── src/
│       │   ├── components/           # React components
│       │   │   ├── layout/           # Layout components
│       │   │   ├── dashboard/        # Dashboard components
│       │   │   ├── auth/             # Auth components
│       │   │   ├── campaigns/        # Campaign components
│       │   │   ├── alerts/           # Alert components
│       │   │   ├── reports/          # Report components
│       │   │   └── common/           # Reusable components
│       │   ├── pages/                # Next.js pages
│       │   ├── hooks/                # React hooks
│       │   ├── services/             # API services
│       │   ├── store/                # Redux store
│       │   ├── types/                # TypeScript types
│       │   ├── styles/               # Global styles
│       │   ├── utils/                # Utility functions
│       │   └── app.tsx               # App entry
│       ├── public/                   # Static assets
│       ├── .env.example
│       ├── tsconfig.json
│       ├── next.config.js
│       ├── package.json
│       ├── tailwind.config.js
│       ├── postcss.config.js
│       └── Dockerfile
│
├── packages/
│   ├── shared/                       # Shared code
│   │   ├── src/
│   │   │   ├── types/                # Shared TypeScript types
│   │   │   ├── constants/            # Shared constants
│   │   │   └── utils/                # Shared utilities
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── sdk/                          # AdCrewOS SDK
│       ├── src/
│       │   ├── client.ts             # SDK client
│       │   ├── index.ts
│       │   └── types.ts
│       ├── package.json
│       └── tsconfig.json
│
├── docs/
│   ├── ARCHITECTURE.md               # Architecture overview
│   ├── API.md                        # API documentation
│   ├── DATABASE.md                   # Database schema docs
│   ├── DEVELOPMENT.md                # Development guide
│   ├── DEPLOYMENT.md                 # Deployment guide
│   ├── SECURITY.md                   # Security guidelines
│   └── CONTRIBUTING.md               # Contributing guidelines
│
├── docker-compose.yml                # Docker Compose for local dev
├── .env.example                      # Environment variables template
├── .gitignore
├── package.json                      # Root package.json (Turborepo)
├── turbo.json                        # Turborepo config
├── tsconfig.json                     # Root TypeScript config
└── README.md
```

## Quick Start Commands

Before running these commands, you need to:

1. Create the directory structure:
```bash
mkdir -p apps/api/src apps/api/prisma apps/api/tests
mkdir -p apps/web/src apps/web/public
mkdir -p packages/shared/src packages/sdk/src
mkdir -p docs
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
```

4. Setup database:
```bash
cd apps/api
npm run db:generate
npm run db:migrate
```

5. Start development servers:
```bash
npm run dev
```

## Core Technologies

### Backend (apps/api)
- **Runtime:** Node.js 18+
- **Framework:** Express.js 4.18+
- **Language:** TypeScript 5+
- **Database ORM:** Prisma 5+
- **Authentication:** JWT + OAuth 2.0
- **API Validation:** Zod/Joi
- **Testing:** Jest
- **Real-time:** Socket.io
- **Logging:** Pino

### Frontend (apps/web)
- **Framework:** Next.js 14+
- **Language:** TypeScript 5+
- **Styling:** Tailwind CSS
- **UI Components:** shadcn/ui
- **State Management:** Redux Toolkit / TanStack Query
- **HTTP Client:** Axios
- **Real-time:** Socket.io-client
- **Testing:** Jest + React Testing Library
- **Charts:** Recharts

### Shared (packages/shared)
- TypeScript types
- Constants (pricing, thresholds, etc.)
- Utility functions
- Configuration schemas

## Environment Variables Template

Create `.env.example` in root and each app with these variables:

### API Environment (.env)
```
NODE_ENV=development
PORT=3001
DATABASE_URL=postgresql://user:password@localhost:5432/adcrewos
JWT_SECRET=your-super-secret-jwt-key
JWT_REFRESH_SECRET=your-super-secret-refresh-key
JWT_EXPIRY=15m
JWT_REFRESH_EXPIRY=7d

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# PayPal (optional)
PAYPAL_CLIENT_ID=...
PAYPAL_SECRET=...

# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=...
GOOGLE_ADS_CLIENT_ID=...
GOOGLE_ADS_CLIENT_SECRET=...

# Meta Ads API
META_APP_ID=...
META_APP_SECRET=...
META_BUSINESS_ACCOUNT_ID=...

# Twilio (SMS)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...

# SendGrid (Email)
SENDGRID_API_KEY=...
SENDGRID_FROM_EMAIL=noreply@adcrewos.com

# Sentry
SENTRY_DSN=...

# Session
SESSION_SECRET=...
```

### Web Environment (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_APP_NAME=AdCrewOS
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Implementation Roadmap

This project is built in phases. See `plan.md` in the session state for the complete roadmap.

### Phase 1: Foundation (Complete these first)
- [ ] Monorepo setup (Turborepo)
- [ ] Database schema (Prisma)
- [ ] Authentication system (JWT)
- [ ] Payment integration (Stripe)

### Phase 2: Core Dashboard
- [ ] Dashboard layout
- [ ] Google Ads OAuth
- [ ] Meta Ads OAuth
- [ ] Metrics display

### Phase 3: Analytics & Reporting
- [ ] Performance charts
- [ ] Report generation
- [ ] Scheduled delivery

### Phase 4: Alerts & Automation
- [ ] Alert rules engine
- [ ] SMS alerts
- [ ] Email alerts
- [ ] Auto-pause/increase logic

### Phase 5+
- [ ] Onboarding flow
- [ ] Team management
- [ ] Testing & optimization
- [ ] Production deployment

## File Creation Instructions

All files referenced in this document need to be created. Start with:

1. Configuration files (tsconfig, package.json, etc.)
2. Core types and constants
3. Database schema (Prisma)
4. Authentication system
5. API routes and controllers
6. Frontend components
7. Tests and documentation

See the plan.md for detailed implementation tasks.

## Next Steps

1. Create all directories referenced above
2. Copy this file and place it in the project root
3. Install dependencies: `npm install`
4. Start implementing according to the phase breakdown
5. Refer to individual docs as you progress

Good luck with AdCrewOS! 🚀
