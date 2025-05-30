import * as vscode from 'vscode';

export function getWebviewContent(webview: vscode.Webview, extensionUri: vscode.Uri): string {
    const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'style.css'));

    return /* html */ `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="${styleUri}" rel="stylesheet" />
        <title>AlgoGenerator // Core</title>
        <style>
            :root {
                --bg-color: #1e1e1e;
                --card-bg: #252526;
                --border-color: #3e3e42;
                --accent-color: #007acc;
                --accent-color-light: #3794ff;
                --text-color: #d4d4d4;
                --placeholder-color: #858585;
                --error-color: #f48771;
                --loading-color: #007acc;
                --shadow-color: rgba(2, 2, 2, 0.2);
                --success-color: #4ec9b0;
                --highlight-color: #2d2d30;
                --code-bg: #1e1e1e;
                --code-border: #252526;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                min-height: 100vh;
                box-sizing: border-box;
                overflow-x: hidden;
                line-height: 1.6;
            }

            h2 {
                color: var(--accent-color-light);
                text-align: center;
                margin-bottom: 30px;
                font-weight: 500;
                font-size: 2.2em;
                letter-spacing: -0.5px;
                position: relative;
                padding-bottom: 15px;
            }

            h2::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 50%;
                transform: translateX(-50%);
                width: 80px;
                height: 3px;
                background: linear-gradient(90deg, var(--accent-color), var(--accent-color-light));
                border-radius: 3px;
            }

            .container {
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 40px;
                width: 90%;
                max-width: 1200px;
                background: var(--card-bg);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                margin-bottom: 30px;
            }

            .form-section {
                display: flex;
                flex-direction: column;
            }

            label {
                display: block;
                margin-top: 20px;
                margin-bottom: 8px;
                font-weight: 500;
                color: var(--accent-color-light);
                font-size: 0.95em;
            }

            select, textarea {
                width: 100%;
                padding: 12px;
                background-color: var(--card-bg);
                border: 1px solid var(--border-color);
                border-radius: 6px;
                color: var(--text-color);
                font-family: inherit;
                font-size: 1em;
                box-sizing: border-box;
                transition: all 0.3s ease;
            }

            select {
                appearance: none;
                background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23d4d4d4' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
                background-repeat: no-repeat;
                background-position: right 12px center;
                background-size: 16px;
            }

            select:focus, textarea:focus {
                outline: none;
                border-color: var(--accent-color);
                box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.3);
            }

            textarea {
                min-height: 150px;
                resize: vertical;
                line-height: 1.6;
            }

            ::placeholder {
                color: var(--placeholder-color);
                opacity: 1;
            }

            .button-section {
                display: flex;
                flex-direction: column;
                gap: 16px;
                justify-content: center;
                min-width: 200px;
            }

            button {
                padding: 12px 20px;
                font-size: 1em;
                font-weight: 500;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                background-color: var(--accent-color);
                color: white;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            }

            button:hover:not(:disabled) {
                background-color: var(--accent-color-light);
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0, 122, 204, 0.3);
            }

            button:active:not(:disabled) {
                transform: translateY(0);
            }

            button:disabled {
                background-color: #333;
                color: #666;
                cursor: not-allowed;
                box-shadow: none;
            }

            #output {
                width: 90%;
                max-width: 1200px;
                background: var(--card-bg);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 25px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                position: relative;
                margin-bottom: 30px;
            }

            #output-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }

            #output-title {
                font-weight: 500;
                color: var(--accent-color-light);
                font-size: 1.1em;
            }

            #output-text {
                white-space: pre;
                color: var(--text-color);
                background: var(--code-bg);
                padding: 20px;
                border-radius: 6px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 0.95em;
                line-height: 1.5;
                border: 1px solid var(--code-border);
                overflow-x: auto;
                min-height: 50px;
                tab-size: 4;
                margin: 0;
            }

            #error-text {
                color: var(--error-color);
                font-weight: 500;
                margin-top: 15px;
                padding: 12px;
                background-color: rgba(244, 135, 113, 0.1);
                border-radius: 6px;
                display: none;
                font-size: 1em;
            }

            #loading-text {
                color: #3794ff;
                margin-top: 15px;
                display: none;
                align-items: center;
                justify-content: center;
                gap: 20px; /* This adds space between loader and text */
                font-weight: 500;
            }

            .loading-message {
                margin-left: 10px; /* Additional spacing if needed */
                color: #3794ff;
            }

            /* HTML: <div class="loader"></div> */
            .loader {
                width: 40px;
                aspect-ratio: 1;
                color: #3794ff;
                position: relative;
                background: radial-gradient(10px,currentColor 94%,#0000);
            }
            .loader:before {
                content: '';
                position: absolute;
                inset: 0;
                border-radius: 50%;
                background:
                    radial-gradient(9px at bottom right,#0000 94%,currentColor) top    left,
                    radial-gradient(9px at bottom left ,#0000 94%,currentColor) top    right,
                    radial-gradient(9px at top    right,#0000 94%,currentColor) bottom left,
                    radial-gradient(9px at top    left ,#0000 94%,currentColor) bottom right;
                background-size: 20px 20px;
                background-repeat: no-repeat;
                animation: l18 1.5s infinite cubic-bezier(0.3,1,0,1);
            }
            @keyframes l18 {
                33%  {inset:-10px;transform: rotate(0deg)}
                66%  {inset:-10px;transform: rotate(90deg)}
                100% {inset:0    ;transform: rotate(90deg)}
            }

            #copy-output {
                background: var(--border-color);
                color: white;
                border: none;
                padding: 6px 12px;
                font-size: 0.85em;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                gap: 6px;
            }

            #copy-output:hover {
                background: var(--accent-color);
                color: white;
            }

            .status-badge {
                background: var(--success-color);
                color: #1e1e1e;
                padding: 4px 10px;
                font-size: 0.75em;
                border-radius: 12px;
                font-weight: 500;
                display: none;
            }

            /* Syntax highlighting */
            .token.comment,
            .token.prolog,
            .token.doctype,
            .token.cdata {
                color: #6a9955;
            }

            .token.punctuation {
                color: #d4d4d4;
            }

            .token.property,
            .token.tag,
            .token.boolean,
            .token.number,
            .token.constant,
            .token.symbol,
            .token.deleted {
                color: #b5cea8;
            }

            .token.selector,
            .token.attr-name,
            .token.string,
            .token.char,
            .token.builtin,
            .token.inserted {
                color: #ce9178;
            }

            .token.operator,
            .token.entity,
            .token.url,
            .language-css .token.string,
            .style .token.string {
                color: #d4d4d4;
            }

            .token.atrule,
            .token.attr-value,
            .token.keyword {
                color: #569cd6;
            }

            .token.function,
            .token.class-name {
                color: #dcdcaa;
            }

            .token.regex,
            .token.important,
            .token.variable {
                color: #d16969;
            }

            @media (max-width: 900px) {
                .container {
                    grid-template-columns: 1fr;
                    gap: 30px;
                    padding: 25px;
                }
                
                .button-section {
                    flex-direction: row;
                    min-width: auto;
                }
                
                button {
                    flex: 1;
                }
            }

            @media (max-width: 600px) {
                .container {
                    width: 95%;
                    padding: 20px;
                }
                
                .button-section {
                    flex-direction: column;
                }
                
                h2 {
                    font-size: 1.8em;
                }
                
                body {
                    padding: 15px;
                }
                
                #output {
                    padding: 20px;
                }
            }
        </style>
    </head>
    <body>
        
        <div class="container">
            <div class="form-section">
                <label for="purpose">Contract Type</label>
                <select id="purpose">
                    <option value="">Select contract type...</option>
                    <option value="Escrow">Escrow Contract</option>
                    <option value="NFT">NFT Minting</option>
                    <option value="DAO">DAO Governance</option>
                    <option value="Voting">Voting Mechanism</option>
                    <option value="DeFi">DeFi Protocol</option>
                    <option value="Custom">Custom Script</option>
                </select>

                <label for="chat">Contract Description</label>
                <textarea id="chat" rows="6" placeholder="Describe the functionality you need for your Algorand smart contract..."></textarea>
            </div>

            <div class="button-section">
                <button id="generate">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Generate Code
                </button>
                <button id="deploy" disabled>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                        <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                        <line x1="12" y1="22.08" x2="12" y2="12"></line>
                    </svg>
                    Deploy Contract
                </button>
                <button id="retry" disabled>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="23 4 23 10 17 10"></polyline>
                        <polyline points="1 20 1 14 7 14"></polyline>
                        <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                    </svg>
                    Retry
                </button>
            </div>
        </div>

        <div id="output">
            <div id="output-header">
                <div id="output-title">Generated Code</div>
                <button id="copy-output">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                    Copy
                </button>
            </div>
            <pre id="output-text"></pre>
            <div id="error-text"></div>
            <div id="loading-text">
                <span class="loader"></span>
                <span class="loading-message">Processing request...</span>
            </div>        
        </div>

        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script>
            const vscode = acquireVsCodeApi();
            const outputText = document.getElementById('output-text');
            const errorText = document.getElementById('error-text');
            const loadingText = document.getElementById('loading-text');
            const generateBtn = document.getElementById('generate');
            const deployBtn = document.getElementById('deploy');
            const retryBtn = document.getElementById('retry');
            const purposeSelect = document.getElementById('purpose');
            const chatInput = document.getElementById('chat');
            const copyBtn = document.getElementById('copy-output');

            // Set loading state
            function setLoading(isLoading) {
                generateBtn.disabled = isLoading;
                deployBtn.disabled = isLoading;
                retryBtn.disabled = isLoading;
                loadingText.style.display = isLoading ? 'flex' : 'none';
                outputText.style.display = isLoading ? 'none' : 'block';
                if (isLoading) errorText.style.display = 'none';
            }

            // Update button states based on input
            function updateButtonStates() {
                const hasInput = purposeSelect.value && chatInput.value.trim();
                generateBtn.disabled = !hasInput;
                
                const hasOutput = outputText.textContent.trim();
                deployBtn.disabled = !hasOutput;
            }

            // Generate button handler
            generateBtn.addEventListener('click', () => {
                if (!purposeSelect.value) {
                    errorText.style.display = 'block';
                    errorText.textContent = 'Please select a contract type';
                    return;
                }
                
                setLoading(true);
                vscode.postMessage({
                    command: 'generate',
                    purpose: purposeSelect.value,
                    chat: chatInput.value,
                    type: 'Stateful',
                    lang: 'Python'
                });
            });

            // Deploy button handler
            deployBtn.addEventListener('click', () => {
                setLoading(true);
                vscode.postMessage({
                    command: 'deploy',
                    code: outputText.textContent,
                    contractType: 'Stateful',
                    lang: 'Python'
                });
            });

            // Retry button handler
            retryBtn.addEventListener('click', () => {
                setLoading(true);
                vscode.postMessage({
                    command: 'retry',
                    purpose: purposeSelect.value,
                    chat: chatInput.value,
                    type: 'Stateful',
                    lang: 'Python',
                    output: outputText.textContent
                });
            });

            // Handle messages from extension
            window.addEventListener('message', event => {
                const message = event.data;
                setLoading(false);

                if (message.command === 'displayOutput') {
                    outputText.style.display = 'block';
                    outputText.innerHTML = message.output;
                    errorText.style.display = 'none';
                    deployBtn.disabled = false;
                    retryBtn.disabled = false;
                } 
                else if (message.command === 'error') {
                    outputText.style.display = 'block';
                    errorText.style.display = 'block';
                    errorText.textContent = message.error;
                    deployBtn.disabled = true;
                }
                
                updateButtonStates();
            });

            // Copy button functionality
            copyBtn.addEventListener('click', () => {
                const textToCopy = outputText.textContent;
                navigator.clipboard.writeText(textToCopy).then(() => {
                    copyBtn.innerHTML = 
                        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
                            '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>' +
                            '<polyline points="22 4 12 14.01 9 11.01"></polyline>' +
                        '</svg>' +
                        'Copied!';
                        
                    setTimeout(() => {
                        copyBtn.innerHTML = 
                            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
                                '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>' +
                                '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>' +
                            '</svg>' +
                            'Copy';
                    }, 2000);
                });
            });

            // Update buttons when inputs change
            purposeSelect.addEventListener('change', updateButtonStates);
            chatInput.addEventListener('input', updateButtonStates);

            // Initialize
            updateButtonStates();
        </script>
    </body>
    </html>
    `;
}