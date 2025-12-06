<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./static/darkmode.png">
  <source media="(prefers-color-scheme: light)" srcset="./static/lightmode.png">
  <img alt="Ecomm Hacks Banner" src="./static/lightmode.png">
</picture>

---

## Team Name
**Ephemeral Ads**

## Team Members
- Warren Zhu
- Matthew Kotzbauer

## Demo
- **Live URL:** [TBD]
- **Demo Video:** [TBD]

## What We Built

**Ephemeral Ads** is an invisible advertising platform that embeds products directly INTO aesthetic content using AI image editing, rather than overlaying intrusive ads.

### The Problem

**1. Pinterest is 50-60% ads.** Users consistently complain that their feed is overwhelmed by sponsored content that drowns out what they actually came to see. Ads are overt, disruptive, and feel like an interruption rather than a discovery.

**2. Chat-based AI interfaces don't fit e-commerce.** Conversational UIs like ChatGPT's ad placements feel jarring and unnatural in contexts where users want to *browse and discover* fluidly—not engage in back-and-forth dialogue. Shopping is about serendipity and visual inspiration, not Q&A.

### Our Solution

Products appear *inside* images, not on top of them. Using Nano Banana Pro's image editing capabilities, we seamlessly integrate advertiser products into user-generated aesthetic content. Discovery happens through subtle hover interactions—a gentle outline that breathes and fades, revealing purchase options only when the user expresses interest.

The result: advertising that feels like content, not interruption.

## How It Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ADVERTISER CONSOLE                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ Products │  │ Demo-    │  │ Aesthetic│  │ Budget   │            │
│  │ Catalog  │  │ graphics │  │ Matching │  │ & Deploy │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼─────────────┼─────────────┼─────────────┼───────────────────┘
        │             │             │             │
        └─────────────┴──────┬──────┴─────────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │   SEMANTIC MATCHING    │
                │  User posts matched to │
                │  advertiser criteria   │
                └───────────┬────────────┘
                            │
                            ▼
                ┌────────────────────────┐
                │   NANO BANANA PRO      │
                │  Product edited INTO   │
                │  matched images        │
                └───────────┬────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Ephemeral Canvas                                           │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                     │   │
│  │  │ ░░░░░░░ │  │ ░░░░░░░ │  │ ░░░░░░░ │  Cards fade away   │   │
│  │  │ ░░░░░░░ │  │ ░░▓▓░░░ │  │ ░░░░░░░ │  unless saved      │   │
│  │  │ ░░░░░░░ │  │ ░░░░░░░ │  │ ░░░░░░░ │                     │   │
│  │  └─────────┘  └────┬────┘  └─────────┘                     │   │
│  │                    │                                        │   │
│  │                    ▼ hover reveals product                  │   │
│  │              ┌──────────────┐                               │   │
│  │              │ HAY Sofa     │  Glassmorphic popup           │   │
│  │              │ $3,895       │  1-click checkout             │   │
│  │              │ [Add to Bag] │                               │   │
│  │              └──────────────┘                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

**Flow:**
1. Advertisers upload product catalogs, set demographics, and define aesthetic matching criteria
2. User-generated content is semantically matched to advertiser preferences
3. Nano Banana Pro edits products INTO matched images seamlessly
4. Users browse an ephemeral canvas—cards fade unless saved
5. Subtle hover reveals embedded products with smooth 1-click purchase

## Key Features

### Consumer Experience
- **Ephemeral Canvas** — Cards drift away unless you save them, creating urgency and focus
- **Invisible Product Placement** — Products are AI-edited INTO images, not overlaid
- **Hover-to-Reveal Discovery** — Subtle breathing outlines that fade with the card; hover to pause and explore
- **Seamless 1-Click Checkout** — Glassmorphic popups with instant "Add to Bag"

### Advertiser Console
- **Product Catalog Management** — Upload and select products to advertise
- **Demographic Targeting** — Age ranges (18-24, 25-34, etc.) and interests (Fashion, Home, Tech)
- **Aesthetic Matching** — Scene types, vibe filters, custom semantic queries
- **Placement Prompts** — Control how products appear (subtle, prominent, editorial, in-use)
- **Budget Control** — Daily budget slider with impression estimates
- **Live Testing** — Click any sample post to preview AI-generated product placement

## Tech Stack
- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Backend:** FastAPI + Python + uv
- **Models:** Nano Banana Pro (image editing), Gemini 3 Pro (semantic matching)
- **Styling:** Custom CSS with glassmorphism, micro-animations, 4pm Paris aesthetic

## Setup Instructions

```bash
# Install dependencies
npm install
cd backend && uv sync && cd ..

# Start both servers (backend :8000, frontend :4173)
make serve

# Or for development with hot reload
make dev

# Stop all servers
make kill
```

**Environment Setup:**
```bash
# backend/.env
GEMINI_API_KEY=your_api_key_here
```

## Screenshots

[Screenshots to be added]
