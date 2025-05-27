import * as vscode from 'vscode';

export function getWebviewContent(webview: vscode.Webview, extensionUri: vscode.Uri): string {
  const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'main.js'));
  const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'style.css'));

  return /* html */ `
    <!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link href="${styleUri}" rel="stylesheet" />
  <title>Algorand Builder</title>
  <style>
    body {
      font-family: sans-serif;
      margin: 20px;
    }

    .container {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 30px;
    }

    .form-section {
      flex: 1;
      max-width: 600px;
    }

    label {
      display: block;
      margin-top: 10px;
      font-weight: bold;
    }

    select, textarea {
      width: 100%;
      padding: 6px;
      margin-top: 4px;
      margin-bottom: 12px;
      border-radius: 4px;
      border: 1px solid #ccc;
    }

    .button-section {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    button {
      padding: 10px 15px;
      font-size: 14px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      background-color: #007acc;
      color: white;
      transition: background 0.2s ease;
    }

    button:hover {
      background-color: #005fa3;
    }

    button:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
    }

    #output {
      margin-top: 30px;
      padding: 15px;
      background: #f4f4f4;
      border-radius: 6px;
    }

    #output-text {
      white-space: pre-wrap;
      color: black;
      font-family: monospace;
      background: #eaeaea;
      padding: 10px;
      border-radius: 4px;
      font-size: 14px;
    }

    #error-text {
      color: red;
      font-weight: bold;
      margin-top: 10px;
    }

    #loading-text {
      color: #007acc;
      font-style: italic;
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <h2>AlgoGenerator for Degens</h2>
  <div class="container">
    <div class="form-section">
      <label for="purpose">Purpose:</label>
      <select id="purpose">
        <option>-Select-</option>
        <option>Escrow</option>
        <option>NFT</option>
        <option>DAO</option>
        <option>Voting</option>
        <option>DeFi</option>
      </select>

      <label for="customPrompt">Description:</label>
      <textarea id="chat" rows="4" placeholder="Explain the purpose of the contract"></textarea>
    </div>

    <div class="button-section">
      <button id="generate">Generate</button>
      <button id="deploy">Deploy</button>
      <button id="retry" disabled>Retry</button>
    </div>
  </div>

  <div id="output" style="position: relative; margin-top: 20px; padding: 10px; background: #f4f4f4; border-radius: 5px;">
    <button 
      id="copy-output" 
      style="position: absolute; top: 5px; right: 5px; font-size: 10px; padding: 3px 6px; cursor: pointer;">
      📋Copy
    </button>
    <pre id="output-text" style="white-space: pre-wrap; color: black; font-family: monospace; margin-top: 20px;">
      Output will be displayed here
    </pre>
    <div id="error-text" style="display:none;"></div>
    <div id="loading-text" style="display:none;">Loading...</div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script>
    const vscode = acquireVsCodeApi();
    const outputText = document.getElementById('output-text');
    const errorText = document.getElementById('error-text');
    const loadingText = document.getElementById('loading-text');
    
    // Configure marked to use highlight.js for syntax highlighting
    marked.setOptions({
      highlight: function(code, lang) {
        const language = lang || 'plaintext';
        return code; // Return as plain text for now
      },
      langPrefix: 'language-', // Use language-* class for syntax highlighting
      breaks: true,
      gfm: true
    });
    document.getElementById('generate').onclick = function() {
      errorText.style.display = 'none';
      loadingText.style.display = 'block';
      outputText.textContent = '';
      vscode.postMessage({
        command: 'generate',
        purpose: document.getElementById('purpose').value,
        chat: document.getElementById('chat').value,
        type: 'Stateful',
        lang: 'Python'
      });
    };
    document.getElementById('deploy').onclick = function() {
      errorText.style.display = 'none';
      loadingText.style.display = 'block';
      outputText.textContent = '';
      vscode.postMessage({
        command: 'deploy',
        code: outputText.textContent,
        contractType: 'Stateful',
        lang: 'Python'
      });
    };
    document.getElementById('retry').onclick = function() {
      errorText.style.display = 'none';
      loadingText.style.display = 'block';
      outputText.textContent = '';
      vscode.postMessage({
        command: 'retry',
        purpose: document.getElementById('purpose').value,
        chat: document.getElementById('chat').value,
        type: 'Stateful',
        lang: 'Python',
        output: outputText.textContent
      });
    };
    window.addEventListener('message', event => {
      const message = event.data;
      loadingText.style.display = 'none';
      if (message.command === 'displayOutput') {
        errorText.style.display = 'none';
        // Render markdown and set as HTML
        outputText.innerHTML = marked.parse(message.output);
        document.getElementById('retry').disabled = false;
      } else if (message.command === 'error') {
        errorText.style.display = 'block';
        errorText.textContent = message.error;
        outputText.textContent = '';
        document.getElementById('retry').disabled = true;
      }
    });
    document.getElementById('copy-output').onclick = function() {
      navigator.clipboard.writeText(outputText.textContent);
    };
  </script>
</body>
</html>

  `;
}
