const synth = window.speechSynthesis;
let currentUtteranceId = null;

function playVoice(id) {
    // Stop if already speaking
    if (synth.speaking) {
        synth.cancel();
        resetIcons();
        if (currentUtteranceId === id) {
            currentUtteranceId = null;
            return; // Toggle off
        }
    }

    const text = window.voiceData[id];
    if (!text) return console.error("No audio data found for ID:", id);

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    
    // UI Updates
    const btn = document.getElementById(`btn-${id}`);
    if (btn) {
        btn.innerHTML = `<span>⏸️ Stop</span>`;
        btn.classList.add('text-red-400');
    }
    
    currentUtteranceId = id;
    
    utterance.onend = () => {
        resetIcons();
        currentUtteranceId = null;
    };

    synth.speak(utterance);
}

function resetIcons() {
    document.querySelectorAll('[id^="btn-"]').forEach(btn => {
        btn.innerHTML = `<span>🔊 Listen</span>`;
        btn.classList.remove('text-red-400');
    });
}
