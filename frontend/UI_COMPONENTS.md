# 🧩 Component Guidelines

## 1. The "Interactive Question" Card
- **Background:** Slate-800 (`#1E293B`).
- **Border:** 1px Slate-700.
- **States:** 
  - *Default:* Gray border.
  - *Selected:* Emerald-500 border (2px).
  - *Correct:* Emerald-500 background (opacity 10%) + check icon.
  - *Incorrect:* Ruby-500 background (opacity 10%) + x icon.

## 2. 3D Flashcard Component
- **Front:** Question text + Subject Tag.
- **Back:** Explanation + "Got it" / "Needs Review" buttons.
- **Animation:** `rotate-y-180` with a `0.6s` transition.
- **UX:** Swipe Right = Mastered, Swipe Left = Re-study.

## 3. The "Sync Status" Indicator
- **Connected:** Pulsing Emerald Dot + "Synced".
- **Offline:** Solid Amber Dot + "Offline Mode".
- **Syncing:** Rotating Spinner icon.

## 4. Floating Scientific Calculator
- **Layout:** 4x5 Grid.
- **Interaction:** Draggable handle at the top.
- **Visuals:** Glassmorphism (`backdrop-blur-md`).
