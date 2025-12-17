// ==========================================
// MOBILE-SPECIFIC ENHANCEMENTS
// ==========================================

// Detect mobile device
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

// ========== HAPTIC FEEDBACK ==========
function triggerHaptic(type = 'light') {
    if (!isMobile || !navigator.vibrate) return;
    
    const patterns = {
        light: [10],
        medium: [20],
        heavy: [30],
        success: [10, 20, 10],
        error: [20, 10, 20, 10, 20]
    };
    
    navigator.vibrate(patterns[type] || patterns.light);
}

// ========== SWIPE GESTURES ==========
class SwipeHandler {
    constructor(element, callbacks) {
        this.element = element;
        this.callbacks = callbacks;
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchEndX = 0;
        this.touchEndY = 0;
        this.minSwipeDistance = 50;
        
        this.init();
    }
    
    init() {
        this.element.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
            this.touchStartY = e.changedTouches[0].screenY;
        });
        
        this.element.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.touchEndY = e.changedTouches[0].screenY;
            this.handleSwipe();
        });
    }
    
    handleSwipe() {
        const deltaX = this.touchEndX - this.touchStartX;
        const deltaY = this.touchEndY - this.touchStartY;
        
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > this.minSwipeDistance) {
            if (deltaX > 0) {
                this.callbacks.onSwipeRight?.();
            } else {
                this.callbacks.onSwipeLeft?.();
            }
        } else if (Math.abs(deltaY) > this.minSwipeDistance) {
            if (deltaY > 0) {
                this.callbacks.onSwipeDown?.();
            } else {
                this.callbacks.onSwipeUp?.();
            }
        }
    }
}

// ========== PULL TO REFRESH ==========
class PullToRefresh {
    constructor(element, onRefresh) {
        this.element = element;
        this.onRefresh = onRefresh;
        this.startY = 0;
        this.pullDistance = 0;
        this.threshold = 80;
        this.indicator = null;
        
        this.init();
    }
    
    init() {
        this.createIndicator();
        
        this.element.addEventListener('touchstart', (e) => {
            if (this.element.scrollTop === 0) {
                this.startY = e.touches[0].clientY;
            }
        });
        
        this.element.addEventListener('touchmove', (e) => {
            if (this.startY === 0 || this.element.scrollTop > 0) return;
            
            const currentY = e.touches[0].clientY;
            this.pullDistance = currentY - this.startY;
            
            if (this.pullDistance > 0) {
                this.updateIndicator(this.pullDistance);
                e.preventDefault();
            }
        });
        
        this.element.addEventListener('touchend', () => {
            if (this.pullDistance > this.threshold) {
                this.triggerRefresh();
            }
            this.resetIndicator();
            this.startY = 0;
            this.pullDistance = 0;
        });
    }
    
    createIndicator() {
        this.indicator = document.createElement('div');
        this.indicator.className = 'pull-refresh-indicator';
        this.indicator.innerHTML = '<div class="spinner"></div>';
        this.element.prepend(this.indicator);
    }
    
    updateIndicator(distance) {
        const progress = Math.min(distance / this.threshold, 1);
        this.indicator.style.transform = `translateY(${distance * 0.5}px)`;
        this.indicator.style.opacity = progress;
    }
    
    resetIndicator() {
        this.indicator.style.transform = 'translateY(-50px)';
        this.indicator.style.opacity = '0';
    }
    
    async triggerRefresh() {
        this.indicator.classList.add('refreshing');
        triggerHaptic('medium');
        await this.onRefresh();
        setTimeout(() => {
            this.indicator.classList.remove('refreshing');
            this.resetIndicator();
        }, 1000);
    }
}

// ========== BOTTOM SHEET ==========
function showBottomSheet(content, options = {}) {
    const sheet = document.createElement('div');
    sheet.className = 'bottom-sheet-overlay';
    
    const sheetContent = document.createElement('div');
    sheetContent.className = 'bottom-sheet';
    sheetContent.innerHTML = `
        <div class="bottom-sheet-handle"></div>
        <div class="bottom-sheet-content">
            ${content}
        </div>
    `;
    
    sheet.appendChild(sheetContent);
    document.body.appendChild(sheet);
    
    // Animate in
    setTimeout(() => {
        sheet.classList.add('active');
    }, 10);
    
    // Close on overlay click
    sheet.addEventListener('click', (e) => {
        if (e.target === sheet) {
            closeBottomSheet(sheet);
        }
    });
    
    // Swipe down to close
    new SwipeHandler(sheetContent, {
        onSwipeDown: () => closeBottomSheet(sheet)
    });
    
    return sheet;
}

function closeBottomSheet(sheet) {
    sheet.classList.remove('active');
    setTimeout(() => sheet.remove(), 300);
}

// ========== MOBILE-OPTIMIZED QUIZ NAVIGATION ==========
function showMobileQuizNavigation(questions) {
    const content = `
        <h3 class="text-xl font-bold mb-4">Quiz Navigation</h3>
        <div class="grid grid-cols-5 gap-2 mb-4">
            ${questions.map((q, i) => {
                const answered = currentQuizState.answers[q.id] !== undefined;
                return `
                    <button onclick="scrollToQuestion(${i}); closeBottomSheet(this.closest('.bottom-sheet-overlay'))" 
                        class="w-12 h-12 rounded-full ${answered ? 'bg-brand-500' : 'bg-gray-700'} font-bold">
                        ${i + 1}
                    </button>
                `;
            }).join('')}
        </div>
        <button onclick="closeBottomSheet(this.closest('.bottom-sheet-overlay'))" 
            class="w-full py-3 bg-gray-700 rounded-xl font-bold">
            Close
        </button>
    `;
    
    showBottomSheet(content);
}

function scrollToQuestion(index) {
    const questions = document.querySelectorAll('.quiz-question');
    if (questions[index]) {
        questions[index].scrollIntoView({ behavior: 'smooth', block: 'center' });
        triggerHaptic('light');
    }
}

// ========== MOBILE MENU ==========
function showMobileMenu() {
    const content = `
        <h3 class="text-xl font-bold mb-4">Menu</h3>
        <div class="space-y-2">
            <button onclick="showStatsPanel(); closeBottomSheet(this.closest('.bottom-sheet-overlay'))" 
                class="w-full p-4 bg-dark-bg rounded-xl text-left flex items-center gap-3">
                <span class="text-2xl">📊</span>
                <div>
                    <div class="font-bold">Statistics</div>
                    <div class="text-xs text-gray-400">View your progress</div>
                </div>
            </button>
            <button onclick="exportChat(); closeBottomSheet(this.closest('.bottom-sheet-overlay'))" 
                class="w-full p-4 bg-dark-bg rounded-xl text-left flex items-center gap-3">
                <span class="text-2xl">📥</span>
                <div>
                    <div class="font-bold">Export Chat</div>
                    <div class="text-xs text-gray-400">Save conversation</div>
                </div>
            </button>
            <button onclick="showKeyboardShortcuts(); closeBottomSheet(this.closest('.bottom-sheet-overlay'))" 
                class="w-full p-4 bg-dark-bg rounded-xl text-left flex items-center gap-3">
                <span class="text-2xl">⌨️</span>
                <div>
                    <div class="font-bold">Shortcuts</div>
                    <div class="text-xs text-gray-400">Keyboard shortcuts</div>
                </div>
            </button>
            <button onclick="showSettings(); closeBottomSheet(this.closest('.bottom-sheet-overlay'))" 
                class="w-full p-4 bg-dark-bg rounded-xl text-left flex items-center gap-3">
                <span class="text-2xl">⚙️</span>
                <div>
                    <div class="font-bold">Settings</div>
                    <div class="text-xs text-gray-400">Customize your experience</div>
                </div>
            </button>
        </div>
    `;
    
    showBottomSheet(content);
}

// ========== SETTINGS PANEL ==========
function showSettings() {
    const prefs = AppState.preferences;
    
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm';
    modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
    
    modal.innerHTML = `
        <div class="bg-dark-card rounded-3xl p-8 max-w-md w-full mx-4 shadow-2xl border border-dark-border animate-slide-up max-h-[80vh] overflow-y-auto">
            <h2 class="font-display text-2xl font-bold mb-6">⚙️ Settings</h2>
            
            <div class="space-y-4">
                <div class="flex justify-between items-center p-4 bg-dark-bg rounded-xl">
                    <div>
                        <div class="font-bold">Notifications</div>
                        <div class="text-xs text-gray-400">Achievement alerts</div>
                    </div>
                    <input type="checkbox" id="setting-notifications" ${prefs.notifications ? 'checked' : ''} 
                        onchange="updateSetting('notifications', this.checked)"
                        class="w-12 h-6 rounded-full appearance-none bg-gray-700 checked:bg-brand-500 relative cursor-pointer transition">
                </div>
                
                <div class="flex justify-between items-center p-4 bg-dark-bg rounded-xl">
                    <div>
                        <div class="font-bold">Sound Effects</div>
                        <div class="text-xs text-gray-400">Audio feedback</div>
                    </div>
                    <input type="checkbox" id="setting-sounds" ${prefs.sounds ? 'checked' : ''} 
                        onchange="updateSetting('sounds', this.checked)"
                        class="w-12 h-6 rounded-full appearance-none bg-gray-700 checked:bg-brand-500 relative cursor-pointer transition">
                </div>
                
                <div class="p-4 bg-dark-bg rounded-xl">
                    <div class="font-bold mb-3">Default Difficulty</div>
                    <select id="setting-difficulty" onchange="updateSetting('difficulty', this.value)"
                        class="w-full p-3 bg-gray-700 rounded-lg text-white">
                        <option value="easy" ${prefs.difficulty === 'easy' ? 'selected' : ''}>Easy</option>
                        <option value="medium" ${prefs.difficulty === 'medium' ? 'selected' : ''}>Medium</option>
                        <option value="hard" ${prefs.difficulty === 'hard' ? 'selected' : ''}>Hard</option>
                    </select>
                </div>
                
                <div class="p-4 bg-dark-bg rounded-xl">
                    <div class="font-bold mb-2">Data Management</div>
                    <button onclick="clearAllData()" 
                        class="w-full py-2 bg-red-600 hover:bg-red-500 rounded-lg font-bold transition">
                        Clear All Data
                    </button>
                </div>
            </div>
            
            <button onclick="this.closest('.fixed').remove()" 
                class="w-full mt-6 py-3 bg-brand-500 hover:bg-brand-600 rounded-xl font-bold transition">
                Done
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function updateSetting(key, value) {
    AppState.preferences[key] = value;
    Storage.save('preferences', AppState.preferences);
    showToast(`Setting updated: ${key}`, 'success', 2000);
    triggerHaptic('light');
}

function clearAllData() {
    if (confirm('Are you sure? This will delete all your progress, chat history, and achievements.')) {
        localStorage.clear();
        showToast('All data cleared', 'success');
        setTimeout(() => location.reload(), 1500);
    }
}

// ========== STUDY PLANNER ==========
function showStudyPlanner() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm';
    modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
    
    const studyPlan = Storage.load('studyPlan', []);
    
    modal.innerHTML = `
        <div class="bg-dark-card rounded-3xl p-8 max-w-md w-full mx-4 shadow-2xl border border-dark-border animate-slide-up max-h-[80vh] overflow-y-auto">
            <h2 class="font-display text-2xl font-bold mb-6">📅 Study Planner</h2>
            
            <div class="mb-6">
                <input type="text" id="study-topic" placeholder="Topic to study..." 
                    class="w-full p-3 bg-dark-bg rounded-xl mb-2 border border-gray-700 focus:border-brand-500 outline-none">
                <div class="flex gap-2">
                    <input type="date" id="study-date" 
                        class="flex-1 p-3 bg-dark-bg rounded-xl border border-gray-700 focus:border-brand-500 outline-none">
                    <button onclick="addStudyTask()" 
                        class="px-6 py-3 bg-brand-500 hover:bg-brand-600 rounded-xl font-bold transition">
                        Add
                    </button>
                </div>
            </div>
            
            <div id="study-plan-list" class="space-y-2 mb-6">
                ${studyPlan.length === 0 ? '<p class="text-gray-400 text-center py-4">No study tasks yet</p>' : 
                    studyPlan.map((task, i) => `
                        <div class="flex items-center justify-between p-3 bg-dark-bg rounded-xl">
                            <div>
                                <div class="font-bold">${task.topic}</div>
                                <div class="text-xs text-gray-400">${task.date}</div>
                            </div>
                            <button onclick="removeStudyTask(${i})" class="text-red-400 hover:text-red-300">
                                ✕
                            </button>
                        </div>
                    `).join('')}
            </div>
            
            <button onclick="this.closest('.fixed').remove()" 
                class="w-full py-3 bg-gray-700 hover:bg-gray-600 rounded-xl font-bold transition">
                Close
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function addStudyTask() {
    const topic = document.getElementById('study-topic').value.trim();
    const date = document.getElementById('study-date').value;
    
    if (!topic || !date) {
        showToast('Please fill in all fields', 'warning');
        return;
    }
    
    const studyPlan = Storage.load('studyPlan', []);
    studyPlan.push({ topic, date, completed: false });
    Storage.save('studyPlan', studyPlan);
    
    showToast('Study task added!', 'success');
    triggerHaptic('success');
    
    // Refresh the modal
    document.querySelector('.fixed.z-50').remove();
    showStudyPlanner();
}

function removeStudyTask(index) {
    const studyPlan = Storage.load('studyPlan', []);
    studyPlan.splice(index, 1);
    Storage.save('studyPlan', studyPlan);
    
    showToast('Task removed', 'info');
    
    // Refresh the modal
    document.querySelector('.fixed.z-50').remove();
    showStudyPlanner();
}

// ========== INITIALIZE MOBILE FEATURES ==========
if (isMobile) {
    document.addEventListener('DOMContentLoaded', () => {
        // Add pull to refresh
        const chatBox = document.getElementById('chat-box');
        if (chatBox) {
            new PullToRefresh(chatBox, async () => {
                await new Promise(resolve => setTimeout(resolve, 1000));
                showToast('Refreshed!', 'success');
            });
        }
        
        // Add swipe gestures to chat bubbles
        setTimeout(() => {
            document.querySelectorAll('.chat-bubble.user-msg').forEach(bubble => {
                new SwipeHandler(bubble, {
                    onSwipeLeft: () => {
                        bubble.style.transform = 'translateX(-20px)';
                        bubble.style.opacity = '0.5';
                        setTimeout(() => {
                            if (confirm('Delete this message?')) {
                                bubble.remove();
                            } else {
                                bubble.style.transform = '';
                                bubble.style.opacity = '';
                            }
                        }, 200);
                    }
                });
            });
        }, 1000);
    });
}
