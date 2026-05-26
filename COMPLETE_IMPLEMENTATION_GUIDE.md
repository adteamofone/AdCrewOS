# AdCrewOS Complete Implementation Roadmap & Documentation

This file consolidates all critical documentation needed for the project.

## Part 1: Quick Start Guide

### For Windows Users:
```batch
REM 1. Run initialization script to create folders
.\init.bat

REM 2. Install dependencies
npm install

REM 3. Setup environment files
copy .env.example .env.local
cd apps\api
copy .env.example .env
cd ..\web
copy .env.example .env
cd ..\..

REM 4. Setup database
cd apps\api
npm run db:generate
npm run db:migrate dev --name init
cd ..\..

REM 5. Start development
npm run dev
```

### For macOS/Linux Users:
```bash
# 1. Run initialization script to create folders
chmod +x init.sh
./init.sh

# 2. Install dependencies
npm install

# 3. Setup environment files
cp .env.example .env.local
cd apps/api && cp .env.example .env
cd ../web && cp .env.example .env
cd ../..

# 4. Setup database
cd apps/api
npm run db:generate
npm run db:migrate dev --name init
cd ../..

# 5. Start development
npm run dev
```

## Part 2: Project Architecture

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Client Layer                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Next.js Web App │         │  Mobile (Future) │         │
│  │  React Components│         │  React Native    │         │
│  └────────┬─────────┘         └────────┬─────────┘         │
└───────────┼──────────────────────────────┼──────────────────┘
            │                              │
    ┌───────┴──────┐                ┌──────┴────────┐
    │              │                │               │
    │  REST API    │            WebSocket Events   │
    │  (REST)      │            (Socket.io)        │
    │              │                │               │
    └───────┬──────┘                └──────┬────────┘
            │                              │
┌───────────▼──────────────────────────────▼───────────────┐
│          Express.js Backend Server                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Authentication → Services → Data Layer (ORM)   │   │
│  └─────────────────────────────────────────────────┘   │
└───────────┬─────────────────────────────────────────────┘
            │
    ┌───────┼───────────────────┐
    │       │                   │
    ▼       ▼                   ▼
  PostgreSQL Redis         External APIs
  (Database) (Cache)       (Google, Meta, Stripe)
```

### Technology Stack

**Frontend (apps/web):**
- React 18+ with TypeScript
- Next.js 14+ (SSR/SSG)
- Tailwind CSS for styling
- Redux Toolkit for state management
- Recharts for analytics visualization
- Socket.io-client for real-time updates

**Backend (apps/api):**
- Node.js 18+ with Express.js
- TypeScript for type safety
- Prisma ORM for database
- PostgreSQL for persistence
- Redis for caching/sessions
- JWT + OAuth 2.0 for authentication

**DevOps:**
- Docker & Docker Compose for local development
- GitHub Actions for CI/CD
- AWS for cloud deployment (ECS, RDS, S3)
- Vercel for frontend deployment

## Part 3: Core Features Implementation

### 1. Three-Step Onboarding Flow

```
User Registration
       ↓
Free 7-Day Trial Activated
       ↓
Step 1: Connect Ad Accounts
  - Google Ads OAuth
  - Meta Facebook OAuth
       ↓
Step 2: Set Performance Goals
  - Target CPA
  - Target ROAS
  - Daily Budget
       ↓
Step 3: Configure Thresholds
  - Pause if CPA > X
  - Auto-increase if ROAS > X
  - Alert notification preferences
       ↓
Access to Dashboard
```

### 2. Unified Dashboard Features

```
┌─────────────────────────────────────────┐
│  AdCrewOS Dashboard                     │
├─────────────────────────────────────────┤
│                                         │
│  Key Metrics (Cards)                    │
│  ├─ Total Spend: $12,847                │
│  ├─ ROAS: 3.2x                          │
│  ├─ Active Campaigns: 14                │
│  └─ Alerts: 2 (NEW)                    │
│                                         │
│  Performance Chart (Multi-Account)      │
│  ├─ Spend Trend                         │
│  ├─ Revenue Trend                       │
│  └─ ROAS Trend                          │
│                                         │
│  Campaign Table                         │
│  ├─ Campaign Name                       │
│  ├─ Status (Active/Paused)              │
│  ├─ Spend                               │
│  ├─ CPA                                 │
│  └─ ROAS                                │
│                                         │
└─────────────────────────────────────────┘
```

### 3. Real-Time Alerts System

```
Monitoring Loop (Every 5 minutes)
    ↓
Fetch Metrics from Ad Platforms
    ↓
Check Against User's Alert Rules
    ↓
Rule Triggered? → NO → Wait 5 mins
    ↓ YES
Create Alert Record
    ↓
Send Notifications (Email/SMS)
    ↓
Execute Auto-Actions (Pause/Increase)
    ↓
Log Activity
```

### 4. Automated Report Generation

```
Scheduled Report Trigger (Daily/Weekly/Monthly)
    ↓
Aggregate Metrics from Database
    ↓
Generate PDF/CSV/JSON
    ↓
Upload to Cloud Storage (S3)
    ↓
Send Email with Download Link
    ↓
Store Report Record
```

### 5. Billing & Subscriptions

```
User Signup
    ↓
Select Plan (Solo or Agency)
    ↓
Stripe Payment Processing
    ↓
Subscription Record Created
    ↓
7-Day Trial Period Starts
    ↓
    ├─ Day 7: Trial Ending Reminder
    ├─ Day 8: Charge Credit Card
    │   └─ If Failed: Retry Logic (3 attempts)
    └─ Monthly: Bill for Ad Spend %
```

## Part 4: API Endpoints Structure

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user

### Ad Account Endpoints
- `GET /api/v1/ad-accounts` - List user's ad accounts
- `POST /api/v1/ad-accounts` - Connect new ad account
- `GET /api/v1/ad-accounts/:id` - Get specific account
- `DELETE /api/v1/ad-accounts/:id` - Disconnect account
- `GET /api/v1/ad-accounts/:id/campaigns` - Get campaigns

### Campaign Endpoints
- `GET /api/v1/campaigns` - List all campaigns
- `GET /api/v1/campaigns/:id` - Get campaign details
- `PATCH /api/v1/campaigns/:id` - Update campaign
- `GET /api/v1/campaigns/:id/metrics` - Get performance metrics

### Alert Endpoints
- `GET /api/v1/alerts` - List alerts
- `POST /api/v1/alerts/rules` - Create alert rule
- `GET /api/v1/alerts/rules` - List alert rules
- `PATCH /api/v1/alerts/rules/:id` - Update rule
- `DELETE /api/v1/alerts/rules/:id` - Delete rule

### Report Endpoints
- `GET /api/v1/reports` - List scheduled reports
- `POST /api/v1/reports` - Create new report
- `GET /api/v1/reports/:id/download` - Download report
- `DELETE /api/v1/reports/:id` - Delete report

### Billing Endpoints
- `GET /api/v1/billing/subscription` - Get subscription info
- `POST /api/v1/billing/upgrade` - Change subscription tier
- `GET /api/v1/billing/invoices` - Get invoice history
- `POST /api/v1/billing/payment-method` - Update payment method

## Part 5: Database Schema (Prisma Models)

See FILE_STRUCTURE_COMPLETE.md for complete Prisma schema.

Key tables:
- `User` - User accounts
- `OAuthToken` - OAuth credentials
- `AdAccount` - Connected ad accounts
- `Campaign` - Ad campaigns
- `CampaignMetric` - Time-series metrics data
- `AlertRule` - User-defined alert rules
- `Alert` - Fired alerts
- `Subscription` - Billing information
- `TeamMember` - Team collaboration (Agency tier)
- `Report` - Scheduled reports
- `ActivityLog` - Audit trail

## Part 6: Security Implementation

### Authentication Flow
```
User Login
    ↓
Verify Email/Password (bcrypt)
    ↓
Generate JWT Access Token (15m expiry)
    ↓
Generate JWT Refresh Token (7d expiry)
    ↓
Store Refresh Token in HTTP-only Cookie
    ↓
Return Access Token + User Data
    ↓
Client stores Access Token in Memory
    ↓
Send Access Token in Authorization Header
```

### OAuth Integration Flow
```
User Clicks "Connect Google Ads"
    ↓
Redirect to Google OAuth Consent Screen
    ↓
User Grants Permissions
    ↓
Google redirects with Authorization Code
    ↓
Backend exchanges Code for Access Token
    ↓
Store Access Token (encrypted)
    ↓
Store Refresh Token (encrypted)
    ↓
User sees connected account in dashboard
```

### Data Protection
- All passwords hashed with bcrypt
- API keys encrypted at rest
- OAuth tokens stored securely
- HTTPS/TLS in production
- Rate limiting on API endpoints
- CORS configured for trusted origins
- SQL injection prevention via Prisma
- XSS protection via React
- CSRF tokens for state-changing operations

## Part 7: Real-Time Architecture

### WebSocket Events

**Client → Server:**
```typescript
// Join user's dashboard
socket.emit('join-dashboard', userId)

// Subscribe to campaign updates
socket.emit('subscribe-campaign', campaignId)

// Get live metrics
socket.emit('request-metrics', { campaignId })
```

**Server → Client:**
```typescript
// Broadcast alert
io.to(`dashboard-${userId}`).emit('alert', alertData)

// Send metric update
io.to(`dashboard-${userId}`).emit('metrics-update', metricsData)

// Send campaign status change
io.to(`campaign-${campaignId}`).emit('status-changed', newStatus)
```

## Part 8: Deployment Architecture

### Production Environment

```
┌─────────────────────────────────────────────────────┐
│            CloudFront CDN                           │
│         (Static Assets & Caching)                   │
└────────────┬─────────────────────────────┬──────────┘
             │                             │
         ┌───▼──────┐                ┌────▼──────┐
         │  Vercel  │                │AWS API    │
         │  (Next.js)               │Gateway    │
         └───┬──────┘                └────┬──────┘
             │                           │
             └───────────────┬───────────┘
                             │
                    ┌────────▼────────┐
                    │  AWS ECS        │
                    │  (Docker)       │
                    │  (API Servers)  │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐          ┌───▼────┐        ┌────▼────┐
    │PostgreSQL          Redis        S3        │
    │(RDS)      │        ElastiCache│           │
    │Database   │        Cache       │           │
    └──────────┘        └──────────┘        ┌──────────┐
                                             │Cloudwatch
                                             │Monitoring
                                             └──────────┘
```

### Deployment Steps

1. **Code Push to GitHub**
2. **GitHub Actions runs tests & builds**
3. **Docker images created**
4. **Images pushed to AWS ECR**
5. **ECS service updated with new images**
6. **Database migrations run**
7. **Health checks confirm success**
8. **Rollback on failure**

## Part 9: Monitoring & Observability

### Key Metrics to Monitor
- API response times (target: < 200ms)
- Database query performance
- Error rates (target: < 0.1%)
- System uptime (target: 99.9%)
- WebSocket connection count
- Cache hit ratio

### Alerting Rules
- High error rate (> 5%)
- API response slow (> 1s)
- Database connection pool exhausted
- Disk space low (< 10%)
- Service down (0 available instances)

### Logging Strategy
- Application logs: JSON format via Pino
- Request/Response logs: All API calls
- Error logs: Stack traces and context
- Audit logs: User actions
- Performance logs: Query times and metrics

## Part 10: Testing Strategy

### Unit Tests
- Services: Business logic tests
- Utils: Utility function tests
- Models: Database logic tests

### Integration Tests
- API endpoints: Full request/response cycle
- Database: CRUD operations
- Authentication: OAuth flow

### E2E Tests
- Complete user flows: Registration → Dashboard → Campaign Management
- Critical paths: Payment processing, alert triggering
- Error scenarios: Invalid input, network failures

### Test Coverage Target
- Overall: 80%+
- Critical paths: 100%
- Services: 85%+
- Utils: 75%+

## Part 11: Scaling & Performance

### Horizontal Scaling
- Stateless API design (deployable on multiple nodes)
- Load balancing (AWS ALB)
- Database replication
- Redis cluster for high availability

### Performance Optimization
- API response caching (1 hour for metrics)
- Database query optimization
- CDN for static assets
- Code splitting on frontend
- Image optimization
- Compression (gzip)

### Database Optimization
- Connection pooling (RDS Proxy)
- Query performance monitoring
- Index optimization
- Archive old metrics data
- Scheduled maintenance

## Part 12: Troubleshooting Guide

### Common Issues & Solutions

**Issue: Database connection refused**
```
Solution:
1. Check PostgreSQL is running
2. Verify DATABASE_URL in .env
3. Check database exists
4. Check username/password
```

**Issue: "Port already in use"**
```
Windows: netstat -ano | findstr :3001
         taskkill /PID <PID> /F
Mac/Linux: lsof -i :3001
           kill -9 <PID>
```

**Issue: Module not found errors**
```
Solution:
1. npm install
2. npm run build
3. Clear cache: npm run clean && npm install
```

**Issue: Prisma client outdated**
```
Solution:
cd apps/api
npm run db:generate
```

**Issue: OAuth token expired**
```
Solution:
1. Check token expiration logic
2. Implement refresh token rotation
3. Store tokens securely
4. Monitor token age
```

## Next Steps

1. ✅ Read this documentation file
2. ✅ Run the initialization script (init.bat or init.sh)
3. ✅ Install dependencies (npm install)
4. ✅ Setup environment variables
5. ✅ Start development (npm run dev)
6. ✅ Begin implementing Phase 1 features
7. ✅ Follow git workflow for contributions
8. ✅ Submit PR for review

---

**For questions or issues, refer to specific documentation files or the development guide.**

Last updated: 2024
AdCrewOS - Production Ad Account Management Platform
