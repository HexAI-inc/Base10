// ==========================================
// ENHANCED FEATURES FOR WAEC TUTOR
// ==========================================

// ========== STATE MANAGEMENT ==========
const AppState = {
    currentQuiz: null,
    quizScore: 0,
    quizTotal: 0,
    quizAnswers: {},
    studyStreak: 0,
    totalQuizzes: 0,
    achievements: [],
    preferences: {},
    stats: {
        totalCorrect: 0,
        totalAttempted: 0,
        subjectStats: {}
    }
};

// ========== LOCAL STORAGE ==========
const Storage = {
    save(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Storage error:', e);
        }
    },
    
    load(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Storage error:', e);
            return defaultValue;
        }
    },
    
    clear(key) {
        localStorage.removeItem(key);
    }
};

// Initialize state from storage
function initializeState() {
    AppState.studyStreak = Storage.load('studyStreak', 0);
    AppState.totalQuizzes = Storage.load('totalQuizzes', 0);
    AppState.achievements = Storage.load('achievements', []);
    AppState.stats = Storage.load('stats', {
        totalCorrect: 0,
        totalAttempted: 0,
        subjectStats: {}
    });
    AppState.preferences = Storage.load('preferences', {
        theme: 'dark',
        notifications: true,
        sounds: true,
        difficulty: 'medium'
    });
    
    // Update streak on load
    updateStreak();
    
    // Restore chat history
    const savedHistory = Storage.load('chatHistory');
    if (savedHistory && window.location.hash === '#restore') {
        chatHistory = savedHistory;
        restoreChatUI();
    }
}

function updateStreak() {
    const lastVisit = Storage.load('lastVisit');
    const today = new Date().toDateString();
    
    if (lastVisit === today) {
        // Already visited today
        return;
    }
    
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (lastVisit === yesterday.toDateString()) {
        // Consecutive day
        AppState.studyStreak++;
    } else if (lastVisit !== today) {
        // Streak broken
        AppState.studyStreak = 1;
    }
    
    Storage.save('lastVisit', today);
    Storage.save('studyStreak', AppState.studyStreak);
    updateStreakDisplay();
}

function updateStreakDisplay() {
    const streakEl = document.getElementById('streak-display');
    if (streakEl && AppState.studyStreak > 0) {
        streakEl.innerHTML = `🔥 ${AppState.studyStreak} day streak`;
        streakEl.classList.remove('hidden');
    }
}

// ========== TOAST NOTIFICATIONS ==========
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} animate-slide-up`;
    
    const icons = {
        success: '✓',
        error: '✗',
        info: 'ℹ',
        warning: '⚠'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed top-20 right-4 z-50 flex flex-col gap-2';
    document.body.appendChild(container);
    return container;
}

// ========== QUIZ PROGRESS & SCORING ==========
let currentQuizState = {
    questions: [],
    currentIndex: 0,
    answers: {},
    startTime: null,
    timerInterval: null,
    timedMode: false,
    timeLimit: 300 // 5 minutes default
};

function initQuizProgress(questions, timedMode = false) {
    currentQuizState = {
        questions: questions,
        currentIndex: 0,
        answers: {},
        startTime: Date.now(),
        timerInterval: null,
        timedMode: timedMode,
        timeLimit: 300
    };
    
    if (timedMode) {
        startQuizTimer();
    }
    
    updateQuizProgress();
}

function updateQuizProgress() {
    const progressEl = document.getElementById('quiz-progress');
    if (!progressEl) return;
    
    const { questions, currentIndex } = currentQuizState;
    const answered = Object.keys(currentQuizState.answers).length;
    const total = questions.length;
    const percent = (answered / total) * 100;
    
    progressEl.innerHTML = `
        <div class="flex items-center justify-between mb-2 text-xs">
            <span>Progress: ${answered}/${total}</span>
            <span>${Math.round(percent)}%</span>
        </div>
        <div class="w-full bg-gray-700 rounded-full h-2">
            <div class="bg-gradient-to-r from-brand-500 to-brand-400 h-2 rounded-full transition-all duration-500" 
                 style="width: ${percent}%"></div>
        </div>
    `;
}

function startQuizTimer() {
    const timerEl = document.getElementById('quiz-timer');
    if (!timerEl) return;
    
    timerEl.classList.remove('hidden');
    
    currentQuizState.timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - currentQuizState.startTime) / 1000);
        const remaining = currentQuizState.timeLimit - elapsed;
        
        if (remaining <= 0) {
            clearInterval(currentQuizState.timerInterval);
            autoSubmitQuiz();
            return;
        }
        
        const minutes = Math.floor(remaining / 60);
        const seconds = remaining % 60;
        timerEl.innerHTML = `⏱️ ${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        if (remaining <= 30) {
            timerEl.classList.add('text-red-500', 'animate-pulse');
        }
    }, 1000);
}

function calculateQuizScore() {
    const { questions, answers } = currentQuizState;
    let correct = 0;
    
    questions.forEach((q, idx) => {
        if (answers[q.id] === q.correct_index) {
            correct++;
        }
    });
    
    return {
        correct,
        total: questions.length,
        percentage: Math.round((correct / questions.length) * 100)
    };
}

function showQuizResults() {
    const score = calculateQuizScore();
    const timeTaken = Math.floor((Date.now() - currentQuizState.startTime) / 1000);
    
    // Update stats
    AppState.stats.totalCorrect += score.correct;
    AppState.stats.totalAttempted += score.total;
    AppState.totalQuizzes++;
    
    Storage.save('stats', AppState.stats);
    Storage.save('totalQuizzes', AppState.totalQuizzes);
    
    // Check for achievements
    checkAchievements(score);
    
    // Show modal
    showResultsModal(score, timeTaken);
    
    // Confetti for good scores
    if (score.percentage >= 80) {
        triggerConfetti();
    }
}

function showResultsModal(score, timeTaken) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm';
    
    const minutes = Math.floor(timeTaken / 60);
    const seconds = timeTaken % 60;
    
    const getMessage = (percentage) => {
        if (percentage === 100) return { text: '🎉 Perfect Score!', color: 'text-yellow-400' };
        if (percentage >= 80) return { text: '🌟 Excellent!', color: 'text-green-400' };
        if (percentage >= 60) return { text: '👍 Good Job!', color: 'text-blue-400' };
        if (percentage >= 40) return { text: '📚 Keep Practicing!', color: 'text-orange-400' };
        return { text: '💪 Don\'t Give Up!', color: 'text-red-400' };
    };
    
    const message = getMessage(score.percentage);
    
    modal.innerHTML = `
        <div class="bg-dark-card rounded-3xl p-8 max-w-md w-full mx-4 shadow-2xl border border-dark-border animate-slide-up">
            <div class="text-center">
                <h2 class="font-display text-3xl font-bold mb-2 ${message.color}">${message.text}</h2>
                <p class="text-gray-400 mb-6">Quiz Complete</p>
                
                <div class="bg-dark-bg rounded-2xl p-6 mb-6">
                    <div class="text-6xl font-bold mb-2 text-brand-500">${score.percentage}%</div>
                    <div class="text-gray-400">${score.correct} out of ${score.total} correct</div>
                </div>
                
                <div class="grid grid-cols-2 gap-4 mb-6 text-sm">
                    <div class="bg-dark-bg rounded-xl p-4">
                        <div class="text-gray-400 mb-1">Time Taken</div>
                        <div class="font-bold text-brand-400">${minutes}m ${seconds}s</div>
                    </div>
                    <div class="bg-dark-bg rounded-xl p-4">
                        <div class="text-gray-400 mb-1">Total Quizzes</div>
                        <div class="font-bold text-brand-400">${AppState.totalQuizzes}</div>
                    </div>
                </div>
                
                <div class="flex gap-3">
                    <button id="back-to-chat-btn" class="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-3 rounded-xl font-bold transition">
                        Back to Chat
                    </button>
                    <button id="try-again-btn" class="flex-1 bg-brand-500 hover:bg-brand-600 text-white py-3 rounded-xl font-bold transition">
                        Try Again
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add event listeners
    modal.querySelector('#back-to-chat-btn').addEventListener('click', () => {
        console.log('[back-to-chat] Closing results modal');
        modal.remove();
        // Ensure chat interface is visible
        const chatInterface = document.getElementById('chat-interface');
        if (chatInterface) {
            chatInterface.style.transform = 'translateY(0)';
        }
        // DON'T remove quiz container - keep it visible in chat
        // Scroll to bottom to show quiz
        const chatBox = document.getElementById('chat-box');
        setTimeout(() => {
            chatBox.scrollTo({
                top: chatBox.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    });
    
    modal.querySelector('#try-again-btn').addEventListener('click', () => {
        modal.remove();
        showDifficultySelector();
    });
    
    // Close on backdrop click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

// ========== CONFETTI ANIMATION ==========
function triggerConfetti() {
    const duration = 3000;
    const end = Date.now() + duration;
    
    const colors = ['#22c55e', '#16a34a', '#4ade80', '#FFD700'];
    
    (function frame() {
        confetti({
            particleCount: 3,
            angle: 60,
            spread: 55,
            origin: { x: 0 },
            colors: colors
        });
        confetti({
            particleCount: 3,
            angle: 120,
            spread: 55,
            origin: { x: 1 },
            colors: colors
        });

        if (Date.now() < end) {
            requestAnimationFrame(frame);
        }
    }());
}

// ========== ACHIEVEMENTS ==========
const ACHIEVEMENTS = [
    { id: 'first_quiz', name: 'First Steps', description: 'Complete your first quiz', icon: '🎯' },
    { id: 'perfect_score', name: 'Perfectionist', description: 'Score 100% on a quiz', icon: '💯' },
    { id: 'quiz_10', name: 'Dedicated', description: 'Complete 10 quizzes', icon: '📚' },
    { id: 'quiz_50', name: 'Scholar', description: 'Complete 50 quizzes', icon: '🎓' },
    { id: 'streak_7', name: 'Weekly Warrior', description: '7 day study streak', icon: '🔥' },
    { id: 'streak_30', name: 'Consistent Champion', description: '30 day study streak', icon: '👑' }
];

function checkAchievements(score) {
    const newAchievements = [];
    
    if (AppState.totalQuizzes === 1 && !hasAchievement('first_quiz')) {
        newAchievements.push('first_quiz');
    }
    
    if (score.percentage === 100 && !hasAchievement('perfect_score')) {
        newAchievements.push('perfect_score');
    }
    
    if (AppState.totalQuizzes === 10 && !hasAchievement('quiz_10')) {
        newAchievements.push('quiz_10');
    }
    
    if (AppState.totalQuizzes === 50 && !hasAchievement('quiz_50')) {
        newAchievements.push('quiz_50');
    }
    
    if (AppState.studyStreak === 7 && !hasAchievement('streak_7')) {
        newAchievements.push('streak_7');
    }
    
    if (AppState.studyStreak === 30 && !hasAchievement('streak_30')) {
        newAchievements.push('streak_30');
    }
    
    newAchievements.forEach(id => {
        AppState.achievements.push(id);
        const achievement = ACHIEVEMENTS.find(a => a.id === id);
        showAchievementUnlock(achievement);
    });
    
    if (newAchievements.length > 0) {
        Storage.save('achievements', AppState.achievements);
    }
}

function hasAchievement(id) {
    return AppState.achievements.includes(id);
}

function showAchievementUnlock(achievement) {
    showToast(`${achievement.icon} Achievement Unlocked: ${achievement.name}`, 'success', 5000);
    
    if (AppState.preferences.sounds) {
        playAchievementSound();
    }
}

function playAchievementSound() {
    const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRA==');
    audio.volume = 0.3;
    audio.play().catch(() => {});
}

// ========== COPY & REGENERATE ==========
function addMessageControls(bubbleElement, messageContent, isAI = false) {
    if (!isAI) return;
    
    const controls = document.createElement('div');
    controls.className = 'message-controls flex gap-2 mt-2 pt-2 border-t border-gray-700/50';
    
    controls.innerHTML = `
        <button onclick="copyMessage(this)" data-content="${escapeHtml(messageContent)}" 
            class="control-btn" title="Copy">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
            </svg>
        </button>
        <button onclick="regenerateResponse()" class="control-btn" title="Regenerate">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
        </button>
    `;
    
    bubbleElement.appendChild(controls);
}

function copyMessage(button) {
    const content = button.getAttribute('data-content');
    navigator.clipboard.writeText(content).then(() => {
        showToast('Message copied!', 'success', 2000);
    }).catch(() => {
        showToast('Failed to copy', 'error', 2000);
    });
}

function regenerateResponse() {
    if (chatHistory.length < 2) return;
    
    // Remove last AI response
    chatHistory.pop();
    const lastUserMsg = chatHistory[chatHistory.length - 1];
    
    // Remove last bubble from UI
    const chatBox = document.getElementById('chat-box');
    const bubbles = chatBox.querySelectorAll('.chat-bubble');
    if (bubbles.length > 0) {
        bubbles[bubbles.length - 1].remove();
    }
    
    // Resend
    sendMessage(lastUserMsg.content);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========== EXPORT CHAT ==========
function exportChat() {
    const chatBox = document.getElementById('chat-box');
    const bubbles = chatBox.querySelectorAll('.chat-bubble');
    
    let text = `WaeGPT Chat Export\n`;
    text += `Date: ${new Date().toLocaleString()}\n`;
    text += `Subject: ${document.getElementById('subject').value}\n`;
    text += `${'='.repeat(50)}\n\n`;
    
    bubbles.forEach(bubble => {
        const isUser = bubble.classList.contains('user-msg');
        const content = bubble.querySelector('div').textContent;
        text += `${isUser ? 'You' : 'WaeGPT'}: ${content}\n\n`;
    });
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `waegpt-chat-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    
    showToast('Chat exported!', 'success');
}

// ========== KEYBOARD SHORTCUTS ==========
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to send message
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            sendMessage();
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            document.querySelectorAll('.fixed.z-50').forEach(modal => modal.remove());
        }
        
        // Ctrl/Cmd + K for quick quiz
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            triggerQuiz();
        }
        
        // Ctrl/Cmd + E to export
        if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
            e.preventDefault();
            exportChat();
        }
    });
}

// ========== TYPING INDICATOR ==========
function showTypingIndicator() {
    const chatBox = document.getElementById('chat-box');
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'chat-bubble ai-msg flex items-center gap-2';
    indicator.innerHTML = `
        <div class="flex gap-1">
            <div class="w-2 h-2 bg-brand-500 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
            <div class="w-2 h-2 bg-brand-500 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
            <div class="w-2 h-2 bg-brand-500 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
        </div>
        <span class="text-xs text-gray-400">WaeGPT is thinking...</span>
    `;
    chatBox.appendChild(indicator);
    chatBox.scrollTop = chatBox.scrollHeight;
    return indicator;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

// ========== DIFFICULTY SELECTOR ==========
function showDifficultySelector() {
    console.log('[showDifficultySelector] Opening difficulty modal');
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm';
    modal.id = 'difficulty-modal';
    
    modal.innerHTML = `
        <div class="bg-dark-card rounded-3xl p-8 max-w-md w-full mx-4 shadow-2xl border border-dark-border animate-slide-up">
            <h2 class="font-display text-2xl font-bold mb-4">Select Difficulty</h2>
            <div class="flex flex-col gap-3">
                <button data-difficulty="easy" class="difficulty-btn bg-green-600 hover:bg-green-500">
                    <span class="text-2xl">😊</span>
                    <div>
                        <div class="font-bold">Easy</div>
                        <div class="text-xs opacity-75">5 simple questions</div>
                    </div>
                </button>
                <button data-difficulty="medium" class="difficulty-btn bg-yellow-600 hover:bg-yellow-500">
                    <span class="text-2xl">🤔</span>
                    <div>
                        <div class="font-bold">Medium</div>
                        <div class="text-xs opacity-75">10 standard questions</div>
                    </div>
                </button>
                <button data-difficulty="hard" class="difficulty-btn bg-red-600 hover:bg-red-500">
                    <span class="text-2xl">🔥</span>
                    <div>
                        <div class="font-bold">Hard</div>
                        <div class="text-xs opacity-75">20 challenging questions</div>
                    </div>
                </button>
            </div>
            <button id="cancel-difficulty" class="w-full mt-4 py-3 border border-gray-600 rounded-xl hover:bg-gray-700 transition">
                Cancel
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add event listeners to difficulty buttons
    modal.querySelectorAll('[data-difficulty]').forEach(btn => {
        btn.addEventListener('click', function() {
            const difficulty = this.getAttribute('data-difficulty');
            modal.remove(); // Remove modal immediately
            startQuizWithDifficulty(difficulty);
        });
    });
    
    // Add event listener to cancel button
    modal.querySelector('#cancel-difficulty').addEventListener('click', () => {
        modal.remove();
    });
    
    // Close on backdrop click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

function startQuizWithDifficulty(difficulty) {
    console.log('[startQuizWithDifficulty] Called with difficulty:', difficulty);
    AppState.preferences.difficulty = difficulty;
    Storage.save('preferences', AppState.preferences);
    
    // Use pending context from conversation if available
    const context = window.pendingQuizContext || {};
    console.log('[startQuizWithDifficulty] Context:', context);
    const subject = context.subject || document.getElementById('subject').value;
    const topic = context.topic || "General";
    const questionCount = difficulty === 'easy' ? 5 : difficulty === 'medium' ? 10 : 20;
    
    console.log('[startQuizWithDifficulty] Starting quiz:', { subject, topic, difficulty, questionCount });
    showToast(`Starting ${difficulty} quiz on ${topic}`, 'info');
    
    // Call startQuiz directly with difficulty parameters
    startQuiz(subject, topic, difficulty, questionCount);
    
    // Clear pending context
    window.pendingQuizContext = null;
}

// ========== STUDY STATS PANEL ==========
function showStatsPanel() {
    const stats = AppState.stats;
    const accuracy = stats.totalAttempted > 0 
        ? Math.round((stats.totalCorrect / stats.totalAttempted) * 100) 
        : 0;
    
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm';
    
    modal.innerHTML = `
        <div class="bg-dark-card rounded-3xl p-8 max-w-2xl w-full mx-4 shadow-2xl border border-dark-border animate-slide-up max-h-[80vh] overflow-y-auto">
            <h2 class="font-display text-3xl font-bold mb-6">📊 Your Statistics</h2>
            
            <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="bg-dark-bg rounded-xl p-4">
                    <div class="text-gray-400 text-sm mb-1">Total Quizzes</div>
                    <div class="text-3xl font-bold text-brand-500">${AppState.totalQuizzes}</div>
                </div>
                <div class="bg-dark-bg rounded-xl p-4">
                    <div class="text-gray-400 text-sm mb-1">Accuracy</div>
                    <div class="text-3xl font-bold text-brand-500">${accuracy}%</div>
                </div>
                <div class="bg-dark-bg rounded-xl p-4">
                    <div class="text-gray-400 text-sm mb-1">Study Streak</div>
                    <div class="text-3xl font-bold text-brand-500">🔥 ${AppState.studyStreak}</div>
                </div>
                <div class="bg-dark-bg rounded-xl p-4">
                    <div class="text-gray-400 text-sm mb-1">Achievements</div>
                    <div class="text-3xl font-bold text-brand-500">${AppState.achievements.length}</div>
                </div>
            </div>
            
            <div class="mb-6">
                <h3 class="font-bold text-lg mb-3">🏆 Achievements</h3>
                <div class="grid grid-cols-2 gap-2">
                    ${ACHIEVEMENTS.map(ach => `
                        <div class="bg-dark-bg rounded-lg p-3 ${hasAchievement(ach.id) ? 'opacity-100' : 'opacity-30'}">
                            <div class="text-2xl mb-1">${ach.icon}</div>
                            <div class="font-bold text-sm">${ach.name}</div>
                            <div class="text-xs text-gray-400">${ach.description}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <button id="close-stats-btn" class="w-full py-3 bg-brand-500 hover:bg-brand-600 rounded-xl font-bold transition">
                Close
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add event listeners
    modal.querySelector('#close-stats-btn').addEventListener('click', () => {
        modal.remove();
    });
    
    // Close on backdrop click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

// ========== QUIZ-BASED FLASHCARD MODE (Legacy) ==========
let quizFlashcardDeck = [];
let currentQuizFlashcard = 0;

function convertQuizToFlashcards(questions) {
    flashcardDeck = questions.map(q => ({
        front: q.question,
        back: q.options[q.correct_index],
        explanation: q.explanation
    }));
    
    currentFlashcard = 0;
    showFlashcardUI();
}

function showFlashcardUI() {
    if (flashcardDeck.length === 0) return;
    
    const modal = document.createElement('div');
    modal.id = 'flashcard-modal';
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm';
    
    renderFlashcard(modal);
    document.body.appendChild(modal);
}

function renderQuizFlashcard(container) {
    const card = quizFlashcardDeck[currentQuizFlashcard];
    const total = quizFlashcardDeck.length;
    
    container.innerHTML = `
        <div class="bg-dark-card rounded-3xl p-8 max-w-lg w-full mx-4 shadow-2xl border border-dark-border">
            <div class="flex justify-between items-center mb-6">
                <span class="text-sm text-gray-400">${currentQuizFlashcard + 1} / ${total}</span>
                <button id="close-flashcard-btn" class="text-gray-400 hover:text-white">✕</button>
            </div>
            
            <div id="flashcard-content" class="flashcard mb-6 cursor-pointer">
                <div class="flashcard-front">
                    <div class="text-center p-8 min-h-[200px] flex items-center justify-center">
                        <p class="text-lg">${card.front}</p>
                    </div>
                </div>
                <div class="flashcard-back hidden">
                    <div class="text-center p-8 min-h-[200px] flex flex-col items-center justify-center">
                        <p class="text-xl font-bold text-brand-500 mb-2">${card.back}</p>
                        <p class="text-sm text-gray-400">${card.explanation}</p>
                    </div>
                </div>
            </div>
            
            <div class="flex justify-between">
                <button id="prev-flashcard-btn" ${currentQuizFlashcard === 0 ? 'disabled' : ''} 
                    class="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-xl disabled:opacity-30">
                    ← Previous
                </button>
                <button id="next-flashcard-btn" ${currentQuizFlashcard === total - 1 ? 'disabled' : ''} 
                    class="px-6 py-3 bg-brand-500 hover:bg-brand-600 rounded-xl disabled:opacity-30">
                    Next →
                </button>
            </div>
        </div>
    `;
    
    // Add event listeners
    container.querySelector('#close-flashcard-btn').addEventListener('click', () => {
        container.remove();
    });
    
    container.querySelector('#flashcard-content').addEventListener('click', flipQuizFlashcard);
    
    container.querySelector('#prev-flashcard-btn').addEventListener('click', prevQuizFlashcard);
    
    container.querySelector('#next-flashcard-btn').addEventListener('click', nextQuizFlashcard);
    
    // Render KaTeX for math expressions
    if (typeof renderMathInElement !== 'undefined') {
        try {
            const flashcardContent = container.querySelector('#flashcard-content');
            renderMathInElement(flashcardContent, {
                delimiters: [
                    {left: "$$", right: "$$", display: true},
                    {left: "$", right: "$", display: false},
                    {left: "\\(", right: "\\)", display: false},
                    {left: "\\[", right: "\\]", display: true}
                ],
                throwOnError: false,
                strict: false,
                trust: true
            });
        } catch (e) {
            console.error('[renderFlashcard] KaTeX error:', e);
        }
    }
}

function flipQuizFlashcard() {
    const front = document.querySelector('.flashcard-front');
    const back = document.querySelector('.flashcard-back');
    
    if (front.classList.contains('hidden')) {
        front.classList.remove('hidden');
        back.classList.add('hidden');
    } else {
        front.classList.add('hidden');
        back.classList.remove('hidden');
    }
}

function nextQuizFlashcard() {
    if (currentQuizFlashcard < quizFlashcardDeck.length - 1) {
        currentQuizFlashcard++;
        renderQuizFlashcard(document.getElementById('quiz-flashcard-modal'));
    }
}

function prevQuizFlashcard() {
    if (currentQuizFlashcard > 0) {
        currentQuizFlashcard--;
        renderQuizFlashcard(document.getElementById('quiz-flashcard-modal'));
    }
}

// ========== INITIALIZE ON LOAD ==========
document.addEventListener('DOMContentLoaded', () => {
    initializeState();
    initKeyboardShortcuts();
    
    // Show streak if exists
    if (AppState.studyStreak > 0) {
        setTimeout(() => {
            showToast(`🔥 ${AppState.studyStreak} day streak! Keep it up!`, 'success', 4000);
        }, 1000);
    }
});

// Auto-save chat history periodically
setInterval(() => {
    if (chatHistory.length > 0) {
        Storage.save('chatHistory', chatHistory);
    }
}, 30000); // Every 30 seconds
