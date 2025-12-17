// Standalone Flashcards Feature
let flashcardMode = 'quiz'; // 'quiz' or 'facts'
let currentFlashcardSet = [];
let currentFlashcardIndex = 0;
let flashcardStats = {
    known: 0,
    learning: 0,
    total: 0
};

// Show Flashcard Main Menu
function showFlashcardMenu() {
    const modal = document.createElement('div');
    modal.id = 'flashcard-menu-modal';
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4';
    
    modal.innerHTML = `
        <div class="bg-dark-card rounded-3xl p-6 md:p-8 max-w-2xl w-full mx-auto shadow-2xl border border-dark-border animate-slide-up max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-6">
                <h2 class="font-display text-2xl md:text-3xl font-bold text-brand-500">🎴 Flashcards</h2>
                <button onclick="closeFlashcardMenu()" class="text-gray-400 hover:text-white text-2xl">✕</button>
            </div>
            
            <!-- Mode Selection -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div onclick="selectFlashcardMode('quiz')" class="cursor-pointer p-6 bg-gradient-to-br from-brand-500/20 to-brand-600/10 rounded-2xl border-2 border-brand-500/30 hover:border-brand-500 transition group">
                    <div class="text-4xl mb-3">❓</div>
                    <h3 class="font-bold text-lg mb-2 group-hover:text-brand-400">Quiz Flashcards</h3>
                    <p class="text-sm text-gray-400">Practice with question & answer cards. Flip to reveal answers.</p>
                </div>
                
                <div onclick="selectFlashcardMode('facts')" class="cursor-pointer p-6 bg-gradient-to-br from-purple-500/20 to-purple-600/10 rounded-2xl border-2 border-purple-500/30 hover:border-purple-500 transition group">
                    <div class="text-4xl mb-3">💡</div>
                    <h3 class="font-bold text-lg mb-2 group-hover:text-purple-400">Topic Flashcards</h3>
                    <p class="text-sm text-gray-400">Learn key facts, formulas, and concepts about a topic.</p>
                </div>
            </div>
            
            <!-- Topic Selection -->
            <div class="mb-6">
                <label class="block text-sm font-semibold mb-2 text-gray-300">Select or Type Topic</label>
                <div class="flex gap-2">
                    <select id="flashcard-subject" class="flex-1 bg-dark-bg border border-gray-700 rounded-xl px-4 py-3 focus:border-brand-500 focus:outline-none">
                        <option value="Mathematics">Mathematics</option>
                        <option value="English Language">English Language</option>
                        <option value="Physics">Physics</option>
                        <option value="Chemistry">Chemistry</option>
                        <option value="Biology">Biology</option>
                        <option value="Economics">Economics</option>
                    </select>
                </div>
                <input type="text" id="flashcard-topic" placeholder="e.g., Algebra, Verbs, Motion..." 
                    class="mt-2 w-full bg-dark-bg border border-gray-700 rounded-xl px-4 py-3 focus:border-brand-500 focus:outline-none">
            </div>
            
            <!-- Quick Topic Suggestions -->
            <div class="mb-6">
                <label class="block text-sm font-semibold mb-2 text-gray-300">Quick Suggestions</label>
                <div class="flex flex-wrap gap-2">
                    <button onclick="setFlashcardTopic('Algebra')" class="px-4 py-2 bg-gray-700 hover:bg-brand-500 rounded-full text-sm transition">Algebra</button>
                    <button onclick="setFlashcardTopic('Geometry')" class="px-4 py-2 bg-gray-700 hover:bg-brand-500 rounded-full text-sm transition">Geometry</button>
                    <button onclick="setFlashcardTopic('Grammar')" class="px-4 py-2 bg-gray-700 hover:bg-brand-500 rounded-full text-sm transition">Grammar</button>
                    <button onclick="setFlashcardTopic('Motion')" class="px-4 py-2 bg-gray-700 hover:bg-brand-500 rounded-full text-sm transition">Motion</button>
                    <button onclick="setFlashcardTopic('Electricity')" class="px-4 py-2 bg-gray-700 hover:bg-brand-500 rounded-full text-sm transition">Electricity</button>
                    <button onclick="setFlashcardTopic('Acids and Bases')" class="px-4 py-2 bg-gray-700 hover:bg-brand-500 rounded-full text-sm transition">Acids & Bases</button>
                </div>
            </div>
            
            <!-- Generate Button -->
            <button onclick="generateFlashcards()" class="w-full py-4 bg-brand-500 hover:bg-brand-600 rounded-xl font-bold text-lg transition transform active:scale-95">
                Generate Flashcards
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function closeFlashcardMenu() {
    const modal = document.getElementById('flashcard-menu-modal');
    if (modal) modal.remove();
}

function selectFlashcardMode(mode) {
    flashcardMode = mode;
    console.log('[Flashcards] Mode selected:', mode);
}

function setFlashcardTopic(topic) {
    document.getElementById('flashcard-topic').value = topic;
}

async function generateFlashcards() {
    const subject = document.getElementById('flashcard-subject').value;
    const topic = document.getElementById('flashcard-topic').value.trim();
    
    if (!topic) {
        showToast('Please enter a topic', 'error');
        return;
    }
    
    closeFlashcardMenu();
    showToast(`Generating ${flashcardMode} flashcards for ${topic}...`, 'info');
    
    if (flashcardMode === 'quiz') {
        await generateQuizFlashcards(subject, topic);
    } else {
        await generateFactFlashcards(subject, topic);
    }
}

async function generateQuizFlashcards(subject, topic) {
    try {
        // Try to load from static JSON first
        const response = await fetch('/static/data/waec_questions.json');
        const allQuestions = await response.json();
        
        // Filter by subject (broader matching)
        const subjectLower = subject.toLowerCase();
        const topicLower = topic.toLowerCase();
        
        let filtered = allQuestions.filter(q => 
            q.subject.toLowerCase().includes(subjectLower) &&
            (q.topic.toLowerCase().includes(topicLower) || topicLower.includes(q.topic.toLowerCase()))
        );
        
        // If no exact topic match, try just subject
        if (filtered.length < 5) {
            filtered = allQuestions.filter(q => q.subject.toLowerCase().includes(subjectLower));
            console.log(`[Flashcards] Using broader subject match: ${filtered.length} questions`);
        }
        
        if (filtered.length >= 5) {
            // Use static questions - shuffle and take 15-20
            const shuffled = filtered.sort(() => Math.random() - 0.5);
            currentFlashcardSet = shuffled.slice(0, Math.min(20, filtered.length)).map((q, idx) => {
                // Get correct answer - answer is 'a', 'b', 'c', or 'd'
                const answerIndex = q.answer.toLowerCase().charCodeAt(0) - 97; // 'a' = 0, 'b' = 1, etc.
                const correctAnswer = q.options[answerIndex] || q.answer;
                
                return {
                    id: idx,
                    front: q.question,
                    back: correctAnswer,
                    options: q.options,
                    answer: q.answer,
                    explanation: q.explanation,
                    type: 'quiz'
                };
            });
            
            console.log(`[Flashcards] Loaded ${currentFlashcardSet.length} questions from static JSON`);
        } else {
            // Try AI generation as fallback
            console.log('[Flashcards] Insufficient static questions, trying AI generation...');
            
            try {
                const res = await fetch('/api/quiz', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ 
                        subject: subject,
                        topic: topic,
                        difficulty: 'medium',
                        question_count: 10
                    })
                });
                
                if (!res.ok) {
                    throw new Error(`API returned ${res.status}`);
                }
                
                const rawJson = await res.json();
                let data = typeof rawJson === 'string' ? JSON.parse(rawJson) : rawJson;
                
                if (data.questions && data.questions.length > 0) {
                    currentFlashcardSet = data.questions.map((q, idx) => {
                        const answerIndex = q.answer.toLowerCase().charCodeAt(0) - 97;
                        const correctAnswer = q.options[answerIndex] || q.answer;
                        
                        return {
                            id: idx,
                            front: q.question,
                            back: correctAnswer,
                            options: q.options,
                            answer: q.answer,
                            explanation: q.explanation,
                            type: 'quiz'
                        };
                    });
                    console.log('[Flashcards] Generated via AI');
                } else {
                    throw new Error('No questions in API response');
                }
            } catch (apiError) {
                console.error('[Flashcards] AI generation failed:', apiError);
                
                // Last resort: use ANY available questions from subject
                if (allQuestions.length > 0) {
                    const anySubject = allQuestions.filter(q => q.subject.toLowerCase().includes('math') || q.subject.toLowerCase().includes('english') || q.subject.toLowerCase().includes('physics'));
                    if (anySubject.length >= 5) {
                        const shuffled = anySubject.sort(() => Math.random() - 0.5);
                        currentFlashcardSet = shuffled.slice(0, 10).map((q, idx) => {
                            const answerIndex = q.answer.toLowerCase().charCodeAt(0) - 97;
                            const correctAnswer = q.options[answerIndex] || q.answer;
                            
                            return {
                                id: idx,
                                front: q.question,
                                back: correctAnswer,
                                options: q.options,
                                answer: q.answer,
                                explanation: q.explanation,
                                type: 'quiz'
                            };
                        });
                        console.log('[Flashcards] Using fallback questions');
                    } else {
                        throw new Error('No questions available');
                    }
                } else {
                    throw apiError;
                }
            }
        }
        
        if (currentFlashcardSet.length === 0) {
            throw new Error('No flashcards were generated');
        }
        
        currentFlashcardIndex = 0;
        flashcardStats = { known: 0, learning: 0, total: currentFlashcardSet.length };
        showFlashcardViewer();
        
    } catch (error) {
        console.error('[Flashcards] Fatal error:', error);
        showToast('Failed to generate quiz flashcards. Please try a different topic.', 'error');
    }
}

async function generateFactFlashcards(subject, topic) {
    try {
        // Generate topic facts using AI
        const prompt = `Generate exactly 10 educational flashcards about "${topic}" in ${subject} for WAEC students.

CRITICAL REQUIREMENTS:
1. Each flashcard must have a SHORT concept/term on the front (5-15 words maximum)
2. The back should have a clear, concise explanation (1-3 sentences, 20-50 words)
3. Use proper LaTeX for ALL mathematical and chemical notation
4. NEVER use LaTeX arrow commands - use plain text arrows (→, ←) or words instead

LaTeX RULES:
✓ CORRECT: Formulas in LaTeX: $E = mc^2$, $\\frac{a}{b}$, $x^2$, $\\sqrt{x}$
✓ CORRECT: Chemical formulas: $H^+$, $H_2O$, $SO_4^{2-}$, $Ca^{2+}$
✓ CORRECT: Greek letters: $\\theta$, $\\Delta$, $\\pi$, $\\alpha$
✓ CORRECT: Subscripts/superscripts: $x_1$, $y^2$, $10^3$
✓ CORRECT: Fractions: $\\frac{numerator}{denominator}$
✗ WRONG: Do NOT use \\rightarrow, \\leftarrow, \\to in JSON
✗ WRONG: Do NOT use \\text{} or \\mathrm{}
✗ WRONG: Plain text for units: kg, m/s, K, J (NOT in LaTeX)

ARROW ALTERNATIVES:
- Use → or ← (unicode arrows)
- Or use words: "produces", "yields", "forms", "leads to"
- Example: "$HCl + NaOH$ produces $NaCl + H_2O$" (not \\rightarrow)

Format as a valid JSON array with NO additional text:
[
  {"front": "Short concept", "back": "Clear explanation with $LaTeX$ if needed"},
  {"front": "Another concept", "back": "Another explanation"}
]

Return ONLY the JSON array. No markdown, no code blocks, no explanations.`;
        
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                history: [{ role: 'user', content: prompt }],
                subject: subject
            })
        });
        
        const data = await res.json();
        console.log('[Flashcards] Raw response:', data.response.substring(0, 200));
        
        // Extract JSON array from response
        let jsonStr = null;
        const jsonMatch = data.response.match(/\[[\s\S]*\]/);
        
        if (jsonMatch) {
            jsonStr = jsonMatch[0];
        } else {
            // Try to find JSON between code blocks
            const codeBlockMatch = data.response.match(/```(?:json)?\s*(\[[\s\S]*?\])\s*```/);
            if (codeBlockMatch) {
                jsonStr = codeBlockMatch[1];
            }
        }
        
        if (jsonStr) {
            try {
                // More aggressive JSON cleaning - handle LaTeX arrows and symbols
                jsonStr = jsonStr
                    .replace(/\\n/g, ' ')           // Remove newlines
                    .replace(/\\t/g, ' ')           // Remove tabs
                    .replace(/\\r/g, ' ')           // Remove carriage returns
                    .replace(/\\rightarrow/g, '→')  // Replace LaTeX arrow
                    .replace(/\\leftarrow/g, '←')   // Replace LaTeX arrow
                    .replace(/\\Rightarrow/g, '⇒')  // Replace LaTeX arrow
                    .replace(/\\Leftarrow/g, '⇐')   // Replace LaTeX arrow
                    .replace(/\\to/g, '→')          // Replace LaTeX arrow
                    .replace(/\\times/g, '×')       // Replace LaTeX times
                    .replace(/\\div/g, '÷')         // Replace LaTeX div
                    .replace(/\\pm/g, '±')          // Replace LaTeX plus-minus
                    .replace(/\\cdot/g, '·')        // Replace LaTeX dot
                    .replace(/\\−/g, '-')           // Replace special minus
                    .replace(/\\\\/g, '\\')         // Fix double backslashes
                    .replace(/\\"/g, '"')           // Fix escaped quotes inside strings
                    .replace(/\\'/g, "'")           // Fix escaped single quotes
                    .replace(/[\u0000-\u001F\u007F-\u009F]/g, ' '); // Remove control characters
                
                console.log('[Flashcards] Cleaned JSON:', jsonStr.substring(0, 200));
                
                const facts = JSON.parse(jsonStr);
                
                // Validate and create flashcards
                if (Array.isArray(facts) && facts.length > 0) {
                    currentFlashcardSet = facts
                        .filter(f => f && (f.front || f.concept || f.term) && (f.back || f.explanation || f.definition))
                        .map((f, idx) => {
                            const front = (f.front || f.concept || f.term || '').trim();
                            const back = (f.back || f.explanation || f.definition || '').trim();
                            
                            // Skip if either is empty or contains malformed JSON
                            if (!front || !back || front.includes('{"') || back.includes('{"')) {
                                return null;
                            }
                            
                            return {
                                id: idx,
                                front: front.substring(0, 500),
                                back: back.substring(0, 1000),
                                type: 'fact'
                            };
                        })
                        .filter(card => card !== null);
                    
                    if (currentFlashcardSet.length === 0) {
                        throw new Error('No valid flashcards after filtering');
                    }
                    
                    console.log('[Flashcards] Created', currentFlashcardSet.length, 'valid flashcards');
                } else {
                    throw new Error('Invalid facts array');
                }
            } catch (parseError) {
                console.error('[Flashcards] JSON parse error:', parseError);
                console.error('[Flashcards] Failed JSON string:', jsonStr);
                
                // Fallback: Extract clean text and split into educational points
                const cleanText = data.response
                    .replace(/\[[\s\S]*\]/, '')        // Remove failed JSON
                    .replace(/```[\s\S]*?```/g, '')    // Remove code blocks
                    .replace(/[{}\[\]]/g, '')          // Remove stray brackets
                    .trim();
                
                const sentences = cleanText
                    .split(/(?<=[.!?])\s+/)            // Split on sentence boundaries
                    .map(s => s.trim())
                    .filter(s => s.length > 30 && s.length < 500 && !s.includes('{"') && !s.includes('}')); // Filter valid sentences
                
                if (sentences.length >= 3) {
                    currentFlashcardSet = sentences.slice(0, 10).map((sentence, idx) => ({
                        id: idx,
                        front: `${topic} - Concept ${idx + 1}`,
                        back: sentence,
                        type: 'fact'
                    }));
                    console.log('[Flashcards] Fallback: Created', currentFlashcardSet.length, 'cards from text');
                } else {
                    throw new Error('Unable to generate flashcards - insufficient content');
                }
            }
        } else {
            // No JSON found - treat entire response as learning content
            const cleanText = data.response
                .replace(/[{}\[\]]/g, '')
                .trim();
            
            const sentences = cleanText
                .split(/(?<=[.!?])\s+/)
                .map(s => s.trim())
                .filter(s => s.length > 30 && s.length < 500);
            
            if (sentences.length >= 3) {
                currentFlashcardSet = sentences.slice(0, 10).map((sentence, idx) => ({
                    id: idx,
                    front: `${topic} - Key Point ${idx + 1}`,
                    back: sentence,
                    type: 'fact'
                }));
                console.log('[Flashcards] No JSON: Created', currentFlashcardSet.length, 'cards from text');
            } else {
                throw new Error('Unable to generate flashcards - insufficient content');
            }
        }
        
        currentFlashcardIndex = 0;
        flashcardStats = { known: 0, learning: 0, total: currentFlashcardSet.length };
        showFlashcardViewer();
        
    } catch (error) {
        console.error('[Flashcards] Fact flashcard generation failed:', error);
        
        // Fallback: Create generic educational cards about the topic
        const genericFacts = [
            { front: `What is ${topic}?`, back: `${topic} is an important concept in ${subject}. It involves key principles and applications that are essential for WAEC examination preparation.` },
            { front: `Why study ${topic}?`, back: `Understanding ${topic} helps build a strong foundation in ${subject} and is frequently tested in WAEC exams.` },
            { front: `Key aspect of ${topic}`, back: `${topic} requires careful study of definitions, principles, and practical applications.` },
            { front: `${topic} in exams`, back: `WAEC questions on ${topic} typically test your understanding of core concepts and their real-world applications.` },
            { front: `Study tip for ${topic}`, back: `Focus on understanding the fundamental principles of ${topic} rather than just memorization. Practice with past questions.` }
        ];
        
        currentFlashcardSet = genericFacts.map((f, idx) => ({
            id: idx,
            front: f.front,
            back: f.back,
            type: 'fact'
        }));
        
        currentFlashcardIndex = 0;
        flashcardStats = { known: 0, learning: 0, total: currentFlashcardSet.length };
        showFlashcardViewer();
        
        showToast('Using general study tips (AI temporarily unavailable)', 'warning');
    }
}

function showFlashcardViewer() {
    const modal = document.createElement('div');
    modal.id = 'flashcard-viewer-modal';
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4';
    
    modal.innerHTML = `
        <div class="bg-dark-card rounded-3xl p-4 md:p-8 max-w-2xl w-full mx-auto shadow-2xl border border-dark-border">
            <!-- Header -->
            <div class="flex justify-between items-center mb-4">
                <div class="flex items-center gap-4">
                    <span class="text-sm text-gray-400">${currentFlashcardIndex + 1} / ${currentFlashcardSet.length}</span>
                    <div class="flex gap-2 text-xs">
                        <span class="text-green-400">✓ ${flashcardStats.known}</span>
                        <span class="text-yellow-400">⏳ ${flashcardStats.learning}</span>
                    </div>
                </div>
                <button onclick="closeFlashcardViewer()" class="text-gray-400 hover:text-white">✕</button>
            </div>
            
            <!-- Progress Bar -->
            <div class="w-full bg-gray-700 rounded-full h-2 mb-6">
                <div class="bg-brand-500 h-2 rounded-full transition-all" style="width: ${(currentFlashcardIndex / currentFlashcardSet.length) * 100}%"></div>
            </div>
            
            <!-- Flashcard -->
            <div id="flashcard-container" class="mb-6 touch-pan-y">
                ${renderFlashcard()}
            </div>
            
            <!-- Navigation -->
            <div class="flex gap-2 md:gap-3 flex-wrap">
                <button onclick="markFlashcard('known')" class="flex-1 min-w-[100px] px-3 py-2 md:px-4 md:py-3 bg-green-600 hover:bg-green-500 rounded-xl font-semibold transition text-sm md:text-base">
                    ✓ Know
                </button>
                <button onclick="markFlashcard('learning')" class="flex-1 min-w-[100px] px-3 py-2 md:px-4 md:py-3 bg-yellow-600 hover:bg-yellow-500 rounded-xl font-semibold transition text-sm md:text-base">
                    ⏳ Learning
                </button>
                <button onclick="nextFlashcard()" class="flex-1 min-w-[100px] px-3 py-2 md:px-4 md:py-3 bg-brand-500 hover:bg-brand-600 rounded-xl font-semibold transition text-sm md:text-base">
                    Next →
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add swipe gesture support
    initSwipeGestures();
    
    // Render LaTeX after modal is added to DOM
    setTimeout(() => {
        renderFlashcardMath();
    }, 50);
}

function renderFlashcard() {
    const card = currentFlashcardSet[currentFlashcardIndex];
    if (!card) return '';
    
    // Format options for quiz cards
    let optionsHTML = '';
    if (card.type === 'quiz' && card.options && card.options.length > 0) {
        optionsHTML = `
            <div class="mt-4 space-y-2 text-left w-full">
                ${card.options.map((opt, idx) => {
                    const letter = String.fromCharCode(97 + idx); // a, b, c, d
                    const isCorrect = card.answer && letter === card.answer.toLowerCase();
                    return `
                        <div class="option-item p-2 rounded-lg bg-dark-surface/50 border border-gray-700">
                            <span class="font-semibold text-brand-400">${letter.toUpperCase()}.</span> ${opt}
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }
    
    return `
        <div class="flashcard-3d relative w-full" style="min-height: 300px; perspective: 1000px;">
            <div id="flashcard-inner" class="relative w-full h-full transition-transform duration-500" style="transform-style: preserve-3d;">
                <!-- Front -->
                <div class="flashcard-face absolute w-full bg-gradient-to-br from-brand-500/10 to-brand-600/5 border-2 border-brand-500/30 rounded-2xl p-4 md:p-6 cursor-pointer overflow-y-auto" style="min-height: 300px; max-height: 500px; backface-visibility: hidden;" onclick="flipFlashcardStandalone()">
                    <div class="flex flex-col items-center justify-start h-full">
                        <div class="text-xs md:text-sm text-brand-400 mb-3">Click to reveal answer</div>
                        <div class="flashcard-text-front text-base md:text-lg font-semibold overflow-y-auto max-h-[150px] w-full px-2 text-center">${card.front}</div>
                        ${optionsHTML}
                    </div>
                </div>
                
                <!-- Back -->
                <div class="flashcard-face absolute w-full bg-gradient-to-br from-purple-500/10 to-purple-600/5 border-2 border-purple-500/30 rounded-2xl p-4 md:p-6 cursor-pointer overflow-y-auto" style="min-height: 300px; max-height: 500px; backface-visibility: hidden; transform: rotateY(180deg);" onclick="flipFlashcardStandalone()">
                    <div class="flex flex-col items-center justify-center h-full text-center">
                        <div class="text-xs md:text-sm text-purple-400 mb-3">Answer</div>
                        <div class="flashcard-text-back text-base md:text-lg font-semibold mb-3 overflow-y-auto max-h-[200px] w-full px-2">${card.back}</div>
                        ${card.explanation ? `<p class="flashcard-text-explanation text-xs md:text-sm text-gray-400 mt-3 overflow-y-auto max-h-[100px] w-full px-2">${card.explanation}</p>` : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
}

let isFlipped = false;
function flipFlashcardStandalone() {
    const inner = document.getElementById('flashcard-inner');
    if (!inner) return;
    
    isFlipped = !isFlipped;
    inner.style.transform = isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)';
}

function markFlashcard(status) {
    if (status === 'known') {
        flashcardStats.known++;
    } else if (status === 'learning') {
        flashcardStats.learning++;
    }
    
    nextFlashcard();
}

function nextFlashcard() {
    if (currentFlashcardIndex < currentFlashcardSet.length - 1) {
        currentFlashcardIndex++;
        isFlipped = false;
        updateFlashcardViewer();
    } else {
        showFlashcardResults();
    }
}

function updateFlashcardViewer() {
    const container = document.getElementById('flashcard-container');
    if (container) {
        container.innerHTML = renderFlashcard();
        // Render LaTeX after content update
        setTimeout(() => {
            renderFlashcardMath();
        }, 50);
    }
    
    // Update progress bar and counter
    const progressBar = document.querySelector('.bg-brand-500');
    if (progressBar) {
        progressBar.style.width = `${(currentFlashcardIndex / currentFlashcardSet.length) * 100}%`;
    }
    
    const counter = document.querySelector('.text-gray-400');
    if (counter) {
        counter.textContent = `${currentFlashcardIndex + 1} / ${currentFlashcardSet.length}`;
    }
}

function showFlashcardResults() {
    closeFlashcardViewer();
    
    const accuracy = Math.round((flashcardStats.known / flashcardStats.total) * 100);
    
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4';
    
    modal.innerHTML = `
        <div class="bg-dark-card rounded-3xl p-6 md:p-8 max-w-md w-full mx-auto shadow-2xl border border-dark-border animate-slide-up">
            <h2 class="font-display text-2xl md:text-3xl font-bold mb-6 text-center">🎉 Session Complete!</h2>
            
            <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="bg-dark-bg rounded-xl p-4 text-center">
                    <div class="text-3xl font-bold text-green-400">${flashcardStats.known}</div>
                    <div class="text-sm text-gray-400 mt-1">Known</div>
                </div>
                <div class="bg-dark-bg rounded-xl p-4 text-center">
                    <div class="text-3xl font-bold text-yellow-400">${flashcardStats.learning}</div>
                    <div class="text-sm text-gray-400 mt-1">Learning</div>
                </div>
            </div>
            
            <div class="text-center mb-6">
                <div class="text-5xl font-bold text-brand-500 mb-2">${accuracy}%</div>
                <div class="text-gray-400">Mastery Level</div>
            </div>
            
            <div class="flex gap-3 flex-col sm:flex-row">
                <button onclick="this.closest('.fixed').remove(); showFlashcardMenu();" class="flex-1 px-6 py-3 bg-brand-500 hover:bg-brand-600 rounded-xl font-semibold transition">
                    New Session
                </button>
                <button onclick="this.closest('.fixed').remove();" class="flex-1 px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-xl font-semibold transition">
                    Close
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    if (typeof confetti !== 'undefined') {
        confetti({ particleCount: 100, spread: 70 });
    }
}

function closeFlashcardViewer() {
    const modal = document.getElementById('flashcard-viewer-modal');
    if (modal) modal.remove();
}

// Swipe gesture support
let touchStartX = 0;
let touchEndX = 0;
let touchStartY = 0;
let touchEndY = 0;

function initSwipeGestures() {
    const container = document.getElementById('flashcard-container');
    if (!container) return;
    
    container.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });
    
    container.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleSwipe();
    }, { passive: true });
}

function handleSwipe() {
    const swipeThreshold = 50;
    const verticalSwipe = Math.abs(touchEndY - touchStartY);
    const horizontalSwipe = touchEndX - touchStartX;
    
    // Only handle horizontal swipes (ignore vertical scrolling)
    if (Math.abs(horizontalSwipe) > swipeThreshold && verticalSwipe < swipeThreshold) {
        if (horizontalSwipe > 0) {
            // Swipe right - previous card
            if (currentFlashcardIndex > 0) {
                currentFlashcardIndex--;
                isFlipped = false;
                updateFlashcardViewer();
            }
        } else {
            // Swipe left - next card
            nextFlashcard();
        }
    }
}

// Render LaTeX/KaTeX in flashcard content
function renderFlashcardMath() {
    if (typeof renderMathInElement === 'undefined') {
        console.warn('[Flashcards] KaTeX auto-render not available');
        return;
    }
    
    const elements = [
        document.querySelector('.flashcard-text-front'),
        document.querySelector('.flashcard-text-back'),
        document.querySelector('.flashcard-text-explanation')
    ];
    
    elements.forEach(el => {
        if (el) {
            try {
                renderMathInElement(el, {
                    delimiters: [
                        {left: '$$', right: '$$', display: true},
                        {left: '$', right: '$', display: false},
                        {left: '\\(', right: '\\)', display: false},
                        {left: '\\[', right: '\\]', display: true}
                    ],
                    throwOnError: false,
                    trust: true
                });
            } catch (e) {
                console.error('[Flashcards] KaTeX render error:', e);
            }
        }
    });
}
