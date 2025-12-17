// Scientific Calculator for Quiz
let calculatorState = {
    display: '0',
    previousValue: null,
    operation: null,
    waitingForOperand: false,
    memory: 0,
    isRadians: true // true for radians, false for degrees
};

function showCalculator() {
    // Remove existing calculator if any
    const existing = document.getElementById('calculator-modal');
    if (existing) {
        existing.remove();
        return;
    }

    const modal = document.createElement('div');
    modal.id = 'calculator-modal';
    modal.className = 'fixed bottom-4 right-4 sm:right-4 left-4 sm:left-auto z-50 animate-slide-up';
    
    modal.innerHTML = `
        <div class="bg-dark-card rounded-2xl p-4 shadow-2xl border border-dark-border w-full sm:w-80 max-w-sm mx-auto">
            <!-- Header -->
            <div class="flex justify-between items-center mb-3">
                <span class="text-brand-500 font-bold">🔢 Calculator</span>
                <button onclick="closeCalculator()" class="text-gray-400 hover:text-white">✕</button>
            </div>
            
            <!-- Display -->
            <div id="calc-display" class="bg-dark-bg text-white text-right text-2xl p-4 rounded-xl mb-3 font-mono overflow-x-auto">
                0
            </div>
            
            <!-- Mode Toggle -->
            <div class="flex gap-2 mb-3">
                <button onclick="toggleAngleMode()" id="angle-mode" class="flex-1 px-2 py-1 text-xs bg-brand-500/20 text-brand-500 rounded">
                    RAD
                </button>
                <button onclick="clearMemory()" class="flex-1 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded">
                    MC
                </button>
                <button onclick="recallMemory()" class="flex-1 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded">
                    MR
                </button>
                <button onclick="addToMemory()" class="flex-1 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded">
                    M+
                </button>
            </div>
            
            <!-- Scientific Functions -->
            <div class="grid grid-cols-5 gap-2 mb-2">
                <button onclick="calcFunction('sin')" class="calc-btn-sci">sin</button>
                <button onclick="calcFunction('cos')" class="calc-btn-sci">cos</button>
                <button onclick="calcFunction('tan')" class="calc-btn-sci">tan</button>
                <button onclick="calcFunction('log')" class="calc-btn-sci">log</button>
                <button onclick="calcFunction('ln')" class="calc-btn-sci">ln</button>
            </div>
            
            <div class="grid grid-cols-5 gap-2 mb-2">
                <button onclick="calcFunction('sqrt')" class="calc-btn-sci">√</button>
                <button onclick="calcFunction('pow')" class="calc-btn-sci">x²</button>
                <button onclick="calcFunction('exp')" class="calc-btn-sci">eˣ</button>
                <button onclick="inputConstant('pi')" class="calc-btn-sci">π</button>
                <button onclick="inputConstant('e')" class="calc-btn-sci">e</button>
            </div>
            
            <!-- Number Pad -->
            <div class="grid grid-cols-4 gap-2">
                <button onclick="clearCalc()" class="calc-btn-op bg-red-500/20 text-red-500 hover:bg-red-500/30">C</button>
                <button onclick="deleteDigit()" class="calc-btn-op">⌫</button>
                <button onclick="inputOperation('%')" class="calc-btn-op">%</button>
                <button onclick="inputOperation('/')" class="calc-btn-op">÷</button>
                
                <button onclick="inputDigit('7')" class="calc-btn">7</button>
                <button onclick="inputDigit('8')" class="calc-btn">8</button>
                <button onclick="inputDigit('9')" class="calc-btn">9</button>
                <button onclick="inputOperation('*')" class="calc-btn-op">×</button>
                
                <button onclick="inputDigit('4')" class="calc-btn">4</button>
                <button onclick="inputDigit('5')" class="calc-btn">5</button>
                <button onclick="inputDigit('6')" class="calc-btn">6</button>
                <button onclick="inputOperation('-')" class="calc-btn-op">−</button>
                
                <button onclick="inputDigit('1')" class="calc-btn">1</button>
                <button onclick="inputDigit('2')" class="calc-btn">2</button>
                <button onclick="inputDigit('3')" class="calc-btn">3</button>
                <button onclick="inputOperation('+')" class="calc-btn-op">+</button>
                
                <button onclick="inputDigit('0')" class="calc-btn">0</button>
                <button onclick="inputDigit('.')" class="calc-btn">.</button>
                <button onclick="toggleSign()" class="calc-btn">±</button>
                <button onclick="calculate()" class="calc-btn-equals bg-brand-500 hover:bg-brand-600 text-white">=</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add CSS if not already added
    if (!document.getElementById('calculator-styles')) {
        const style = document.createElement('style');
        style.id = 'calculator-styles';
        style.textContent = `
            .calc-btn, .calc-btn-op, .calc-btn-sci, .calc-btn-equals {
                padding: 12px;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.2s;
                border: none;
                cursor: pointer;
            }
            .calc-btn {
                background: #334155;
                color: white;
            }
            .calc-btn:hover {
                background: #475569;
            }
            .calc-btn-op {
                background: #1e293b;
                color: #22c55e;
            }
            .calc-btn-op:hover {
                background: #334155;
            }
            .calc-btn-sci {
                background: #1e293b;
                color: #60a5fa;
                font-size: 0.75rem;
                padding: 8px;
            }
            .calc-btn-sci:hover {
                background: #334155;
            }
            .calc-btn-equals {
                background: #22c55e;
                color: white;
            }
            .calc-btn-equals:hover {
                background: #16a34a;
            }
        `;
        document.head.appendChild(style);
    }
}

function closeCalculator() {
    const modal = document.getElementById('calculator-modal');
    if (modal) {
        modal.remove();
    }
}

function updateDisplay() {
    const display = document.getElementById('calc-display');
    if (display) {
        display.textContent = calculatorState.display;
    }
}

function inputDigit(digit) {
    const { display, waitingForOperand } = calculatorState;
    
    if (waitingForOperand) {
        calculatorState.display = String(digit);
        calculatorState.waitingForOperand = false;
    } else {
        calculatorState.display = display === '0' ? String(digit) : display + digit;
    }
    
    updateDisplay();
}

function inputOperation(operation) {
    const inputValue = parseFloat(calculatorState.display);
    
    if (calculatorState.previousValue == null) {
        calculatorState.previousValue = inputValue;
    } else if (calculatorState.operation) {
        const result = performOperation(calculatorState.previousValue, inputValue, calculatorState.operation);
        calculatorState.display = String(result);
        calculatorState.previousValue = result;
    }
    
    calculatorState.waitingForOperand = true;
    calculatorState.operation = operation;
    updateDisplay();
}

function calculate() {
    const inputValue = parseFloat(calculatorState.display);
    
    if (calculatorState.previousValue != null && calculatorState.operation) {
        const result = performOperation(calculatorState.previousValue, inputValue, calculatorState.operation);
        calculatorState.display = String(result);
        calculatorState.previousValue = null;
        calculatorState.operation = null;
        calculatorState.waitingForOperand = true;
    }
    
    updateDisplay();
}

function performOperation(prev, current, operation) {
    switch (operation) {
        case '+':
            return prev + current;
        case '-':
            return prev - current;
        case '*':
            return prev * current;
        case '/':
            return current !== 0 ? prev / current : 0;
        case '%':
            return prev % current;
        default:
            return current;
    }
}

function calcFunction(func) {
    const value = parseFloat(calculatorState.display);
    let result;
    
    switch (func) {
        case 'sin':
            result = calculatorState.isRadians ? Math.sin(value) : Math.sin(value * Math.PI / 180);
            break;
        case 'cos':
            result = calculatorState.isRadians ? Math.cos(value) : Math.cos(value * Math.PI / 180);
            break;
        case 'tan':
            result = calculatorState.isRadians ? Math.tan(value) : Math.tan(value * Math.PI / 180);
            break;
        case 'log':
            result = Math.log10(value);
            break;
        case 'ln':
            result = Math.log(value);
            break;
        case 'sqrt':
            result = Math.sqrt(value);
            break;
        case 'pow':
            result = Math.pow(value, 2);
            break;
        case 'exp':
            result = Math.exp(value);
            break;
        default:
            result = value;
    }
    
    calculatorState.display = String(result);
    calculatorState.waitingForOperand = true;
    updateDisplay();
}

function inputConstant(constant) {
    let value;
    switch (constant) {
        case 'pi':
            value = Math.PI;
            break;
        case 'e':
            value = Math.E;
            break;
        default:
            return;
    }
    
    calculatorState.display = String(value);
    calculatorState.waitingForOperand = true;
    updateDisplay();
}

function clearCalc() {
    calculatorState.display = '0';
    calculatorState.previousValue = null;
    calculatorState.operation = null;
    calculatorState.waitingForOperand = false;
    updateDisplay();
}

function deleteDigit() {
    const { display } = calculatorState;
    calculatorState.display = display.length > 1 ? display.slice(0, -1) : '0';
    updateDisplay();
}

function toggleSign() {
    const value = parseFloat(calculatorState.display);
    calculatorState.display = String(-value);
    updateDisplay();
}

function toggleAngleMode() {
    calculatorState.isRadians = !calculatorState.isRadians;
    const btn = document.getElementById('angle-mode');
    if (btn) {
        btn.textContent = calculatorState.isRadians ? 'RAD' : 'DEG';
    }
}

function addToMemory() {
    calculatorState.memory += parseFloat(calculatorState.display);
    showToast('Added to memory', 'success');
}

function recallMemory() {
    calculatorState.display = String(calculatorState.memory);
    calculatorState.waitingForOperand = true;
    updateDisplay();
}

function clearMemory() {
    calculatorState.memory = 0;
    showToast('Memory cleared', 'info');
}
