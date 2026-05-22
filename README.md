# AdCrewOS - Unified Ad Account Management Platform

## 📊 Production-Ready SaaS for Ad Account Management

AdCrewOS is a comprehensive SaaS platform designed for small business owners, freelancers, small agencies, and solopreneurs to autonomously manage ad accounts across Google Ads and Meta (Facebook) in one unified dashboard.

### ✨ Key Features

- **Unified Dashboard** - Monitor all ad accounts and campaigns in one place
- **Real-time Alerts** - SMS and email notifications for campaign performance thresholds
- **Automated Reports** - Scheduled, downloadable reports (PDF, CSV, JSON)
- **3-Step Onboarding** - Easy setup: connect accounts → set goals → configure thresholds
- **Autonomous Automation** - Auto-pause underperforming campaigns or increase ad spend
- **Payment Integration** - Stripe and PayPal support with flexible pricing tiers
- **Free 7-Day Trial** - No credit card required to get started
- **Team Collaboration** - Multi-user access with role-based permissions (Agency tier)

### 💰 Pricing

- **Solo** - $49/month + 2% of ad spend (perfect for freelancers & small businesses)
- **Agency** - $199/month + 1% of ad spend (includes team management)

### 🎨 Brand Identity

- Modern dark theme with cyan/turquoise accents
- Clean, intuitive UI following AdCrewOS brand guidelines
- Responsive design for desktop, tablet, and mobile
- Accessibility-first component design

### 🚀 Quick Start

#### Prerequisites
- Node.js 18+
- npm or yarn
- PostgreSQL 14+
- Optional: Docker & Docker Compose

#### Development Setup (Windows)

1. **Initialize project structure:**
   ```bash
   .\init.bat
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   copy .env.example .env.local
   cd apps\api
   copy .env.example .env
   cd ..\web
   copy .env.example .env
   cd ..\..
   ```

4. **Setup database:**
   ```bash
   cd apps\api
   npm run db:generate
   npm run db:migrate dev --name init
   cd ..\..
   ```

5. **Start development servers:**
   ```bash
   npm run dev
   ```

The application will be available at:
- **Frontend:** http://localhost:3000
- **API:** http://localhost:3001

#### Development Setup (macOS/Linux)

1. **Initialize project structure:**
   ```bash
   chmod +x init.sh
   ./init.sh
   ```

2. **Follow steps 2-5 above** (same commands work on all platforms)

#### Docker Setup

```bash
# Copy environment files
copy .env.example .env.local
cd apps\api && copy .env.example .env
cd ../web && copy .env.example .env
cd ../..

# Start with Docker Compose
docker-compose up -d

# Run database migrations
docker-compose exec api npm run db:migrate dev --name init
```

### 📚 Documentation

- [Setup Guide](./SETUP_GUIDE.md) - Detailed project structure
- [File Structure](./FILE_STRUCTURE_COMPLETE.md) - Complete file contents
- [Architecture Guide](./docs/ARCHITECTURE.md) - System design and components
- [API Documentation](./docs/API.md) - API endpoints and integration
- [Database Schema](./docs/DATABASE.md) - Data models and relationships
- [Development Guide](./docs/DEVELOPMENT.md) - Development workflows
- [Deployment Guide](./docs/DEPLOYMENT.md) - Production deployment
- [Implementation Plan](./plan.md) - Project roadmap (in session state)

### 🏗️ Technology Stack

**Frontend:**
- Next.js 14+ with React 18+
- TypeScript
- Tailwind CSS
- Redux Toolkit + RTK Query
- Recharts for analytics
- Socket.io for real-time updates

**Backend:**
- Node.js 18+ with Express.js
- TypeScript
- Prisma ORM
- PostgreSQL
- Redis for caching
- JWT + OAuth 2.0 authentication
- Stripe API for payments
- Twilio for SMS
- SendGrid for emails

**DevOps:**
- Docker & Docker Compose
- Turborepo for monorepo management
- AWS deployment (ECS, RDS, S3)
- GitHub Actions for CI/CD

### 📁 Project Structure

```
adcrewos/
├── apps/
│   ├── api/              # Node.js + Express backend
│   └── web/              # React + Next.js frontend
├── packages/
│   ├── shared/           # Shared types and constants
│   └── sdk/              # AdCrewOS SDK
├── docs/                 # Documentation
├── docker-compose.yml    # Docker Compose configuration
└── README.md
```

### 🔐 Security Features

- JWT-based authentication with refresh tokens
- OAuth 2.0 for ad platform integrations
- Encrypted API keys and secrets
- Rate limiting and CSRF protection
- HTTPS/TLS encryption
- SQL injection prevention (Prisma)
- XSS protection (React built-in)
- Regular security audits
- Data encryption at rest

### 📊 Monitoring & Observability

- Error tracking with Sentry
- Infrastructure monitoring with Datadog
- Real-time application logging with Pino
- Performance monitoring with Prometheus
- Health checks and status pages

### 🤝 Contributing

This project is part of the AdCrewOS initiative. For contribution guidelines, see [CONTRIBUTING.md](./docs/CONTRIBUTING.md)

### 📄 License

MIT License - see LICENSE file for details

### 🌐 Links

- **Website:** https://adcrewos.com
- **Documentation:** https://docs.adcrewos.com
- **Support:** support@adcrewos.com
- **Status Page:** https://status.adcrewos.com

### 🛠️ Development Commands

```bash
# Development
npm run dev              # Start all dev servers
npm run dev:api         # Start API only
npm run dev:web         # Start web only

# Building
npm run build            # Build all apps
npm run build:api       # Build API
npm run build:web       # Build web

# Testing & Linting
npm run test            # Run all tests
npm run lint            # Lint all code
npm run type-check      # TypeScript type checking

# Database
cd apps/api && npm run db:migrate dev    # Create new migration
cd apps/api && npm run db:push           # Sync schema to database
cd apps/api && npm run db:reset          # Reset database

# Docker
docker-compose up       # Start all services
docker-compose down     # Stop all services
docker-compose logs -f  # View logs
```

### 📖 Next Steps

1. **Read the Setup Guide** to understand the project structure
2. **Run init.bat** (Windows) or init.sh (macOS/Linux) to create directories
3. **Install dependencies** with npm install
4. **Setup environment variables** from the .env.example files
5. **Start development** with npm run dev
6. **Review the Architecture Guide** to understand the system design
7. **Begin implementing features** according to the implementation plan

### 🎯 Implementation Roadmap

See [plan.md](./plan.md) in the session state folder for the complete phase-by-phase implementation roadmap:

- **Phase 1:** Foundation & authentication
- **Phase 2:** Dashboard core features
- **Phase 3:** Analytics & reporting
- **Phase 4:** Alerts & automation
- **Phase 5:** 3-step onboarding
- **Phase 6:** Team collaboration
- **Phase 7:** Testing & optimization
- **Phase 8:** Production deployment

---

**Built with ❤️ for small business ad management**

*AdCrewOS - Automate, Monitor, Scale Your Ad Accounts*
Automously manage ad accounts across multiple platforms with a unified dashboard, real-time anomoly alerts, and scheduled reporting. Made especially for small business owners, freelancers, and small agencies.
