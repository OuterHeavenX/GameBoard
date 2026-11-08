# Gameboard design rules

Read this before changing anything visual. If a change breaks a rule here, change the rule on purpose or change the design. Do not drift.

## What this is

A calm, dense, professional control panel for one developer's 60+ projects. It should feel like Linear, Stripe's dashboard or GitHub's project views: quiet, precise, fast to scan. It is not a game UI and not a marketing page.

## Principles

1. **Content first.** The projects and screenshots are the visuals. The chrome stays out of the way.
2. **One primary action per screen.** Only one filled green button visible at a time (Add project / Save project). Everything else is secondary or a text/icon button.
3. **Hierarchy through size, weight and spacing, not decoration.** No gradients, glows, or decorative shadows.
4. **Restraint.** If an element does not help someone find, judge or open a project, remove it.
5. **Consistency over novelty.** Reuse an existing component before inventing one.

## Tokens (do not add new ones without a reason)

**Type**
- Headings: Manrope, 600–800. Body and UI: DM Sans.
- Sizes: 10 / 11 / 12 / 14 / 19 / 34 px. Nothing between. Body text never below 11px.
- Uppercase micro-labels: 9–10px, letter-spacing .1–.15em, muted colour. Use sparingly.

**Spacing:** multiples of 4px (4, 8, 12, 16, 24, 32, 40). Cards pad 21–22px. Page sections separate by 32–40px.

**Radius:** 6px for buttons and inputs, 8–9px for cards and panels, 999px only for pills. Nothing else.

**Colour (light / dark)**
| Role | Light | Dark |
|---|---|---|
| Page | `#f7f8f5` | `#121714` |
| Surface (cards, inputs) | `#ffffff` | `#19211c` |
| Border | `#e0e6da` | `#2a362e` |
| Text | `#24352e` | `#dfe8e0` |
| Muted text | `#869080` | `#8fa092` |
| Primary | `#264c3b` | `#3d7358` |
| Highlight (selected, tags) | `#e6ecdd` | `#243a2e` |
| Warning / blocked | amber `#e0b25e` family | same hues, darker fills |
| Success / ready | green family | same |

One accent colour (green). Amber is for "needs attention" only. Never introduce purple, blue-to-purple gradients, neon or rainbow accents.

**Elevation:** borders, not shadows. A soft shadow is allowed only on hover for cards and on the editor panel.

## Components

- **Card:** 16:9 screenshot on top, then name, one meta line, two-line description, link chips, "Next up". Same structure for every project. No per-project colours or decoration; the placeholder for missing screenshots is the neutral striped block.
- **Badges:** tiny, tinted, uppercase text. Max two per card. Meaning is fixed: blue = in development, amber = blocked or needs review, green = ready, grey = paused.
- **Buttons:** primary (filled green), secondary (tinted), icon button (no border). Every icon-only button has an `aria-label`. Minimum hit area 34px, 44px on touch where possible.
- **Forms:** label above field, 12px labels, full-width inputs, validation text under the field in plain words.
- **Panels:** the editor slides in from the right; never a centered modal for editing.
- **Icons:** one stroke style (2px, rounded). No emoji as icons, anywhere.

## Layout

- Fixed left sidebar on desktop, a scrolling top nav on mobile. Content column max about 1200px.
- Card grid: auto-fill, min 280px. Do not use more than two grid patterns on a page.
- Design mobile (390px) and desktop (1280px) every time. Nothing may scroll sideways.

## Copy

- Plain, short, sentence case. Say what happens: "Save project", not "Let's go!".
- No hype ("Unleash", "supercharge", "seamless"), no exclamation marks, no emoji.
- Empty states say what is missing and how to fix it in one sentence.

## States (required for anything new)

Default, hover, focus-visible, active, disabled, loading, empty, error. Focus rings are always visible and never removed. Dark mode must be checked for every change. Contrast: text at least 4.5:1.

## Motion

150–250ms, ease-out, for hover and panel slide only. No bouncing, parallax or looping animation. Respect `prefers-reduced-motion`.

## Slop checklist (reject the change if any are true)

- Gradient backgrounds or gradient text
- Glow, neon outline, or heavy drop shadows
- Emoji used as icons or bullets
- Centered hero text with a big gradient button
- Rounded cards with a coloured left border
- A row of three identical icon-and-blurb tiles
- More than one accent colour
- Lorem ipsum, fake testimonials or fake stats
- New fonts, sizes or radii that are not in the tokens above

## Before finishing any UI change

1. Screenshot at 390px and 1280px, light and dark.
2. Compare against this file and fix every mismatch.
3. Check keyboard: Tab order, Escape closes panels, focus is visible.
4. Verify nothing overflows horizontally and long names truncate cleanly.
