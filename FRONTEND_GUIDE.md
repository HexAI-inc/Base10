# 🎨 Frontend Development Guide - Base10 EdTech Platform

## Backend Status: ✅ DEPLOYED

**Live API URL:** https://stingray-app-x7lzo.ondigitalocean.app  
**API Docs:** https://stingray-app-x7lzo.ondigitalocean.app/docs  
**Total Endpoints:** 46  
**Status:** Production Ready  

---

## Quick Start: Frontend Setup

### 1. Create Next.js Project

```bash
# Create new Next.js app
npx create-next-app@latest base10-frontend --typescript --tailwind --app

cd base10-frontend

# Install dependencies
npm install @tanstack/react-query axios zustand
npm install -D @types/node

# For PWA support
npm install next-pwa
npm install workbox-webpack-plugin

# For payments
npm install react-paystack

# For offline storage
npm install localforage
```

### 2. Configure Environment

Create `.env.local`:
```bash
NEXT_PUBLIC_API_URL=https://stingray-app-x7lzo.ondigitalocean.app
NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY=pk_test_...
NEXT_PUBLIC_APP_NAME="Base10"
```

### 3. Project Structure

```
base10-frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/
│   │   ├── practice/
│   │   ├── flashcards/
│   │   ├── leaderboard/
│   │   ├── ai-tutor/
│   │   └── subscription/
│   ├── teacher/
│   │   ├── dashboard/
│   │   ├── analytics/
│   │   └── classrooms/
│   └── layout.tsx
├── components/
│   ├── auth/
│   ├── questions/
│   ├── ai/
│   ├── billing/
│   └── ui/
├── lib/
│   ├── api.ts
│   ├── auth.ts
│   ├── offline.ts
│   └── store.ts
└── public/
```

---

## Core Features to Implement

### Phase 1: MVP (Week 1-2)

#### 1. Authentication ✅
**Endpoints:**
- POST `/api/v1/auth/register`
- POST `/api/v1/auth/login`
- GET `/api/v1/auth/me`

**Components:**
```typescript
// components/auth/LoginForm.tsx
'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { login } from '@/lib/api';

export default function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const { access_token } = await login(email, password);
      localStorage.setItem('token', access_token);
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button type="submit">Login</button>
    </form>
  );
}
```

#### 2. Question Practice ✅
**Endpoints:**
- GET `/api/v1/questions/`
- GET `/api/v1/questions/random/{subject}`
- POST `/api/v1/sync/push` (for offline sync)

**Features:**
- Subject selection
- Random question fetching
- Answer submission
- Progress tracking
- Offline support

#### 3. Offline Sync ✅
**Endpoints:**
- POST `/api/v1/sync/pull`
- POST `/api/v1/sync/push`

**Implementation:**
```typescript
// lib/offline.ts
import localforage from 'localforage';

const questionsStore = localforage.createInstance({
  name: 'base10',
  storeName: 'questions'
});

export async function cacheQuestions(questions: any[]) {
  await questionsStore.setItem('cached_questions', questions);
}

export async function getCachedQuestions() {
  return await questionsStore.getItem('cached_questions');
}

export async function syncOfflineData() {
  const pendingAttempts = await localforage.getItem('pending_attempts');
  if (pendingAttempts && navigator.onLine) {
    // Push to server
    await fetch('/api/v1/sync/push', {
      method: 'POST',
      body: JSON.stringify({ attempts: pendingAttempts })
    });
  }
}
```

#### 4. Progress Dashboard ✅
**Endpoints:**
- GET `/api/v1/sync/stats`
- GET `/api/v1/leaderboard/my-rank`

---

### Phase 2: Enhanced Features (Week 3-4)

#### 5. AI Tutor Interface 🤖
**Endpoints:**
- POST `/api/v1/ai/chat`
- POST `/api/v1/ai/explain`
- GET `/api/v1/ai/status`

**Component:**
```typescript
// components/ai/AIChatInterface.tsx
'use client';
import { useState } from 'react';
import { chatWithAI } from '@/lib/api';

export default function AIChatInterface() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatWithAI(input, messages);
      setMessages([...messages, userMessage, {
        role: 'assistant',
        content: response.response
      }]);
    } catch (error) {
      console.error('AI chat failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={msg.role === 'user' ? 'text-right' : 'text-left'}>
            <div className="inline-block p-3 rounded-lg mb-2 bg-blue-100">
              {msg.content}
            </div>
          </div>
        ))}
      </div>
      <div className="p-4 border-t">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask me anything..."
          className="w-full p-2 border rounded"
        />
      </div>
    </div>
  );
}
```

#### 6. Subscription & Billing 💰
**Endpoints:**
- GET `/api/v1/billing/plans`
- POST `/api/v1/billing/initialize`
- GET `/api/v1/billing/subscription`

**Component:**
```typescript
// components/billing/SubscriptionPlans.tsx
'use client';
import { useEffect, useState } from 'react';
import { usePaystackPayment } from 'react-paystack';
import { getPlans, initializePayment } from '@/lib/api';

export default function SubscriptionPlans() {
  const [plans, setPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);

  useEffect(() => {
    async function fetchPlans() {
      const data = await getPlans();
      setPlans(data);
    }
    fetchPlans();
  }, []);

  const handleSubscribe = async (plan: any) => {
    const { authorization_url } = await initializePayment(plan.id, userEmail);
    window.location.href = authorization_url;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {plans.map((plan) => (
        <div key={plan.id} className="border rounded-lg p-6">
          <h3 className="text-2xl font-bold">{plan.name}</h3>
          <p className="text-gray-600">{plan.description}</p>
          <div className="text-4xl font-bold my-4">
            ₦{plan.price.toLocaleString()}
            {plan.price > 0 && <span className="text-sm">/month</span>}
          </div>
          <ul className="space-y-2 mb-6">
            {plan.features.map((feature, idx) => (
              <li key={idx} className="flex items-center">
                <span className="mr-2">✓</span> {feature}
              </li>
            ))}
          </ul>
          {plan.price > 0 && (
            <button
              onClick={() => handleSubscribe(plan)}
              className="w-full bg-blue-500 text-white py-2 rounded"
            >
              Subscribe
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
```

#### 7. Smart Image Loading 🖼️
**Endpoints:**
- GET `/api/v1/assets/image/{filename}?quality=low`
- GET `/api/v1/assets/image/{filename}/info`

**Component:**
```typescript
// components/ui/SmartImage.tsx
'use client';
import { useEffect, useState } from 'react';
import Image from 'next/image';

export default function SmartImage({ src, alt }: { src: string; alt: string }) {
  const [quality, setQuality] = useState<'low' | 'medium' | 'high'>('auto');
  const [connection, setConnection] = useState<any>(null);

  useEffect(() => {
    // Detect network quality
    const conn = (navigator as any).connection || (navigator as any).mozConnection;
    if (conn) {
      const effectiveType = conn.effectiveType;
      if (effectiveType === '2g' || effectiveType === 'slow-2g') {
        setQuality('low');
      } else if (effectiveType === '3g') {
        setQuality('medium');
      } else {
        setQuality('high');
      }
    }
  }, []);

  const imageUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/assets/image/${src}?quality=${quality}`;

  return <Image src={imageUrl} alt={alt} width={800} height={600} />;
}
```

---

### Phase 3: Teacher Features (Week 5-6)

#### 8. Teacher Dashboard 👨‍🏫
**Endpoints:**
- GET `/api/v1/teacher/classrooms`
- POST `/api/v1/teacher/classrooms`
- GET `/api/v1/teacher/analytics/{classroom_id}`

---

## API Client Library

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL;

class APIClient {
  private getToken(): string | null {
    return localStorage.getItem('token');
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const token = this.getToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    };

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  // Auth
  async register(data: any) {
    return this.request('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(email: string, password: string) {
    return this.request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username: email, password }),
    });
  }

  async me() {
    return this.request('/api/v1/auth/me');
  }

  // Questions
  async getQuestions(params?: { subject?: string; topic?: string }) {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/questions/?${query}`);
  }

  async getRandomQuestions(subject: string, count: number = 10) {
    return this.request(`/api/v1/questions/random/${subject}?count=${count}`);
  }

  // AI
  async chatWithAI(message: string, history: any[]) {
    return this.request('/api/v1/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ message, history }),
    });
  }

  async explainAnswer(questionId: number, studentAnswer: number) {
    return this.request('/api/v1/ai/explain', {
      method: 'POST',
      body: JSON.stringify({
        question_id: questionId,
        student_answer: studentAnswer,
      }),
    });
  }

  // Billing
  async getPlans() {
    return this.request('/api/v1/billing/plans');
  }

  async initializePayment(planId: string, email: string) {
    return this.request('/api/v1/billing/initialize', {
      method: 'POST',
      body: JSON.stringify({ plan_id: planId, email }),
    });
  }

  async getSubscription() {
    return this.request('/api/v1/billing/subscription');
  }

  // Sync
  async syncPull() {
    return this.request('/api/v1/sync/pull', { method: 'POST' });
  }

  async syncPush(data: any) {
    return this.request('/api/v1/sync/push', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const api = new APIClient();
export default api;
```

---

## PWA Configuration

### next.config.js
```javascript
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
});

module.exports = withPWA({
  reactStrictMode: true,
});
```

### public/manifest.json
```json
{
  "name": "Base10 - Education for Everyone",
  "short_name": "Base10",
  "description": "Offline-first education platform for rural African students",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#2563eb",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

---

## Testing the Integration

### 1. Test Authentication
```bash
# Register a test user
curl -X POST https://stingray-app-x7lzo.ondigitalocean.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "frontend-test@example.com",
    "password": "Test123!",
    "full_name": "Frontend Test",
    "education_level": "SECONDARY",
    "country": "Nigeria"
  }'
```

### 2. Test in Browser Console
```javascript
// In browser console
const API_URL = 'https://stingray-app-x7lzo.ondigitalocean.app';

// Login
const loginResponse = await fetch(`${API_URL}/api/v1/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'frontend-test@example.com',
    password: 'Test123!'
  })
});
const { access_token } = await loginResponse.json();
console.log('Token:', access_token);

// Get questions
const questionsResponse = await fetch(`${API_URL}/api/v1/questions/`, {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const questions = await questionsResponse.json();
console.log('Questions:', questions);
```

---

## Deployment: Frontend to Vercel

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial frontend commit"
git remote add origin https://github.com/HexAI-inc/Base10-Frontend.git
git push -u origin main
```

### 2. Deploy to Vercel
```bash
npm install -g vercel
vercel login
vercel --prod
```

### 3. Configure Environment Variables in Vercel
- `NEXT_PUBLIC_API_URL` = https://stingray-app-x7lzo.ondigitalocean.app
- `NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY` = pk_test_...

---

## Success Metrics

### Week 1-2 (MVP)
- [ ] User can register and login
- [ ] User can view and answer questions
- [ ] Offline mode works (cached questions)
- [ ] Progress is synced when online

### Week 3-4 (Enhanced)
- [ ] AI chat interface functional
- [ ] Subscription plans displayed
- [ ] Payment flow works (Paystack)
- [ ] Image optimization based on network

### Week 5-6 (Complete)
- [ ] Teacher dashboard functional
- [ ] Analytics displayed correctly
- [ ] PWA installable on mobile
- [ ] All 46 endpoints integrated

---

## Resources

- **Backend API:** https://stingray-app-x7lzo.ondigitalocean.app
- **API Docs:** https://stingray-app-x7lzo.ondigitalocean.app/docs
- **Next.js Docs:** https://nextjs.org/docs
- **Tailwind Docs:** https://tailwindcss.com/docs
- **Paystack Docs:** https://paystack.com/docs
- **React Query:** https://tanstack.com/query

---

## Let's Build! 🚀

Your backend is live and ready. Time to create an amazing frontend experience!

**Next command:**
```bash
npx create-next-app@latest base10-frontend --typescript --tailwind --app
```

---

*Ready to change education in Africa, one student at a time.* 🌍
