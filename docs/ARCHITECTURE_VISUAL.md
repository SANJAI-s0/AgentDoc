# AgentDoc Architecture Visual Guide

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LANDING PAGE (Static)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  HTML5 + CSS3 + JavaScript + GSAP Animations         │  │
│  │  • Hero Section                                       │  │
│  │  • 5-Agent Workflow                                   │  │
│  │  • Features & Use Cases                               │  │
│  │  • Demo Link                                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  FRONTEND (React + Vite)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Dashboard  │  Documents  │  Reviews  │  Search      │  │
│  └──────────────────────────────────────────────────────┘  │
│  • Upload Documents                                          │
│  • Track Status                                              │
│  • Review Queue                                              │
│  • Semantic Search                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (Django + DRF)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  REST API Endpoints                                   │  │
│  │  • /api/auth/                                         │  │
│  │  • /api/documents/                                    │  │
│  │  • /api/reviews/                                      │  │
│  │  • /api/search/                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│  • JWT Authentication                                        │
│  • CORS Configuration                                        │
│  • Static File Serving (WhiteNoise)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              5-AGENT SYSTEM (CrewAI + Gemini)               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Classification Agent                              │  │
│  │     └─> Identifies document type                      │  │
│  │                                                        │  │
│  │  2. Extraction Agent                                  │  │
│  │     └─> Extracts structured data                      │  │
│  │                                                        │  │
│  │  3. Validation Agent                                  │  │
│  │     └─> Validates against rules                       │  │
│  │                                                        │  │
│  │  4. Routing Agent                                     │  │
│  │     └─> Routes to approve/review/exception            │  │
│  │                                                        │  │
│  │  5. Audit Agent                                       │  │
│  │     └─> Creates audit trail                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATA LAYER                                  │
│  ┌────────────────────┐  ┌────────────────────┐            │
│  │  MongoDB Atlas     │  │  Local Storage     │            │
│  │  • Documents       │  │  • Uploaded Files  │            │
│  │  • Extractions     │  │  • Media Files     │            │
│  │  • Reviews         │  │  • Temp Storage    │            │
│  │  • Audit Logs      │  │                    │            │
│  │  • Vector Search   │  │                    │            │
│  └────────────────────┘  └────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Landing Page Structure

```
landing-page/
│
├── index.html ─────────────┐
│                            │
├── css/                     │
│   ├── reset.css ──────────┼─> Browser normalization
│   ├── variables.css ──────┼─> Design tokens (colors, spacing)
│   ├── layout.css ─────────┼─> Grid systems, containers
│   ├── components.css ─────┼─> Buttons, cards, navigation
│   ├── sections.css ───────┼─> Hero, features, workflow
│   └── responsive.css ─────┼─> Media queries
│                            │
└── js/                      │
    ├── config.js ──────────┼─> Configuration
    ├── navigation.js ──────┼─> Menu, smooth scroll
    ├── main.js ────────────┼─> Initialization
    └── animations/         │
        ├── hero.js ────────┼─> Hero animations
        ├── sections.js ────┼─> Scroll triggers
        └── interactions.js ┼─> Hover effects
                            │
                            ▼
                    GSAP Library (CDN)
```

## 5-Agent Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCUMENT UPLOAD                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 1: CLASSIFICATION                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Input: Raw document                                  │  │
│  │  Process: AI identifies type                          │  │
│  │  Output: {type: "invoice", confidence: 0.95}          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 2: EXTRACTION                                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Input: Document + type                               │  │
│  │  Process: OCR + NLP extraction                        │  │
│  │  Output: {vendor, amount, date, items, ...}           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 3: VALIDATION                                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Input: Extracted data                                │  │
│  │  Process: Business rules + semantic checks            │  │
│  │  Output: {valid: true, issues: [], confidence: 0.92}  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 4: ROUTING                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Input: Validated data + confidence                   │  │
│  │  Process: Risk assessment                             │  │
│  │  Output: Decision (auto-approve/review/exception)     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │  AUTO    │  │  HUMAN   │  │ EXCEPTION│
        │ APPROVE  │  │  REVIEW  │  │ HANDLING │
        └──────────┘  └──────────┘  └──────────┘
                │             │             │
                └─────────────┼─────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 5: AUDIT                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Input: All decisions + actions                       │  │
│  │  Process: Create immutable log                        │  │
│  │  Output: Audit trail entry                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture (Render)

```
┌─────────────────────────────────────────────────────────────┐
│                        RENDER PLATFORM                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Static Site: agentdoc-landing                     │    │
│  │  • Serves landing-page/ directory                  │    │
│  │  • No build needed                                 │    │
│  │  • CDN caching                                     │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Web Service: agentdoc-backend                     │    │
│  │  • Python 3.11                                     │    │
│  │  • Gunicorn WSGI server                            │    │
│  │  • WhiteNoise static files                         │    │
│  │  • Local storage (ephemeral)                       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Web Service: agentdoc-frontend                    │    │
│  │  • Node 20.x                                       │    │
│  │  • Vite build + preview                            │    │
│  │  • Environment config                              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                         │
│                                                              │
│  ┌────────────────────┐  ┌────────────────────┐            │
│  │  MongoDB Atlas     │  │  Google Gemini     │            │
│  │  • Free M0 Cluster │  │  • API Key         │            │
│  │  • 512 MB Storage  │  │  • gemini-2.5-flash│            │
│  │  • Shared CPU      │  │  • Rate limits     │            │
│  └────────────────────┘  └────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
1. USER UPLOADS DOCUMENT
   │
   ▼
2. FRONTEND → BACKEND (POST /api/documents/upload/)
   │
   ▼
3. BACKEND SAVES TO LOCAL STORAGE
   │
   ▼
4. BACKEND TRIGGERS 5-AGENT WORKFLOW
   │
   ├─> Classification Agent (Gemini API)
   │   └─> Stores result in MongoDB
   │
   ├─> Extraction Agent (Gemini API)
   │   └─> Stores result in MongoDB
   │
   ├─> Validation Agent (Gemini API)
   │   └─> Stores result in MongoDB
   │
   ├─> Routing Agent (Gemini API)
   │   └─> Stores decision in MongoDB
   │
   └─> Audit Agent
       └─> Stores audit log in MongoDB
   │
   ▼
5. BACKEND RETURNS STATUS TO FRONTEND
   │
   ▼
6. FRONTEND DISPLAYS RESULT TO USER
```

## CSS Architecture

```
reset.css
  └─> Normalizes browser defaults

variables.css
  └─> Defines design tokens
      • Colors
      • Spacing
      • Shadows
      • Transitions

layout.css
  └─> Defines structure
      • Container
      • Grid systems
      • Section spacing

components.css
  └─> Defines reusable elements
      • Buttons
      • Cards
      • Navigation
      • Icons

sections.css
  └─> Defines section-specific styles
      • Hero
      • Features
      • Workflow
      • Demo

responsive.css
  └─> Defines breakpoints
      • Mobile (< 768px)
      • Tablet (768px - 1199px)
      • Desktop (1200px+)
```

## JavaScript Architecture

```
config.js
  └─> Configuration
      • Demo URL
      • Animation settings
      • GSAP registration

navigation.js
  └─> Navigation functionality
      • Scroll effects
      • Mobile menu
      • Smooth scroll

animations/
  ├─> hero.js
  │   └─> Hero section animations
  │       • Text fade-in
  │       • Document cards
  │       • Counter animations
  │
  ├─> sections.js
  │   └─> Scroll-triggered animations
  │       • Section reveals
  │       • Card animations
  │       • Timeline steps
  │
  └─> interactions.js
      └─> Interactive animations
          • Button hovers
          • Card hovers

main.js
  └─> Initialization
      • Page load
      • Error handling
      • Logging
```

## Security Flow

```
┌─────────────────────────────────────────────────────────────┐
│  HTTPS (Render SSL)                                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  CORS Middleware                                             │
│  • Validates origin                                          │
│  • Allows credentials                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  CSRF Protection                                             │
│  • Token validation                                          │
│  • Secure cookies                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  JWT Authentication                                          │
│  • Token verification                                        │
│  • User identification                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Role-Based Access Control                                   │
│  • Customer: Upload, view own documents                      │
│  • Reviewer: Review queue, approve/reject                    │
│  • Admin: Full access                                        │
└─────────────────────────────────────────────────────────────┘
```

This visual guide provides a comprehensive overview of the AgentDoc architecture, from user interaction to data storage, with clear separation of concerns and modular design.
