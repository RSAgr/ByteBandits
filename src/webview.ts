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
  <p id="output-text" style="white-space: pre-wrap; color: black; font-family: monospace; margin-top: 20px;">
    Output will be displayed here
  </p>
</div>


  <script src="${scriptUri}"></script>
</body>
</html>

  `;
}
