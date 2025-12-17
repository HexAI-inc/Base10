# 🚀 Quick Start Guide

## Installation & Setup

### 1. Activate Virtual Environment
```bash
source ./venv/bin/activate
```

### 2. Install Dependencies (if needed)
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_api_key_here
```

### 4. Run the Application
```bash
python app.py
```

The app will be available at: **http://localhost:5000**

---

## 🎯 First-Time Usage

### On Desktop:
1. Open http://localhost:5000 in your browser
2. You'll see a **keyboard shortcuts** modal (dismiss after reading)
3. Choose a subject or ask a question
4. Try the keyboard shortcuts:
   - `Ctrl+K` for a quiz
   - `Ctrl+E` to export chat
   - `Ctrl+Enter` to send messages

### On Mobile:
1. Open the app in mobile browser
2. Tap the **☰ menu** for mobile options
3. Use swipe gestures:
   - Swipe down to refresh
   - Swipe left to delete messages
4. Install as PWA: Browser Menu → "Add to Home Screen"

---

## 🎮 Try These Features First

### 1. Take a Quiz
- Click "Take a Quiz" button (or `Ctrl+K`)
- Select difficulty level
- Answer questions
- Submit for instant feedback
- See confetti for high scores! 🎉

### 2. View Statistics
- Click the 📊 icon
- See your progress
- Check unlocked achievements
- View study streak

### 3. Use Flashcards
- Complete a quiz
- Click "🎴 Flashcards" button
- Click cards to flip
- Study efficiently!

### 4. Study Planner
- Click 📅 icon (or mobile menu)
- Add topics with dates
- Track your schedule

---

## 📱 Mobile Features

### Install as App
1. Browser menu → "Add to Home Screen"
2. Enjoy offline access
3. Get app-like experience

### Gestures
- **Pull down**: Refresh chat
- **Swipe left**: Delete message
- **Swipe down on sheet**: Close bottom sheet

### Haptic Feedback
Vibration feedback on:
- Correct answers
- Achievement unlocks
- Important actions

---

## ⚡ Power User Tips

1. **Master Keyboard Shortcuts**: Save time with `Ctrl+K`, `Ctrl+E`, `Ctrl+Enter`
2. **Build Streaks**: Study daily for achievement rewards
3. **Export Everything**: Save chats and quizzes for offline review
4. **Use Flashcards**: Better retention than just quizzes
5. **Plan Ahead**: Use study planner for structured learning
6. **Check Stats**: Review weekly to track improvement

---

## 🎨 Customization

### Access Settings:
- Desktop: Click ⚙️ in mobile menu section
- Mobile: Tap ☰ → Settings

### Available Options:
- Notifications: On/Off
- Sound Effects: On/Off
- Default Difficulty: Easy/Medium/Hard
- Clear All Data: Reset everything

---

## 🏆 Achievement Hunting

Start unlocking:
1. **First Steps** (1 quiz) - Easy!
2. **Perfectionist** (100% score) - Challenge!
3. **Dedicated** (10 quizzes) - Commitment!
4. **Scholar** (50 quizzes) - Expert!
5. **Weekly Warrior** (7-day streak) - Consistency!
6. **Consistent Champion** (30-day streak) - Master!

---

## 🐛 Troubleshooting

### App won't load?
- Check if Flask server is running
- Verify http://localhost:5000 is accessible
- Check browser console for errors

### PWA not installing?
- Try Chrome/Edge browsers first
- Check manifest.json is accessible
- Service worker must register successfully

### Features not working?
- Clear browser cache
- Check localStorage is enabled
- Ensure JavaScript is enabled

### No voice output?
- Check browser permissions
- Ensure audio is not muted
- Try different browser

---

## 📊 Data & Privacy

### What's Stored Locally:
- Chat history (last 30 days)
- Quiz scores and statistics
- Study streak data
- Achievement progress
- User preferences
- Study planner tasks

### What's Sent to Server:
- Chat messages (for AI responses)
- Quiz requests (for question generation)
- Subject/topic preferences

### Clear Your Data:
Settings → Data Management → Clear All Data

---

## 🔄 Updates & Maintenance

### Check for Updates:
- Reload page (Ctrl+R / Cmd+R)
- Service worker will fetch updates
- Close all tabs to apply updates

### Backup Your Data:
- Export important chats regularly
- Take screenshots of achievements
- Note your study streak count

---

## 📞 Need Help?

### Resources:
- **Features Guide**: See FEATURES.md for full documentation
- **Code**: Check source files for implementation details
- **Issues**: Report bugs through appropriate channels

### Quick Links:
- Main app: http://localhost:5000
- Manifest: http://localhost:5000/manifest.json
- Service Worker: http://localhost:5000/service-worker.js

---

## 🎓 Study Workflow Suggestions

### Daily Routine:
1. Open app (streak +1! 🔥)
2. Review yesterday's topics (flashcards)
3. Take practice quiz
4. Ask AI to explain mistakes
5. Export difficult topics
6. Plan tomorrow's topics

### Before Exam:
1. Check statistics (identify weak areas)
2. Focus quizzes on weak subjects
3. Use flashcards for quick review
4. Export all important notes
5. Time yourself with timer mode

### Group Study:
1. Share quiz results (export)
2. Challenge friends to beat scores
3. Compare statistics
4. Study together with planner

---

**You're all set! Start learning smarter with WaeGPT! 🚀**
