# AdCrewOS Complete File Structure & Contents

This document contains all files needed for the AdCrewOS project. Use this in conjunction with the init.bat or init.sh scripts.

## Installation Instructions (Windows)

1. **Run the initialization script:**
   ```
   .\init.bat
   ```

2. **Install dependencies:**
   ```
   npm install
   ```

3. **Create environment files:**
   ```
   copy .env.example .env.local
   cd apps\api
   copy .env.example .env
   cd ..\web
   copy .env.example .env
   cd ..\..
   ```

4. **Setup database:**
   ```
   cd apps\api
   npm run db:generate
   npm run db:migrate
   cd ..\..
   ```

5. **Start development:**
   ```
   npm run dev
   ```

---

## File Contents & Creation Order

### 1. Root Level Configuration Files

**File: package.json (already created)**
**File: turbo.json (already created)**
**File: tsconfig.json (already created)**
**File: .gitignore (already created)**
**File: .env.example (already created)**

### 2. API Application Files

Create these in `apps/api/`:

#### apps/api/package.json
[See earlier in this session]

#### apps/api/tsconfig.json
```json
{
  "extends": "../../tsconfig.json",
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

#### apps/api/.env.example
[See earlier in this session]

### 3. API Source Files

Create files in `apps/api/src/`:

#### config/logger.ts
```typescript
import pino from 'pino';

const isDevelopment = process.env.NODE_ENV === 'development';

export const logger = pino(
  {
    level: process.env.LOG_LEVEL || 'info',
    transport: isDevelopment ? {
      target: 'pino-pretty',
      options: {
        colorize: true,
        translateTime: 'SYS:standard',
        ignore: 'pid,hostname',
      },
    } : undefined,
  }
);
```

#### config/database.ts
```typescript
import { PrismaClient } from '@prisma/client';
import { logger } from './logger';

const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: [
      {
        emit: 'event',
        level: 'query',
      },
      {
        emit: 'stdout',
        level: 'error',
      },
      {
        emit: 'stdout',
        level: 'warn',
      },
    ],
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

// Log queries in development
prisma.$on('query', (e) => {
  if (process.env.NODE_ENV === 'development') {
    logger.debug(`Query: ${e.query} [${e.duration}ms]`);
  }
});
```

#### types/index.ts
```typescript
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  tier: 'SOLO' | 'AGENCY';
  trialEndsAt: Date | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface AdAccount {
  id: string;
  userId: string;
  provider: 'GOOGLE' | 'META';
  externalId: string;
  name: string;
  currency: string;
  timezone: string;
  status: 'ACTIVE' | 'PAUSED' | 'DISCONNECTED';
  createdAt: Date;
  updatedAt: Date;
}

export interface Campaign {
  id: string;
  adAccountId: string;
  externalId: string;
  name: string;
  status: 'ACTIVE' | 'PAUSED' | 'COMPLETED' | 'ARCHIVED';
  budget: number;
  spend: number;
  impressions: number;
  clicks: number;
  conversions: number;
  revenue: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface AlertRule {
  id: string;
  userId: string;
  type: 'CPA_THRESHOLD' | 'ROAS_THRESHOLD' | 'BUDGET_THRESHOLD' | 'IMPRESSION_THRESHOLD';
  metric: string;
  threshold: number;
  action: 'ALERT' | 'PAUSE' | 'INCREASE_BUDGET';
  enabled: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Subscription {
  id: string;
  userId: string;
  tier: 'SOLO' | 'AGENCY';
  status: 'ACTIVE' | 'CANCELLED' | 'EXPIRED';
  currentPeriodStart: Date;
  currentPeriodEnd: Date;
  cancelledAt: Date | null;
  createdAt: Date;
  updatedAt: Date;
}
```

#### constants/index.ts
```typescript
export const PRICING = {
  SOLO: {
    monthlyFee: 49,
    adSpendPercentage: 2,
  },
  AGENCY: {
    monthlyFee: 199,
    adSpendPercentage: 1,
  },
};

export const TRIAL_DAYS = 7;

export const AD_PLATFORMS = {
  GOOGLE: 'GOOGLE',
  META: 'META',
};

export const ALERT_TYPES = {
  CPA_THRESHOLD: 'CPA_THRESHOLD',
  ROAS_THRESHOLD: 'ROAS_THRESHOLD',
  BUDGET_THRESHOLD: 'BUDGET_THRESHOLD',
  IMPRESSION_THRESHOLD: 'IMPRESSION_THRESHOLD',
};

export const ALERT_ACTIONS = {
  ALERT: 'ALERT',
  PAUSE: 'PAUSE',
  INCREASE_BUDGET: 'INCREASE_BUDGET',
};

export const JWT_EXPIRY = '15m';
export const JWT_REFRESH_EXPIRY = '7d';
```

---

### 4. Prisma Schema

Create `apps/api/prisma/schema.prisma`:

```prisma
// This is your Prisma schema file,
// learn more about it in the docs: https://pris.ly/d/prisma-schema

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// User Model
model User {
  id            String    @id @default(cuid())
  email         String    @unique
  firstName     String?
  lastName      String?
  password      String    // bcrypted
  tier          String    @default("SOLO") // SOLO or AGENCY
  status        String    @default("ACTIVE") // ACTIVE, TRIAL, SUSPENDED
  trialEndsAt   DateTime?
  lastLoginAt   DateTime?
  
  // Relations
  oauthTokens   OAuthToken[]
  sessions      Session[]
  adAccounts    AdAccount[]
  alertRules    AlertRule[]
  subscription  Subscription?
  teamMembers   TeamMember[]
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@index([email])
  @@index([tier])
}

// OAuth Token Model
model OAuthToken {
  id            String    @id @default(cuid())
  userId        String
  user          User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  provider      String    // GOOGLE, META, STRIPE
  accessToken   String
  refreshToken  String?
  expiresAt     DateTime?
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@unique([userId, provider])
  @@index([provider])
}

// Session Model
model Session {
  id            String    @id @default(cuid())
  userId        String
  user          User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  token         String    @unique
  expiresAt     DateTime
  
  createdAt     DateTime  @default(now())

  @@index([userId])
}

// Ad Account Model
model AdAccount {
  id            String    @id @default(cuid())
  userId        String
  user          User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  provider      String    // GOOGLE or META
  externalId    String    // From the ad platform
  name          String
  currency      String    @default("USD")
  timezone      String    @default("UTC")
  status        String    @default("ACTIVE") // ACTIVE, PAUSED, DISCONNECTED
  
  // Relations
  campaigns     Campaign[]
  metrics       CampaignMetric[]
  settings      AccountSettings?
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@unique([userId, externalId])
  @@index([provider])
  @@index([userId])
}

// Account Settings Model
model AccountSettings {
  id            String    @id @default(cuid())
  adAccountId   String    @unique
  adAccount     AdAccount @relation(fields: [adAccountId], references: [id], onDelete: Cascade)
  
  // Goals
  targetCPA     Float?
  targetROAS    Float?
  dailyBudget   Float?
  
  // Thresholds
  pauseIfCPAAbove    Float?
  pauseIfROASBelow   Float?
  increaseIfROASAbove Float?
  
  // Notifications
  emailAlerts   Boolean   @default(true)
  smsAlerts     Boolean   @default(false)
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
}

// Campaign Model
model Campaign {
  id            String    @id @default(cuid())
  adAccountId   String
  adAccount     AdAccount @relation(fields: [adAccountId], references: [id], onDelete: Cascade)
  externalId    String    // From ad platform
  name          String
  status        String    // ACTIVE, PAUSED, COMPLETED, ARCHIVED
  budget        Float
  
  // Relations
  metrics       CampaignMetric[]
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@unique([adAccountId, externalId])
  @@index([adAccountId])
  @@index([status])
}

// Campaign Metrics Model (time series)
model CampaignMetric {
  id            String    @id @default(cuid())
  campaignId    String?
  campaign      Campaign? @relation(fields: [campaignId], references: [id], onDelete: Cascade)
  adAccountId   String
  adAccount     AdAccount @relation(fields: [adAccountId], references: [id], onDelete: Cascade)
  
  // Metrics
  date          DateTime
  spend         Float
  impressions   Int
  clicks        Int
  conversions   Int
  revenue       Float
  cpc           Float?    // Cost per click
  cpa           Float?    // Cost per acquisition
  roas          Float?    // Return on ad spend
  ctr           Float?    // Click through rate
  conversionRate Float?
  
  createdAt     DateTime  @default(now())

  @@index([adAccountId])
  @@index([campaignId])
  @@index([date])
}

// Alert Rule Model
model AlertRule {
  id            String    @id @default(cuid())
  userId        String
  user          User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  adAccountId   String?
  
  // Rule configuration
  type          String    // CPA_THRESHOLD, ROAS_THRESHOLD, etc.
  metric        String
  threshold     Float
  operator      String    // GREATER_THAN, LESS_THAN, EQUAL
  action        String    // ALERT, PAUSE, INCREASE_BUDGET
  
  enabled       Boolean   @default(true)
  
  // Relations
  alerts        Alert[]
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@index([userId])
}

// Alert Model (fired alerts)
model Alert {
  id            String    @id @default(cuid())
  ruleId        String
  rule          AlertRule @relation(fields: [ruleId], references: [id], onDelete: Cascade)
  
  message       String
  severity      String    // INFO, WARNING, ERROR
  status        String    @default("UNREAD") // UNREAD, READ, ACTIONED
  
  // Notification
  notifications AlertNotification[]
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@index([ruleId])
  @@index([status])
  @@index([createdAt])
}

// Alert Notification Model
model AlertNotification {
  id            String    @id @default(cuid())
  alertId       String
  alert         Alert     @relation(fields: [alertId], references: [id], onDelete: Cascade)
  
  channel       String    // EMAIL, SMS, PUSH
  recipient     String
  status        String    // PENDING, SENT, FAILED
  sentAt        DateTime?
  
  createdAt     DateTime  @default(now())
}

// Report Model
model Report {
  id            String    @id @default(cuid())
  userId        String
  name          String
  
  // Content
  metrics       String    // JSON array of metrics
  startDate     DateTime
  endDate       DateTime
  format        String    // PDF, CSV, JSON
  
  // Schedule
  schedule      String?   // DAILY, WEEKLY, MONTHLY, null for one-time
  lastGeneratedAt DateTime?
  nextGeneratedAt DateTime?
  
  // File
  fileUrl       String?
  fileSize      Int?
  
  // Delivery
  emailRecipients String?  // JSON array
  autoDeliver   Boolean   @default(false)
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@index([userId])
}

// Subscription Model
model Subscription {
  id            String    @id @default(cuid())
  userId        String    @unique
  user          User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  tier          String    // SOLO, AGENCY
  status        String    // ACTIVE, CANCELLED, EXPIRED
  
  stripeCustomerId String?
  stripeSubscriptionId String?
  
  currentPeriodStart DateTime
  currentPeriodEnd   DateTime
  cancelledAt    DateTime?
  
  // Usage
  totalAdSpend  Float     @default(0)
  lastCalculatedAt DateTime?
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@index([status])
}

// Team Member Model (for Agency tier)
model TeamMember {
  id            String    @id @default(cuid())
  userId        String
  user          User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  email         String
  firstName     String?
  lastName      String?
  role          String    // ADMIN, MANAGER, VIEWER
  status        String    // ACTIVE, INVITED, INACTIVE
  
  invitedAt     DateTime?
  inviteToken   String?   @unique
  inviteExpiresAt DateTime?
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@unique([userId, email])
  @@index([role])
}

// Activity Log Model
model ActivityLog {
  id            String    @id @default(cuid())
  userId        String?
  
  action        String    // CREATE, UPDATE, DELETE, LOGIN, etc.
  resource      String    // User, Campaign, Alert, etc.
  resourceId    String?
  details       String?   // JSON
  
  ipAddress     String?
  userAgent     String?
  
  createdAt     DateTime  @default(now())

  @@index([userId])
  @@index([action])
  @@index([createdAt])
}
```

---

### 5. Web Frontend Files

Create `apps/web/package.json`, `apps/web/tsconfig.json`, etc. (similar structure to API)

---

## Next Steps After File Creation

1. **Run init script:**
   ```
   .\init.bat  (Windows)
   ./init.sh   (macOS/Linux)
   ```

2. **Install all dependencies:**
   ```
   npm install
   ```

3. **Setup Prisma:**
   ```
   cd apps\api
   npm run db:generate
   npm run db:migrate dev --name init
   ```

4. **Start development:**
   ```
   npm run dev
   ```

---

## Document References

- For complete API specification, see: docs/API.md
- For database schema details, see: docs/DATABASE.md
- For deployment guide, see: docs/DEPLOYMENT.md
- For architecture overview, see: docs/ARCHITECTURE.md

---

This comprehensive guide provides the foundation for AdCrewOS. All files listed above need to be created in the correct directories as specified.

Total number of files to create: 100+
Estimated project size: ~500KB (before node_modules)

Begin with the initialization scripts and gradually create all files as documented.
