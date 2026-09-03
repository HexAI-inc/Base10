# 🧠 UX Patterns & Interactions

## Core Principle: Design for 2G/3G Networks

Base10 is built for **intermittent connectivity**. Every interaction should feel instant, even when the network is slow or offline.

---

## 1. The "Optimistic" Interaction Model

### Problem
Network is slow (2G/3G). Users on slow connections experience 200-1000ms latency.

### Solution
**Never wait for the server to show feedback.**

### Implementation

#### Quiz Submission
When a user selects "Option A":
1. **Immediate**: Paint the button Green (correct) or Red (incorrect) based on client-side validation
2. **Background**: Queue the API call to submit the answer
3. **Reconciliation**: If server response differs, update UI (rare edge case)

**Code Example:**
```tsx
const handleSelectOption = async (selectedOption: string) => {
  // Step 1: Immediate UI update
  setUserAnswer(selectedOption)
  const isCorrect = selectedOption === correctAnswer
  setAnswerState(isCorrect ? 'correct' : 'incorrect')
  
  // Step 2: Background sync
  try {
    const result = await questionApi.submitAnswer({
      question_id,
      user_answer: selectedOption
    })
    // Step 3: Reconcile if needed
    if (result.is_correct !== isCorrect) {
      setAnswerState(result.is_correct ? 'correct' : 'incorrect')
    }
  } catch (error) {
    // Step 4: Queue for retry
    addToPendingSync({
      type: 'answer_submission',
      data: { question_id, user_answer: selectedOption },
      timestamp: Date.now()
    })
  }
}
```

#### Navigation
Use **Client-Side Routing** for instant page transitions.

```tsx
// Next.js App Router handles this automatically
import Link from 'next/link'

<Link href="/practice" className="transition-opacity duration-150">
  Start Practice
</Link>
```

**Benefits:**
- Page transitions feel instant (<50ms)
- Loader shows only if data fetch takes >300ms
- Previous page stays visible during navigation

---

## 2. Progressive Disclosure (The Data Saver)

### Problem
Images and AI explanations consume significant data (50KB-500KB per item).

### Solution
Show content only when explicitly requested.

### Implementation

#### Images: Click-to-Load
```tsx
const QuestionImage = ({ imageUrl, estimatedSize }) => {
  const [loaded, setLoaded] = useState(false)
  const [connection, setConnection] = useState(getConnectionType())
  
  // Auto-load on WiFi
  useEffect(() => {
    if (connection === 'wifi' || connection === '4g') {
      setLoaded(true)
    }
  }, [connection])
  
  if (!loaded) {
    return (
      <button 
        onClick={() => setLoaded(true)}
        className="w-full py-6 border-2 border-dashed border-slate-700 
                   rounded-lg text-emerald-500 hover:bg-slate-800"
      >
        📊 Load Diagram ({formatBytes(estimatedSize)})
      </button>
    )
  }
  
  return <img src={imageUrl} alt="" className="rounded-lg" />
}
```

#### AI Explanations: Tap-to-Expand
```tsx
const AIExplanation = ({ questionId, userAnswer }) => {
  const [explanation, setExplanation] = useState(null)
  const [loading, setLoading] = useState(false)
  
  const loadExplanation = async () => {
    setLoading(true)
    try {
      const result = await aiApi.explainAnswer({
        question_id: questionId,
        student_answer: userAnswer
      })
      setExplanation(result.explanation)
    } catch (error) {
      showError('Could not load explanation. Try again.')
    } finally {
      setLoading(false)
    }
  }
  
  if (!explanation) {
    return (
      <button 
        onClick={loadExplanation}
        disabled={loading}
        className="mt-4 text-emerald-500 text-sm flex items-center gap-2"
      >
        {loading ? (
          <><Loader2 className="w-4 h-4 animate-spin" /> Loading...</>
        ) : (
          <>🤔 Why did I fail? (Tap to see AI explanation)</>
        )}
      </button>
    )
  }
  
  return (
    <div className="mt-4 p-4 bg-slate-800 rounded-lg prose prose-invert">
      {explanation}
    </div>
  )
}
```

---

## 3. The "Sync" Traffic Light

### Problem
Users need to know their connection status at a glance.

### Solution
A persistent small dot in the top-right header.

### States
- 🟢 **Green**: Online & All changes synced
- 🟡 **Yellow**: Offline (Changes saved locally)
- 🔵 **Pulsing Blue**: Currently syncing...
- 🔴 **Red**: Sync failed (Tap to retry)

### Implementation
```tsx
const SyncIndicator = () => {
  const { status, pendingCount, retry } = useSyncStatus()
  
  const statusConfig = {
    synced: { color: 'bg-green-500', label: 'Synced' },
    offline: { color: 'bg-yellow-500', label: 'Offline' },
    syncing: { color: 'bg-blue-500 animate-pulse', label: 'Syncing...' },
    error: { color: 'bg-red-500', label: 'Sync Failed' }
  }
  
  const config = statusConfig[status]
  
  return (
    <button
      onClick={() => status === 'error' && retry()}
      className="relative group"
      title={config.label}
    >
      <div className={`w-2 h-2 rounded-full ${config.color}`} />
      
      {/* Tooltip */}
      <div className="absolute right-0 top-8 bg-slate-800 text-xs 
                      px-3 py-2 rounded-lg opacity-0 group-hover:opacity-100
                      transition-opacity whitespace-nowrap">
        {config.label}
        {pendingCount > 0 && ` (${pendingCount} pending)`}
      </div>
    </button>
  )
}
```

**Position**: Top-right corner, always visible, 8px diameter

---

## 4. The "Morphing" Input

### Problem
Screen space is precious on mobile devices.

### Solution
Context-aware input transformation.

### Behavior on Dashboard

#### State 1: Centered Search Bar
```tsx
// Initial state
<div className="flex-1 flex items-center justify-center">
  <input
    type="text"
    placeholder="What do you want to learn?"
    className="w-full max-w-2xl h-16 px-6 rounded-full
               bg-slate-800 border-2 border-slate-700
               focus:border-emerald-500 transition-all"
    onFocus={() => setInputMode('chat')}
  />
</div>
```

#### State 2: Bottom Chat Input
```tsx
// After focus
<div className="fixed bottom-0 left-0 right-0 p-4 
                bg-slate-900 border-t border-slate-800
                transition-transform duration-300">
  {/* Quick Chips */}
  <div className="flex gap-2 mb-3 overflow-x-auto no-scrollbar">
    {recentSubjects.map(subject => (
      <button 
        key={subject}
        className="px-4 py-2 bg-slate-800 rounded-full text-sm
                   whitespace-nowrap"
      >
        {subject}
      </button>
    ))}
  </div>
  
  {/* Chat Input */}
  <div className="flex gap-2">
    <input
      type="text"
      ref={inputRef}
      placeholder="Ask me anything..."
      className="flex-1 px-4 py-3 bg-slate-800 rounded-full"
    />
    <button className="w-12 h-12 bg-emerald-500 rounded-full">
      <Send className="w-5 h-5 mx-auto" />
    </button>
  </div>
</div>
```

### Animation
```css
@keyframes morphToBottom {
  from {
    position: static;
    max-width: 48rem;
    border-radius: 9999px;
  }
  to {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    max-width: 100%;
    border-radius: 0;
  }
}

.morphing-input.focused {
  animation: morphToBottom 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}
```
