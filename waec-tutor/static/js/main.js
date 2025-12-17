let chatHistory = [];
window.voiceData = {};

// Context tracking for subject and topic
let conversationContext = {
    subject: null,
    topic: null,
    lastUpdated: null
};

// Socratic mode toggle
let socraticMode = false;

function toggleSocraticMode() {
    socraticMode = !socraticMode;
    const btn = document.getElementById('socratic-toggle');
    const icon = btn.querySelector('.mode-icon');
    const text = btn.querySelector('.mode-text');
    
    if (socraticMode) {
        btn.classList.add('active');
        icon.textContent = '🧠';
        text.textContent = 'Study Partner';
        showToast('Study Partner Mode: I\'ll guide you to discover answers! 🧠', 'success', 4000);
    } else {
        btn.classList.remove('active');
        icon.textContent = '📚';
        text.textContent = 'Homework Helper';
        showToast('Homework Helper Mode: I\'ll explain concepts directly 📚', 'info', 3000);
    }
    
    console.log('[Socratic] Mode toggled:', socraticMode ? 'ON' : 'OFF');
}

function updateConversationContext(subject, topic) {
    if (subject && subject.toLowerCase() !== 'general') {
        conversationContext.subject = subject;
        conversationContext.lastUpdated = Date.now();
    }
    if (topic && topic.toLowerCase() !== 'general') {
        conversationContext.topic = topic;
        conversationContext.lastUpdated = Date.now();
    }
    updateContextDisplay();
    console.log('Context updated:', conversationContext);
}

function updateContextDisplay() {
    const indicator = document.getElementById('context-indicator');
    const display = document.getElementById('context-display');
    
    if (conversationContext.subject || conversationContext.topic) {
        let text = '';
        if (conversationContext.topic) {
            text = conversationContext.topic;
            if (conversationContext.subject) {
                text += ` (${conversationContext.subject})`;
            }
        } else if (conversationContext.subject) {
            text = conversationContext.subject;
        }
        
        display.textContent = text;
        indicator.classList.remove('hidden');
    } else {
        indicator.classList.add('hidden');
    }
}

function clearContext() {
    conversationContext = {
        subject: null,
        topic: null,
        lastUpdated: null
    };
    updateContextDisplay();
    showToast('Context cleared', 'info');
}

function extractContextFromMessage(message) {
    console.log('[extractContextFromMessage] Analyzing:', message.substring(0, 100));
    const lowerMsg = message.toLowerCase();
    
    // Subject patterns with more variations
    const subjects = [
        { pattern: /(mathematics|math|maths|algebra|geometry|calculus|arithmetic)/i, name: 'Mathematics' },
        { pattern: /(english|grammar|comprehension|literature|writing|composition)/i, name: 'English Language' },
        { pattern: /(physics|mechanics|electricity|waves|thermodynamics)/i, name: 'Physics' },
        { pattern: /(chemistry|organic|inorganic|chemical|reactions)/i, name: 'Chemistry' },
        { pattern: /(biology|botany|zoology|genetics|ecology)/i, name: 'Biology' },
        { pattern: /(economics|microeconomics|macroeconomics|trade)/i, name: 'Economics' },
        { pattern: /(geography|map work|climate|landforms)/i, name: 'Geography' },
        { pattern: /(government|civics|politics|democracy)/i, name: 'Government' }
    ];
    
    // Topic patterns - CHECK TOPICS FIRST (more specific)
    const topics = [
        // English/Grammar topics
        { pattern: /\b(adjectives?)\b/i, name: 'adjectives', subject: 'English Language' },
        { pattern: /\b(adverbs?)\b/i, name: 'adverbs', subject: 'English Language' },
        { pattern: /\b(nouns?)\b/i, name: 'nouns', subject: 'English Language' },
        { pattern: /\b(verbs?)\b/i, name: 'verbs', subject: 'English Language' },
        { pattern: /\b(pronouns?)\b/i, name: 'pronouns', subject: 'English Language' },
        { pattern: /\b(prepositions?)\b/i, name: 'prepositions', subject: 'English Language' },
        { pattern: /\b(conjunctions?)\b/i, name: 'conjunctions', subject: 'English Language' },
        { pattern: /\b(tenses?|past tense|present tense|future tense)\b/i, name: 'tenses', subject: 'English Language' },
        { pattern: /\b(synonyms?|antonyms?)\b/i, name: 'lexis', subject: 'English Language' },
        { pattern: /\b(clauses?|phrases?)\b/i, name: 'clauses', subject: 'English Language' },
        { pattern: /\b(punctuation|commas?|apostrophes?)\b/i, name: 'punctuation', subject: 'English Language' },
        
        // Math topics
        { pattern: /\b(quadratic\s+equations?|quadratics?)\b/i, name: 'quadratic equations', subject: 'Mathematics' },
        { pattern: /\b(linear\s+equations?)\b/i, name: 'linear equations', subject: 'Mathematics' },
        { pattern: /\b(simultaneous\s+equations?)\b/i, name: 'simultaneous equations', subject: 'Mathematics' },
        { pattern: /\b(algebra|algebraic)\b/i, name: 'algebra', subject: 'Mathematics' },
        { pattern: /\b(geometry|geometric|triangles?|circles?)\b/i, name: 'geometry', subject: 'Mathematics' },
        { pattern: /\b(trigonometry|sine|cosine|tangent)\b/i, name: 'trigonometry', subject: 'Mathematics' },
        { pattern: /\b(calculus|derivatives?|integrals?)\b/i, name: 'calculus', subject: 'Mathematics' },
        { pattern: /\b(statistics|probability|data)\b/i, name: 'statistics', subject: 'Mathematics' },
        { pattern: /\b(equations?)\b/i, name: 'equations', subject: 'Mathematics' },
        { pattern: /\b(fractions?|decimals?|percentages?)\b/i, name: 'fractions', subject: 'Mathematics' },
        
        // Physics topics - MORE SPECIFIC FIRST
        { pattern: /\b(specific\s+heat\s+capacity|heat\s+capacity)\b/i, name: 'specific heat capacity', subject: 'Physics' },
        { pattern: /\b(latent\s+heat)\b/i, name: 'latent heat', subject: 'Physics' },
        { pattern: /\b(thermal\s+energy|heat\s+transfer)\b/i, name: 'thermal energy', subject: 'Physics' },
        { pattern: /\b(electricity|electric\s+circuits?|magnetism)\b/i, name: 'electricity', subject: 'Physics' },
        { pattern: /\b(motion|kinematics|forces?|velocity|acceleration)\b/i, name: 'motion', subject: 'Physics' },
        { pattern: /\b(waves?|sound|light)\b/i, name: 'waves', subject: 'Physics' },
        { pattern: /\b(energy|work|power)\b/i, name: 'energy', subject: 'Physics' },
        
        // Chemistry topics - MORE SPECIFIC FIRST
        { pattern: /\b(equilibrium|chemical\s+equilibrium)\b/i, name: 'equilibrium', subject: 'Chemistry' },
        { pattern: /\b(acids?|bases?|salts?|pH)\b/i, name: 'acids and bases', subject: 'Chemistry' },
        { pattern: /\b(oxidation|reduction|redox)\b/i, name: 'redox', subject: 'Chemistry' },
        { pattern: /\b(organic\s+chemistry|hydrocarbons?)\b/i, name: 'organic chemistry', subject: 'Chemistry' },
        { pattern: /\b(ionic|covalent|chemical\s+bonding)\b/i, name: 'chemical bonding', subject: 'Chemistry' },
        
        // Biology topics
        { pattern: /\b(photosynthesis)\b/i, name: 'photosynthesis', subject: 'Biology' },
        { pattern: /\b(respiration|cellular\s+respiration)\b/i, name: 'respiration', subject: 'Biology' },
        { pattern: /\b(cells?|cell\s+structure)\b/i, name: 'cell biology', subject: 'Biology' },
        { pattern: /\b(mitosis|meiosis)\b/i, name: 'cell division', subject: 'Biology' },
        { pattern: /\b(genetics|inheritance|DNA)\b/i, name: 'genetics', subject: 'Biology' }
    ];
    
    // Check for TOPICS FIRST (more specific than subjects)
    let topicFound = false;
    for (const topic of topics) {
        const match = message.match(topic.pattern);
        if (match) {
            conversationContext.topic = topic.name;
            console.log('[extractContextFromMessage] Topic found:', topic.name);
            // If topic has an associated subject, use it
            if (topic.subject) {
                conversationContext.subject = topic.subject;
                console.log('[extractContextFromMessage] Subject set from topic:', topic.subject);
            }
            topicFound = true;
            break;
        }
    }
    
    // Check for subjects only if no specific topic was found
    if (!topicFound) {
        for (const subj of subjects) {
            if (subj.pattern.test(message)) {
                conversationContext.subject = subj.name;
                console.log('[extractContextFromMessage] Subject found:', subj.name);
                break;
            }
        }
    }
    
    conversationContext.lastUpdated = Date.now();
    updateContextDisplay();
    console.log('[extractContextFromMessage] Final context:', conversationContext);
} 

async function sendMessage(messageOverride = null) {
    console.log('[sendMessage] Called with override:', messageOverride);
    const input = document.getElementById('user-input');
    console.log('[sendMessage] Input element:', input);
    const message = messageOverride || input.value.trim();
    console.log('[sendMessage] Message:', message);
    if (!message) {
        console.log('[sendMessage] Empty message, returning');
        return;
    }

    input.style.height = '40px';
    input.value = '';

    console.log('[sendMessage] Adding user bubble');
    addBubble(message, 'user-msg');
    
    // Extract context from user message
    console.log('[sendMessage] Extracting context');
    extractContextFromMessage(message);
    
    // Use typing indicator instead of generic loader
    console.log('[sendMessage] Showing typing indicator');
    const typingIndicator = showTypingIndicator();
    
    chatHistory.push({ role: "user", content: message });
    console.log('[sendMessage] Chat history:', chatHistory);

    try {
        const currentSubject = document.getElementById('subject').value;
        console.log('[sendMessage] Current subject:', currentSubject);
        console.log('[sendMessage] Socratic mode:', socraticMode);
        console.log('[sendMessage] Sending API request to /api/chat');
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                history: chatHistory, 
                subject: currentSubject,
                socratic_mode: socraticMode
            })
        });
        
        console.log('[sendMessage] API response status:', res.status);
        const data = await res.json();
        console.log('[sendMessage] API response data:', data);
        removeTypingIndicator();

        chatHistory.push({ role: "model", content: data.response });
        
        // Update context from AI response
        if (data.action_subject || data.action_topic) {
            console.log('[sendMessage] Updating context from AI response:', {
                subject: data.action_subject,
                topic: data.action_topic
            });
            updateConversationContext(data.action_subject, data.action_topic);
        }
        
        // Also extract context from the AI response content itself
        extractContextFromMessage(data.response);
        
        const msgId = Date.now();
        window.voiceData[msgId] = data.voice_text;
        
        // Only show bubble if there is text (sometimes trigger words leave empty text)
        if(data.response.trim().length > 0) {
            const bubble = addBubble(data.response, 'ai-msg', true, msgId);
            addMessageControls(bubble, data.response, true);
        }

        // --- ACTION TRIGGER ---
        if (data.action === "trigger_quiz") {
            // PRIORITIZE: AI-extracted topic > conversation context > fallback
            // This ensures we use the most recent topic from the AI's understanding
            const quizSubject = data.action_subject || conversationContext.subject || document.getElementById('subject').value;
            const quizTopic = data.action_topic || conversationContext.topic || "General";
            
            console.log('[sendMessage] Quiz triggered with context:', {
                conversationSubject: conversationContext.subject,
                conversationTopic: conversationContext.topic,
                actionSubject: data.action_subject,
                actionTopic: data.action_topic,
                finalSubject: quizSubject,
                finalTopic: quizTopic
            });
            
            // Store for use in difficulty selector
            window.pendingQuizContext = { subject: quizSubject, topic: quizTopic };
            
            showDifficultySelector();
        }        
    } catch (error) {
        console.error('[sendMessage] Error:', error);
        removeTypingIndicator();
        addBubble("Error: " + error.message, 'ai-msg');
        showToast('Failed to send message', 'error');
    }
}

function showTypingIndicator() {
    console.log('[showTypingIndicator] Creating typing indicator');
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
    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
    console.log('[showTypingIndicator] Indicator added');
    return indicator;
}

function removeTypingIndicator() {
    console.log('[removeTypingIndicator] Removing typing indicator');
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
        console.log('[removeTypingIndicator] Indicator removed');
    } else {
        console.warn('[removeTypingIndicator] Indicator not found');
    }
}

function addBubble(text, className, isMarkdown = false, voiceId = null) {
    console.log('[addBubble] Called with:', { text: text.substring(0, 50), className, isMarkdown, voiceId });
    const chatBox = document.getElementById('chat-box');
    console.log('[addBubble] Chat box element:', chatBox);
    if (!chatBox) {
        console.error('[addBubble] Chat box not found!');
        return null;
    }
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${className} prose-chat flex flex-col shadow-sm`;
    const content = document.createElement('div');
    
    if (isMarkdown) {
        // Protect LaTeX expressions from markdown parser
        const latexPlaceholders = [];
        let protectedText = text;
        
        // Protect display math ($$...$$)
        protectedText = protectedText.replace(/\$\$[\s\S]*?\$\$/g, (match) => {
            const placeholder = `###LATEX_DISPLAY_${latexPlaceholders.length}###`;
            latexPlaceholders.push(match);
            return placeholder;
        });
        
        // Protect inline math ($...$)
        protectedText = protectedText.replace(/\$[^\$\n]+?\$/g, (match) => {
            const placeholder = `###LATEX_INLINE_${latexPlaceholders.length}###`;
            latexPlaceholders.push(match);
            return placeholder;
        });
        
        // Parse markdown
        let htmlContent = marked.parse(protectedText);
        
        // Restore LaTeX expressions
        latexPlaceholders.forEach((latex, idx) => {
            htmlContent = htmlContent.replace(`###LATEX_DISPLAY_${idx}###`, latex);
            htmlContent = htmlContent.replace(`###LATEX_INLINE_${idx}###`, latex);
        });
        
        // Ensure double line breaks create paragraph spacing
        htmlContent = htmlContent.replace(/<\/p>\s*<p>/g, '</p><p class="mt-4">');
        
        content.innerHTML = htmlContent;
        content.className = 'markdown-content';
        
        // Render math if available
        if (typeof renderMathInElement !== 'undefined') {
            try {
                renderMathInElement(content, {
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
                console.error('[addBubble] KaTeX rendering error:', e);
            }
        } else {
            console.warn('[addBubble] KaTeX not loaded yet');
        }
    } else {
        content.innerText = text;
    }
    bubble.appendChild(content);

    // Store voiceId on the bubble for later use
    if (voiceId) {
        bubble.dataset.voiceId = voiceId;
    }

    chatBox.appendChild(bubble);
    
    // Smooth scroll animation
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: 'smooth'
    });
    
    return bubble;
}

function addMessageControls(bubble, messageText, canRegenerate = false) {
    console.log('[addMessageControls] Called with bubble:', bubble, 'canRegenerate:', canRegenerate);
    const controls = document.createElement('div');
    controls.className = 'mt-2 pt-2 border-t border-gray-700 flex gap-2 justify-end';
    
    // Voice/Listen button (if voiceId exists)
    const voiceId = bubble.dataset.voiceId;
    console.log('[addMessageControls] VoiceId:', voiceId);
    if (voiceId) {
        const voiceBtn = document.createElement('button');
        voiceBtn.id = `btn-${voiceId}`;
        voiceBtn.className = 'flex items-center gap-1 px-2 py-1 text-xs text-green-400 hover:text-green-300 transition rounded';
        voiceBtn.innerHTML = `<span>🔊 Listen</span>`;
        voiceBtn.onclick = () => playVoice(voiceId);
        controls.appendChild(voiceBtn);
    }
    
    // Copy button
    const copyBtn = document.createElement('button');
    copyBtn.className = 'flex items-center gap-1 px-2 py-1 text-xs text-gray-400 hover:text-brand-500 transition rounded';
    copyBtn.innerHTML = `<span>📋 Copy</span>`;
    copyBtn.onclick = () => {
        navigator.clipboard.writeText(messageText);
        showToast('Copied to clipboard', 'success');
    };
    controls.appendChild(copyBtn);
    
    // Regenerate button (only for AI messages)
    if (canRegenerate) {
        const regenBtn = document.createElement('button');
        regenBtn.className = 'flex items-center gap-1 px-2 py-1 text-xs text-gray-400 hover:text-brand-500 transition rounded';
        regenBtn.innerHTML = `<span>🔄 Regenerate</span>
        `;
        regenBtn.onclick = () => {
            const lastUserMsg = chatHistory[chatHistory.length - 2];
            if (lastUserMsg && lastUserMsg.role === 'user') {
                chatHistory.pop(); // Remove AI response
                sendMessage(lastUserMsg.content);
            }
        };
        controls.appendChild(regenBtn);
    }
    
    bubble.appendChild(controls);
}

function addLoader() {
    const id = 'l-'+Date.now();
    const div = document.createElement('div');
    div.id=id; div.className='chat-bubble ai-msg'; div.innerText='Thinking...';
    document.getElementById('chat-box').appendChild(div);
    return id;
}

// --- QUIZ LOGIC ---
// Updated startQuiz function
async function startQuiz(subject = null, topic = null, difficulty = 'medium', questionCount = 10) {
    console.log('[startQuiz] Called with:', { subject, topic, difficulty, questionCount });
    // Use conversation context if no explicit subject/topic provided
    const subjToUse = subject || conversationContext.subject || document.getElementById('subject').value;
    const topicToUse = topic || conversationContext.topic || "General";
    console.log('[startQuiz] Using subject:', subjToUse, 'topic:', topicToUse);
    
    // Better User Feedback
    const displayTopic = topicToUse === "General" ? subjToUse : topicToUse;
    addBubble(`Generating ${questionCount} ${difficulty} ${displayTopic} questions...`, 'ai-msg');
    
    const typingIndicator = showTypingIndicator();

    try {
        const res = await fetch('/api/quiz', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                subject: subjToUse,
                topic: topicToUse,
                difficulty: difficulty,
                question_count: questionCount
            })
        });
        
        const rawJson = await res.json();
        console.log('[startQuiz] Raw response:', rawJson);
        console.log('[startQuiz] Response type:', typeof rawJson);
        
        let data;
        if (typeof rawJson === 'string') {
             const clean = rawJson.replace(/```json/g, '').replace(/```/g, '').trim();
             console.log('[startQuiz] Cleaned string:', clean.substring(0, 200));
             data = JSON.parse(clean);
        } else {
             data = rawJson;
        }
        
        console.log('[startQuiz] Parsed data:', data);
        console.log('[startQuiz] Sample question:', data.questions?.[0]);
        
        removeTypingIndicator();
        document.querySelector('.chat-bubble.ai-msg:last-child').remove();
        renderQuiz(data);
    } catch (e) {
        console.error(e);
        removeTypingIndicator();
        const lastBubble = document.querySelector('.chat-bubble.ai-msg:last-child');
        if (lastBubble) {
            lastBubble.innerText = "Error loading quiz. Please try again.";
        }
        showToast('Failed to generate quiz', 'error');
    }
}


function renderQuiz(data) {
    const chatBox = document.getElementById('chat-box');
    const container = document.createElement('div');
    container.className = "chat-bubble ai-msg w-full max-w-2xl";
    container.id = 'quiz-container';

    if(!data.questions || data.questions.length === 0) {
         container.innerHTML = "Error: Invalid Quiz Format";
         chatBox.appendChild(container);
         return;
    }

    // Initialize quiz state
    initQuizProgress(data.questions, false);
    
    let html = `
        <div class="flex justify-between items-center mb-4">
            <h3 class="font-bold text-green-400 text-lg">📝 Practice Quiz</h3>
            <div class="flex gap-2">
                <button onclick="showCalculator()" 
                    class="text-xs px-3 py-1 bg-brand-600 hover:bg-brand-500 rounded-full transition">
                    🔢 Calculator
                </button>
                <button onclick="convertQuizToFlashcards(currentQuizState.questions)" 
                    class="text-xs px-3 py-1 bg-purple-600 hover:bg-purple-500 rounded-full transition">
                    🎴 Flashcards
                </button>
                <button onclick="exportQuiz()" 
                    class="text-xs px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded-full transition">
                    📥 Export
                </button>
            </div>
        </div>
        
        <div id="quiz-progress" class="mb-4"></div>
        <div id="quiz-timer" class="hidden text-center mb-4 text-lg font-bold"></div>
    `;
    
    data.questions.forEach((q, idx) => {
        html += `
            <div class="quiz-question mb-4 p-4 bg-black/20 rounded-lg border border-gray-700" data-question-id="${q.id}">
                <p class="font-bold text-sm mb-3 text-gray-200">${idx + 1}. ${q.question}</p>
                <div class="flex flex-col gap-2">
                    ${q.options.map((opt, i) => `
                        <label class="flex items-center gap-3 cursor-pointer hover:bg-white/5 p-3 rounded transition group">
                            <input type="radio" name="q${q.id}" value="${i}" 
                                onchange="handleQuizAnswer(${q.id}, ${i})"
                                class="accent-green-500 w-4 h-4">
                            <span class="text-sm text-gray-300 group-hover:text-white">${opt}</span>
                        </label>
                    `).join('')}
                </div>
                <div id="feedback-${q.id}" class="hidden mt-3 text-xs p-3 rounded bg-gray-800 border border-gray-600"></div>
            </div>
        `;
    });
    
    html += `
        <div class="flex gap-3 mt-6">
            <button onclick="submitQuiz()" 
                class="flex-1 py-3 bg-brand-500 hover:bg-brand-600 rounded-xl font-bold transition transform active:scale-95">
                Submit Quiz
            </button>
        </div>
    `;

    container.innerHTML = html;
    chatBox.appendChild(container);
    
    console.log('[displayQuiz] HTML content before KaTeX:', container.innerHTML.substring(0, 200));
    
    // Render math with a small delay to ensure DOM is ready
    setTimeout(() => {
        if (typeof renderMathInElement !== 'undefined') {
            try {
                console.log('[displayQuiz] Starting KaTeX rendering...');
                renderMathInElement(container, {
                    delimiters: [
                        {left: "$$", right: "$$", display: true},
                        {left: "$", right: "$", display: false},
                        {left: "\\(", right: "\\)", display: false},
                        {left: "\\[", right: "\\]", display: true}
                    ],
                    throwOnError: false,
                    strict: false,
                    trust: true,
                    errorColor: '#cc0000'
                });
                console.log('[displayQuiz] KaTeX rendering complete');
            } catch (e) {
                console.error('[displayQuiz] KaTeX rendering error:', e);
            }
        } else {
            console.error('[displayQuiz] KaTeX not loaded!');
        }
    }, 100);
    
    updateQuizProgress();
    
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: 'smooth'
    });
}

function handleQuizAnswer(questionId, answerIndex) {
    currentQuizState.answers[questionId] = answerIndex;
    updateQuizProgress();
}

function submitQuiz() {
    const questions = currentQuizState.questions;
    
    // Show feedback for all questions
    questions.forEach(q => {
        const userAnswer = currentQuizState.answers[q.id];
        const feedback = document.getElementById(`feedback-${q.id}`);
        const questionDiv = document.querySelector(`[data-question-id="${q.id}"]`);
        
        if (userAnswer === undefined) {
            feedback.classList.remove('hidden');
            feedback.innerHTML = `<span class="text-yellow-400 font-bold">⚠ Not answered</span>`;
            feedback.classList.add('border-yellow-500');
            return;
        }
        
        feedback.classList.remove('hidden');
        if (userAnswer === q.correct_index) {
            feedback.innerHTML = `<span class="text-green-400 font-bold">✓ Correct!</span> ${q.explanation}`;
            feedback.classList.add('border-green-500');
            questionDiv.classList.add('bg-green-900/10');
        } else {
            const correctOption = q.options[q.correct_index];
            feedback.innerHTML = `<span class="text-red-400 font-bold">✗ Incorrect.</span> Correct answer: ${correctOption}. ${q.explanation}`;
            feedback.classList.add('border-red-500');
            questionDiv.classList.add('bg-red-900/10');
        }
    });
    
    // Disable all inputs
    document.querySelectorAll('.quiz-question input').forEach(input => {
        input.disabled = true;
    });
    
    // Hide submit button
    event.target.style.display = 'none';
    
    // Show results
    setTimeout(() => {
        showQuizResults();
    }, 500);
}

function autoSubmitQuiz() {
    showToast('Time\'s up! Auto-submitting quiz...', 'warning');
    setTimeout(submitQuiz, 1000);
}

function exportQuiz() {
    const questions = currentQuizState.questions;
    let text = `WaeGPT Quiz Export\nDate: ${new Date().toLocaleString()}\n${'='.repeat(50)}\n\n`;
    
    questions.forEach((q, idx) => {
        text += `Q${idx + 1}: ${q.question}\n`;
        q.options.forEach((opt, i) => {
            text += `   ${String.fromCharCode(65 + i)}) ${opt}\n`;
        });
        text += `   Correct: ${String.fromCharCode(65 + q.correct_index)}\n`;
        text += `   Explanation: ${q.explanation}\n\n`;
    });
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `waegpt-quiz-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    
    showToast('Quiz exported!', 'success');
}

function restoreChatUI() {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = '';
    
    chatHistory.forEach(msg => {
        if (msg.role === 'user') {
            addBubble(msg.content, 'user-msg');
        } else {
            addBubble(msg.content, 'ai-msg', true);
        }
    });
}

// Microphone functionality
let recognition = null;
let isListening = false;

function toggleMic() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        showToast('Speech recognition not supported in this browser', 'error');
        return;
    }
    
    if (isListening) {
        stopListening();
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    const micBtn = document.getElementById('mic-btn');
    
    recognition.onstart = () => {
        isListening = true;
        micBtn.innerHTML = `
            <svg class="w-5 h-5 text-red-500 animate-pulse" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"></path>
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"></path>
            </svg>
        `;
        showToast('Listening...', 'info');
    };
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('user-input').value = transcript;
        stopListening();
    };
    
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        showToast('Error: ' + event.error, 'error');
        stopListening();
    };
    
    recognition.onend = () => {
        stopListening();
    };
    
    recognition.start();
}

function stopListening() {
    if (recognition) {
        recognition.stop();
        recognition = null;
    }
    isListening = false;
    const micBtn = document.getElementById('mic-btn');
    micBtn.innerHTML = `
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
        </svg>
    `;
}
