# Design System Document: The Curated Gallery

## 1. Overview & Creative North Star
**Creative North Star: The Digital Curator**

This design system moves away from the cluttered, "urgent" aesthetic of traditional auction sites. Instead, it adopts the persona of a high-end editorial gallery. Every auction item is treated as a masterpiece, framed by generous whitespace, sophisticated tonal layering, and authoritative typography. 

To achieve this, we break the "template" look by utilizing intentional asymmetry—such as overlapping image elements and high-contrast typography scales—that guides the user’s eye through a narrative rather than a grid. We are not just building a platform; we are creating a premium stage for high-stakes decision-making.

---

## 2. Colors & Atmospheric Depth
Our palette is anchored by the prestige of Deep Bordeaux and the clarity of an expansive white canvas.

### The Color Logic
- **Primary Focus:** `primary_container` (#800020) is our "Prestige Anchor." Use it for the most critical actions and brand moments.
- **Surface Hierarchy:** We utilize a "Nested Depth" approach. Instead of using lines to separate content, we use the `surface` tokens:
    - **Base Layer:** `surface` (#f9f9f9) for the main page background.
    - **Sectioning:** Use `surface_container_low` (#f3f3f3) for large layout blocks.
    - **Inner Content:** Use `surface_container_lowest` (#ffffff) for cards and high-priority content areas to create a "lifted" appearance.

### Design Rules
- **The "No-Line" Rule:** Explicitly prohibit 1px solid borders for sectioning. Boundaries must be defined solely through background color shifts or subtle tonal transitions.
- **The Glass & Gradient Rule:** For floating elements (like status badges or "Quick Bid" overlays), use `surface_container_lowest` at 80% opacity with a `backdrop-filter: blur(12px)`.
- **Signature Textures:** Main CTAs should not be flat. Apply a subtle linear gradient from `primary` (#570013) to `primary_container` (#800020) at a 135-degree angle to add "soul" and dimension.

---

## 3. Typography
We use a dual-font strategy to balance editorial elegance with functional precision.

- **Display & Headlines (Manrope):** A modern, geometric sans-serif that commands authority. Use `display-lg` for hero auction titles and `headline-md` for section headers. 
- **Body & Labels (Inter):** A highly legible, neutral sans-serif designed for data-heavy environments. Use `body-md` for item descriptions and `label-md` for technical auction metadata.

**High-Contrast Scale:** Ensure a dramatic size difference between headlines and body text. A `headline-lg` (2rem) should often sit near `body-sm` (0.75rem) metadata to create a sophisticated, "magazine-style" hierarchy.

---

## 4. Elevation & Tonal Layering
Depth in this design system is organic, not artificial.

- **The Layering Principle:** Achieve hierarchy by "stacking" surfaces. For example, place a `surface_container_lowest` auction card onto a `surface_container_low` section background. This creates a soft, natural lift.
- **Ambient Shadows:** Shadows are rare and reserved for "floating" interactive elements (e.g., active modals). Use a `24px` blur with 6% opacity, using a tinted version of `on_surface` (#1a1c1c) to mimic natural light.
- **The "Ghost Border" Fallback:** If a container requires more definition against a complex background, use the `outline_variant` token at **15% opacity**. Never use 100% opaque borders.
- **Glassmorphism:** Use semi-transparent layers for elements that hover over auction imagery (like "Time Remaining" badges) to allow the product colors to bleed through, softening the interface.

---

## 5. Components

### Elegant Auction Cards
- **Structure:** No borders or divider lines. Use `surface_container_lowest` as the card base.
- **Imagery:** Images should have a slight `xl` (0.75rem) corner radius. For featured items, allow the image to slightly break the card container’s padding for an asymmetrical, editorial feel.
- **Spacing:** Use a 32px internal padding to give the item room to breathe.

### Status Badges (Active, Expired)
- **Active:** Use `surface_container_highest` with a `primary` text color. Apply a subtle pulse animation to a 4px dot next to the text.
- **Expired:** Use `surface_dim` with `on_surface_variant` text. Low contrast to indicate inactivity.
- **Shape:** Use the `full` roundedness scale (pill shape) for a modern look.

### Prominent Bidding Sections
- **The Focus Area:** Use `surface_container_high` (#e8e8e8) to wrap the bidding input, creating a "well" that draws the eye.
- **Buttons (Primary):** Use the signature Bordeaux gradient. Roundedness should be `md` (0.375rem) to maintain a professional, sharp aesthetic.
- **Inputs:** `surface_container_lowest` backgrounds with a "Ghost Border" on focus. Use `title-md` for the numeric bid value to ensure high visibility.

### Lists & Tables
- **Rule:** Forbid the use of horizontal divider lines. Use alternating row colors (`surface` and `surface_container_low`) or 24px vertical whitespace gaps to separate entries.

---

## 6. Do’s and Don’ts

### Do
- **Do** use whitespace as a functional tool to group related bidding information.
- **Do** utilize the `manrope` font for all price-point displays to give them a "premium" weight.
- **Do** use `surface_bright` to highlight the "Current High Bidder" status.

### Don’t
- **Don’t** use pure black (#000000) for text; use `on_surface` (#1a1c1c) to maintain a sophisticated tonal range.
- **Don’t** use standard "drop shadows" on cards; rely on background color shifts (`surface` vs `surface_container`).
- **Don’t** use aggressive, bright "Sale" reds. Stick to the `primary_container` (#800020) for all high-alert actions to maintain brand continuity.
- **Don’t** cram elements. If a section feels tight, increase the spacing by one tier in the scale rather than adding a border.