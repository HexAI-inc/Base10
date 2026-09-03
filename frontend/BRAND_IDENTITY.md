# 🎨 Base10 Brand Identity System

## Core Philosophy
**Base10** is the "Digital Older Sibling." It is knowledgeable, patient, and encouraging. The design should feel **Academic but Modern**—like a textbook that came to life.

---

## Color Palette (High Contrast & OLED Optimized)

We use a **Deep Emerald** strategy. Green signifies "Go/Success" and works beautifully on dark backgrounds (which save battery on AMOLED screens common in Tecno/Infinix phones).

| Token | Hex | Tailwind Class | Usage |
| :--- | :--- | :--- | :--- |
| **Brand Primary** | `#10B981` | `bg-emerald-500` | Primary buttons, Active states, Correct answers |
| **Brand Dark** | `#064E3B` | `bg-emerald-900` | Backgrounds for highlighted cards |
| **Canvas Dark** | `#0F172A` | `bg-slate-900` | Main App Background (Dark Mode Default) |
| **Surface Dark** | `#1E293B` | `bg-slate-800` | Cards, Modals, Inputs |
| **Success** | `#22C55E` | `text-green-500` | "Correct Answer", streaks |
| **Error** | `#EF4444` | `text-red-500` | "Incorrect", offline warnings |
| **Text High** | `#F8FAFC` | `text-slate-50` | Headings |
| **Text Muted** | `#94A3B8` | `text-slate-400` | Explanations, meta-data |

### Why These Colors?

**🌍 West African Context:**
- **True Black (#0F172A)**: Maximizes OLED battery savings on Tecno, Infinix, and Samsung devices
- **Emerald Green**: Culturally neutral, universally positive, excellent outdoor visibility
- **High Contrast**: Readable in direct sunlight (common use case: studying outdoors)
- **Minimal Bright Colors**: Reduces eye strain during long study sessions

**⚡ Technical Benefits:**
- OLED pixels turn off completely on pure blacks (30-40% battery savings)
- Emerald (#10B981) has 4.5:1 contrast ratio against slate-900 (WCAG AA compliant)
- Reduced blue light exposure in evening study sessions

---

## Typography

We use **system-ui** fonts for performance (no download required) but style them specifically.

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
             'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 
             'Fira Sans', 'Droid Sans', 'Helvetica Neue', 
             sans-serif;
```

### Font Roles
- **Headings:** `Outfit` or `Plus Jakarta Sans` (Bold, Tight tracking `-0.02em`)
- **Body:** System fonts (Tall x-height for readability, `line-height: 1.6`)
- **Math:** `KaTeX_Main` (Serif style for equations)
- **Code:** `JetBrains Mono` or `Fira Code` (Optional, for programming courses)

### Why System Fonts?
- **Zero Network Cost**: No font downloads required
- **Instant Rendering**: Native fonts render immediately
- **Familiar to Users**: Matches device OS experience
- **Bandwidth Savings**: Saves ~50-150KB per page load

### Font Size Scale
| Size | rem | px | Usage |
|------|-----|-----|-------|
| xs   | 0.75rem | 12px | Captions, metadata |
| sm   | 0.875rem | 14px | Secondary text |
| base | 1rem | 16px | Body text (minimum) |
| lg   | 1.125rem | 18px | Subheadings |
| xl   | 1.25rem | 20px | Card titles |
| 2xl  | 1.5rem | 24px | Section headers |
| 3xl  | 1.875rem | 30px | Page titles |
| 4xl  | 2.25rem | 36px | Hero text |

---

## Iconography

**Lucide React** (Stroke width: 2px)

### Why Lucide?
- **Clean Vectors**: Scalable, look sharp on low-res screens
- **Lightweight**: ~50KB bundle size (vs 200KB+ for FontAwesome)
- **Consistent Grid**: 24x24 pixel grid system
- **Performance**: Tree-shakeable (only import icons you use)
- **Low-End Friendly**: Renders perfectly at small sizes (16px, 20px)

### Icon Sizing Guidelines
```tsx
import { Book, Award, Sparkles } from 'lucide-react'

// Navigation icons
<Book size={24} strokeWidth={2} />

// Button icons
<Award size={20} strokeWidth={2} />

// Inline text icons
<Sparkles size={16} strokeWidth={2} />

// Feature cards
<Trophy size={48} strokeWidth={1.5} />
```

### Icon Color Usage
- **Primary Actions**: `text-emerald-500`
- **Success States**: `text-green-500`
- **Errors/Warnings**: `text-red-500` or `text-orange-500`
- **Neutral/Muted**: `text-slate-400`
- **High Emphasis**: `text-slate-50`
