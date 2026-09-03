# 📱 Mobile-First Guidelines (The "Rural Constraint")

## Tap Targets
- All buttons must be at least **44x44px**.
- Spacing between multiple-choice options must be **12px** to prevent "fat-finger" errors.

## Visual Hierarchy
- **Primary Action:** (e.g., "Next Question") must be a full-width sticky button at the bottom.
- **Secondary Action:** (e.g., "Hint") should be an outline button or text link.

## Loaders
- Use **Skeleton Screens** (shimmering boxes) instead of spinning wheels. 
- Skeleton screens make the app feel faster on slow 2G/3G connections.

## Offline Feedback
- When the app is offline, add a subtle **Grayscale filter (5%)** to the header to subconsciously let the user know they are in local mode.

## 🚦 Implementation Order

**Phase 0:** Setup Tailwind Config with the Emerald/Slate color palette.

**Phase 1:** Build the Question Card (The most used component).

**Phase 2:** Build the Landing-to-Chat transition.

**Phase 3:** Build the Flashcard Flip logic.

**Phase 4:** Integrate KaTeX styling (ensure math text doesn't overflow bubbles).
