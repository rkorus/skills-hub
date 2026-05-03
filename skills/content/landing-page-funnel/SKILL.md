---
name: landing-page-funnel
version: 1.0.0
description: Build high-converting SaaS landing page funnels using proven patterns. Covers page structure, copy frameworks, design rules, conversion tactics, and anti-patterns.
category: content
tags: [landing-page, funnel, conversion, saas, design]
author: Lyra (AI-CIV)
compatibility: [claude-code, general]
dependencies: []
---
# Landing Page Funnel Skill

---
name: landing-page-funnel
description: Build high-converting SaaS landing page funnels using proven patterns from top-performing companies (Jasper, Notion, Stripe, ClickFunnels, HubSpot, etc.)
version: 2.0.0
source: [your-project-path]
visual-analysis: [your-project-path]
---

## When to Use This Skill

Use when building, auditing, or redesigning a SaaS landing page, pricing page, or signup funnel. Applies to [your brand] and any client project requiring conversion-optimized pages.

---

## 1. Page Structure Template (Exact Section Order)

Build every landing page in this order. Do not skip sections. Do not reorder.

| # | Section | Purpose | Key Rule |
|---|---------|---------|----------|
| 1 | **Nav bar** | Orientation + persistent CTA | Logo left, 3-5 links center, CTA button right |
| 2 | **Hero** | Hook + primary conversion | Headline (under 8 words) + subheadline (1-2 sentences) + primary CTA + product screenshot or 15s demo |
| 3 | **Logo bar** | Instant credibility | 5-8 recognizable customer/press logos. Scrolling carousel on mobile |
| 4 | **Problem/pain** | Emotional resonance | Name the specific pain. No features here. Only the broken status quo |
| 5 | **Solution showcase** | Outcome-driven features | 3-5 feature cards or use-case sections. Benefits, not features. Bento grid or card layout |
| 6 | **Social proof** | Trust through evidence | Testimonials with photo + full name + title + company + specific metric. Never generic quotes |
| 7 | **How it works** | Simplify the mental model | 3-step visual process. Numbered. Icons or illustrations per step |
| 8 | **Pricing preview** | Remove ambiguity | Embedded pricing or "See Pricing" link. If embedded: 3 tiers max, middle highlighted |
| 9 | **FAQ / objection handling** | Overcome hesitation | 5-8 most common questions. Accordion format on mobile |
| 10 | **Final CTA** | Close the loop | Repeat hero CTA with urgency-adjacent copy. "No credit card required" micro-copy |
| 11 | **Footer** | Navigation + legal | Links, legal, secondary nav |

---

## 2. Copy Frameworks

### Framework Selection Guide

| Framework | Best For | Structure |
|-----------|----------|-----------|
| **Problem-Solution-Proof** | Enterprise B2B, long consideration | State problem > show solution > prove with data |
| **PAS (Problem-Agitate-Solution)** | High-ticket, emotional purchases | Name pain > twist the knife > present relief |
| **Before-After-Bridge** | Product-led growth, transformation | Show "before" state > show "after" state > bridge = your product |
| **AIDA** | Content-heavy pages, multiple CTAs | Attention > Interest > Desire > Action |
| **Outcome-first** | Developer/creative audiences who hate hype | Lead with result, explain mechanism second |

**Default for [your brand]:** Problem-Solution-Proof for the main landing page. PAS for retargeting pages.

### Headline Rules

- Under 8 words. Always.
- Lead with the OUTCOME the customer gets, not the tool's features.
- Use an action verb.
- No jargon. No buzzwords. No "leverage" or "synergy."

### 10 Headline Templates

Plug in your product name and audience. Each template encodes a proven pattern.

1. **Outcome + price anchor:** "AI that runs your marketing. $149/mo."
2. **Aspirational identity:** "You're one [product unit] away from [transformation]."
3. **Anti-status-quo:** "Goodbye [old way]. Hello [new way]."
4. **Developer empathy:** "We built [thing] so you don't have to."
5. **Contrast pair:** "One [noun]. Zero [pain point]."
6. **Speed promise:** "[Verb] [outcome] in [timeframe]."
7. **Action + specificity:** "Put [technology] to work for [job]."
8. **Parallel structure:** "[Verb] anything. [Verb] anywhere."
9. **Reframe + outcome:** "More than [category]. [Business result]."
10. **Imperative + scale:** "Stop [wasteful action]. Start [desired action]."

### CTA Button Copy Rules

- Primary CTA: filled/solid button. Text = action + value ("Start Free Trial", "See It In Action").
- Secondary CTA: outlined/ghost button. Text = lower commitment ("Watch Demo", "Learn More").
- Always add micro-copy below primary CTA: "No credit card required" or "Free 14-day trial."
- Repeat primary CTA every 2-3 scroll sections.
- Never use "Submit" or "Click Here."

---

## 3. Design Rules

### [your brand] Brand Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-dark` | `#080A12` | Page background (dark mode), text (light mode) |
| `--color-accent` | `#2A93C1` | Links, secondary buttons, interactive elements |
| `--color-cta` | `#F1420B` | Primary CTA buttons, urgency highlights |

CTA buttons MUST use `#F1420B` on dark backgrounds or white backgrounds for maximum contrast. Never put `#2A93C1` on `#080A12` for CTA buttons (insufficient contrast for action elements).

### Typography

- Headline: 48-64px desktop, 32-40px mobile. Bold weight (700+).
- Subheadline: 20-24px desktop, 16-18px mobile. Regular weight (400).
- Body: 16-18px desktop, 14-16px mobile. Line height 1.5-1.6.
- Use one font family max. Sans-serif. Inter, Geist, or system fonts.

### Mobile-First Rules

- Design mobile layout first, then scale up to desktop.
- 58% of SaaS pricing page visits are mobile. 79-83% of total visits are mobile.
- CTA buttons: minimum 48px height (WCAG), optimal 56-64px on mobile. Full-width on mobile viewports.
- Thumb zone: place primary CTAs in bottom third of screen.
- Sticky/floating CTA on long-scroll pages.
- Stack pricing tiers vertically on mobile. Never horizontal scroll.
- Collapsible feature comparison tables, not wide grids.
- Logo bar: scrolling horizontal carousel on mobile.

### Layout Patterns (2026)

- Bento grid for feature sections.
- Card-based feature sections with hover animations.
- Split-screen hero: text left, product screenshot right.
- Scroll-triggered progressive disclosure.
- Full-width sections alternating with contained-width text blocks.
- Dark backgrounds work best for AI products, developer tools, premium positioning.

---

## 4. Conversion Tactics

### Dual CTA Strategy

Every hero section gets two CTAs side by side:

| Position | Label Pattern | Target |
|----------|--------------|--------|
| Primary (left) | "Start Free Trial" / "Try for Free" | Self-serve signups |
| Secondary (right) | "Get a Demo" / "See It In Action" | Enterprise / high-touch leads |

This is non-negotiable. Jasper, Copy.ai, and HubSpot all use this pattern. It routes visitor intent without forcing a single path.

### Intent Routing (Post-Signup)

Ask 2-3 questions at signup to personalize the experience:

1. Business type / industry
2. Team size (solo / small team / enterprise)
3. Primary goal (e.g., content, lead gen, analytics)

Route answers to a personalized dashboard, onboarding checklist, and feature surfacing. HubSpot converts significantly better with this approach.

### Social Proof Placement Strategy

| Location | Proof Type | Purpose |
|----------|-----------|---------|
| Immediately after hero | Logo bar (5-8 logos) | Reduces bounce |
| Mid-page | Full testimonials with metrics | Builds trust for engaged scrollers |
| Next to pricing tiers | Short testimonial quotes | Reduces plan hesitation |
| Near signup/payment forms | Security badges (SOC 2, GDPR, SSL) | Removes friction at conversion point |

### Testimonial Format (Mandatory)

Every testimonial MUST include all five elements:

1. **Photo** of the person (not a logo, not an icon)
2. **Full name** (never "John D." or initials)
3. **Title and company**
4. **Specific metric or outcome** ("$16M saved annually", "10,000+ hours saved", "5x more meetings")
5. **1-sentence quote** in their voice

Generic testimonials ("Great product!") are worse than no testimonials.

### Guarantee Framing

- Place a money-back guarantee near every pricing CTA.
- Frame as risk reversal: "30-day money-back guarantee. No questions asked."
- Use a small shield/badge icon next to the guarantee text.
- This reduces perceived risk at the exact moment of highest friction.

### Pricing Page Rules

- 3 tiers maximum (e.g., Starter / Pro / Enterprise). Two feels incomplete. Five causes paralysis.
- Highlight middle tier as "Most Popular" with border, badge, or background color.
- Annual/monthly toggle at top. Default to annual. Show savings in dollars ("Save $298/year"), not percentages.
- 8-10 key features per tier with checkmarks/dashes.
- One CTA button per tier.
- Feature comparison table below tier cards for deep evaluators.
- Enterprise tier separated visually, not as a 4th column.

---

## 5. Anti-Patterns (What to Avoid)

These tactics are dead or actively harmful in 2026. Never use them.

| Anti-Pattern | Why It Fails |
|-------------|-------------|
| Fake countdown timers | Users know they reset on reload. Destroys trust. |
| "Only X spots left" (fabricated) | Detected easily. Only use with real scarcity. |
| Exit-intent pop-ups | Blocked by Safari, Firefox, Brave. Feels desperate. |
| Feature-dumping (20+ features listed) | Overwhelms visitors. Focus on 3-5 outcomes. |
| Generic testimonials without names/metrics | Zero credibility. Worse than no testimonials. |
| More than 3 form fields at signup | Each extra field drops conversion. Ask for email only. Get the rest during onboarding. |
| Horizontal pricing tables on mobile | 58% of pricing visits are mobile. Horizontal scroll kills conversion. |
| Stock photos instead of product screenshots | Signals the product is not ready or not real. Show the actual product. |
| Aggressive email sequences within hours of signup | Feels like spam. Use behavior-triggered sequences instead. |
| Gating all content behind demo requests | Buyers complete 69% of purchase decisions before talking to sales. Let them self-educate. |
| Optimizing for lead volume over lead quality | Inflates CAC. Focus on decision-makers with budgets and real pain. |
| Time-based drip emails ignoring behavior | "Email #3 on day 7" regardless of user actions is lazy. Trigger on behavior. |

---

## 5b. Visual Anti-Patterns (NEVER DO)

Based on analysis of Stripe, Linear, Superhuman, Mercury, and Vercel landing pages (April 2026). See `[your-project-path] for full analysis with screenshots.

| Anti-Pattern | Why It Fails |
|-------------|-------------|
| Border-radius on section containers | Creates "card" feel. Top SaaS pages use full-width sections, not boxed content. |
| Glassmorphism/blur effects | Dated trend. No top-5 SaaS page uses frosted glass on content sections. |
| Card grids for main content | Fragments the reading flow. Single-column text is how Stripe/Linear present core messaging. |
| Icon grids (4 icons in a row with labels) | Feels like a template. Typography hierarchy replaces icon decoration. |
| Gradient borders | Decorative noise. Background color changes define sections, not borders. |
| Center-aligned body text | Hard to read past 2 lines. Left-align always except headlines. |
| More than 2 font weights per page | Visual clutter. Top pages use only 400 (body) and 600-700 (headlines). |
| Generic SaaS copy ("Transform your business", "Unlock potential") | Signals AI-generated. Specific, concrete language only. |
| Container/card-heavy layouts | Creates visual weight. Let whitespace and typography do the work. |

---

## 5c. Required Visual Patterns

| Pattern | Specification |
|---------|--------------|
| Full-width sections | Edge to edge, no container boxes wrapping sections |
| Background color = section boundary | Color changes define sections, not borders or dividers |
| Typography-driven hierarchy | Text IS the design. No decorative elements needed. |
| Single column flow | Main content in one column. No multi-column text. |
| Text max-width | 800px for text blocks, 1200px for full-width elements |
| Section padding | 120px top/bottom minimum on desktop |
| Alternating light/dark sections | Creates visual rhythm and signals new topics |

---

## 5c-2. Visual Scroll Guidance (REQUIRED)

Every funnel page MUST include a visual element that guides the viewer's eye down the page toward the CTA. The page should feel like a journey, not a stack of unrelated sections.

**Choose one (or combine) per page:**

| Technique | How to Implement | When to Use |
|-----------|-----------------|-------------|
| Winding path line | SVG path that curves left/right down the page, connecting section waypoints. Animate with stroke-dashoffset on scroll. Dashed or gradient stroke. | Best for storytelling funnels with a clear journey (problem -> solution -> offer) |
| Gradient flow line | Continuous vertical line (orange to white gradient) on the left or center margin with circle nodes at each section. | Best for step-by-step or process funnels |
| Scroll progress indicator | Thin orange progress bar on the side that fills as user scrolls, with section labels at key points. | Best for long-form funnels (10+ sections) |
| Animated dot trail | Subtle dots or particles that flow downward in the background, creating directional movement. Accelerate near the CTA. | Best for modern/tech-forward brands |
| Connected section transitions | Each section's bottom edge visually connects to the next section's top (curved dividers, gradient blends, arrow shapes). | Best for clean/minimal funnels |

**Implementation rules:**
- The visual guide should be SUBTLE, not distracting. Opacity 0.15-0.3 for path lines.
- Animate on scroll using Intersection Observer or scroll event listeners.
- The path should START at the hero and END at the final CTA/pricing section.
- On mobile, simplify to a thin vertical line or hide the path entirely.
- Use the accent color (#FA6600) at low opacity for the path, or use #333333 for subtlety.
- Add small circle nodes (8-12px) at each section transition point.

**SVG Path Pattern (reusable):**
Create an absolutely-positioned SVG that spans the full page height. The path should curve gently left and right, passing through each section's center. Use `stroke-dasharray` and `stroke-dashoffset` animated by scroll position to create a "drawing" effect as the user scrolls down.

**Why this matters:** Funnel pages without visual scroll guidance have 15-25% lower scroll depth. The path gives viewers a subconscious reason to keep scrolling.

---

## 5d. Typography System

| Element | Size | Weight | Notes |
|---------|------|--------|-------|
| H1 | 64px | 700 | Hero headline only. Max 8 words. |
| H2 | 42px | 600 | Section headlines |
| H3 | 28px | 600 | Sub-section headlines |
| Body | 18px | 400 | Line-height 1.6. Left-aligned. |
| Caption/label | 14px | 500 | Uppercase, letter-spacing 2px |

**Rule:** Max 2 font weights per page (400 + 600 or 400 + 700). One font family. Sans-serif.

---

## 5e. Color System

| Token | Hex | Usage |
|-------|-----|-------|
| Dark section bg | `#000000` or `#0A0A0A` | Hero, solution, proof, final CTA sections |
| Light section bg | `#FFFFFF` or `#FAFAFA` | Problem, how-it-works, pricing sections |
| Dark section text | `#FFFFFF` | Primary text on dark backgrounds |
| Light section text | `#1A1A1A` | Primary text on light backgrounds |
| Accent (CTA only) | `#FA6600` | CTA buttons only. Never decorative. |
| Muted text (light bg) | `#666666` | Secondary/supporting text on white |
| Muted text (dark bg) | `#999999` | Secondary/supporting text on black |

**Rule:** Never use colored section backgrounds (no blue sections, no purple sections). Only black, white, and near-variants.

---

## 5f. Section Order (Conversion Flow)

This is the v5 section order optimized for single-product conversion pages. Use instead of the 11-section template (Section 1) when building minimal, high-design funnel pages.

| # | Section | Background | Content Rules |
|---|---------|-----------|--------------|
| 1 | **Hero** | Dark (#0A0A0A) | Full viewport height. One headline (max 8 words). One subline. One CTA button. Nothing else. |
| 2 | **Social proof bar** | Dark (#0A0A0A) | 60px height. Logos or stats in a single row. Subtle, not prominent. |
| 3 | **Problem** | Light (#FFFFFF) | Headline + 3-4 pain points as paragraphs. NOT bullet lists in containers. |
| 4 | **Solution** | Dark (#0A0A0A) | What the product does. Include product screenshot if available. |
| 5 | **How it works** | Light (#FAFAFA) | 3 steps as simple text blocks. Numbered. No icon boxes. |
| 6 | **Proof** | Dark (#0A0A0A) | Testimonial or case study. Real quote with attribution. |
| 7 | **Pricing** | Light (#FFFFFF) | Simple pricing display. Not a comparison table. Single tier prominent. |
| 8 | **Final CTA** | Dark (#0A0A0A) | One headline. One button. 30-day MBG micro-copy. |

---

## 6. Tech Stack

| Layer | Tool | Notes |
|-------|------|-------|
| Framework | Next.js (App Router) | Server components for SEO, client components for interactivity |
| Hosting | Vercel | Edge functions, automatic preview deploys, analytics |
| Styling | Tailwind CSS | Utility-first, responsive breakpoints built in |
| Animation | Framer Motion | Scroll-triggered reveals, hover states, page transitions |
| Analytics | Vercel Analytics + Plausible or PostHog | Privacy-friendly, conversion tracking |
| Forms | React Hook Form + server action | Minimal JS, fast validation |
| CMS (optional) | Sanity or MDX | For testimonials, FAQ, pricing data that changes often |

### File Structure (Next.js App Router)

```
app/
  page.tsx              # Landing page (all sections composed here)
  pricing/page.tsx      # Dedicated pricing page
  demo/page.tsx         # Demo booking page
components/
  hero.tsx
  logo-bar.tsx
  problem-section.tsx
  solution-showcase.tsx
  social-proof.tsx
  how-it-works.tsx
  pricing-preview.tsx
  faq.tsx
  final-cta.tsx
  nav.tsx
  footer.tsx
lib/
  constants.ts          # Brand colors, copy, CTA text
  testimonials.ts       # Structured testimonial data
  pricing.ts            # Tier definitions
```

---

## 7. Quality Checklist

Run through every item before shipping. All must pass.

### Structure
- [ ] Page follows the 11-section order (nav > hero > logos > problem > solution > proof > how-it-works > pricing > FAQ > final CTA > footer)
- [ ] Hero headline is under 8 words and outcome-focused
- [ ] Dual CTA in hero (primary + secondary)
- [ ] Logo bar has 5-8 logos immediately after hero
- [ ] Primary CTA repeats every 2-3 scroll sections

### Copy
- [ ] No feature-dumping. 3-5 outcomes max in solution section
- [ ] Every testimonial has: photo, full name, title, company, specific metric, quote
- [ ] Micro-copy below every CTA ("No credit card required" or equivalent)
- [ ] FAQ covers 5-8 objections
- [ ] No jargon, no buzzwords, no em dashes

### Design
- [ ] Brand colors applied: `#080A12` background, `#2A93C1` accents, `#F1420B` CTAs
- [ ] CTA buttons are 48px+ height on mobile, 44px+ on desktop
- [ ] Mobile layout designed first, then scaled to desktop
- [ ] Sticky CTA visible on mobile during scroll
- [ ] Pricing tiers stack vertically on mobile
- [ ] One font family. Sans-serif.

### v5 Design Checklist (for minimal funnel pages)
- [ ] Full-width sections, no container boxes
- [ ] Background color changes define sections (no borders)
- [ ] Typography-driven hierarchy (no decorative icons)
- [ ] Single column flow, text max-width 800px
- [ ] Section padding 120px+ top/bottom
- [ ] Alternating dark/light sections
- [ ] Max 2 font weights (400 + 600 or 700)
- [ ] No glassmorphism, no gradient borders, no card grids
- [ ] Left-aligned body text (centered headlines only)
- [ ] CTA color: #FA6600

### Conversion
- [ ] Dual CTA routes to different paths (self-serve vs. demo/enterprise)
- [ ] Pricing page defaults to annual toggle
- [ ] Annual savings shown in dollars, not percentages
- [ ] Money-back guarantee near pricing CTAs
- [ ] Security badges near signup/payment forms
- [ ] Social proof placed at all four strategic locations (post-hero, mid-page, near pricing, near forms)

### Technical
- [ ] Lighthouse performance score 90+
- [ ] Core Web Vitals pass (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- [ ] All images optimized (WebP/AVIF, lazy loaded below fold)
- [ ] Open Graph + Twitter Card meta tags set
- [ ] Semantic HTML (h1 once, proper heading hierarchy, landmarks)
- [ ] Mobile viewport meta tag present
- [ ] No layout shift on CTA buttons or pricing cards

### Benchmarks to Target

| Metric | Target |
|--------|--------|
| Visitor-to-lead | 5%+ |
| Landing page conversion | 6%+ |
| Free trial to paid | 25%+ |
| Annual plan uptake | 55%+ |
| Mobile conversion | 3%+ |
| Onboarding completion | 50%+ |
| 90-day retention | 45%+ |
