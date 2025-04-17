import * as vscode from 'vscode';

export function getWebviewContent(webview: vscode.Webview, extensionUri: vscode.Uri): string {
  const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'main.js'));
  const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'style.css'));

  return /* html */ `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <link href="${styleUri}" rel="stylesheet">
      <title>Algorand Contract Builder</title>
    </head>
    <body>
      <h2>Algorand Contract Generator</h2>
      <label for="purpose">Purpose:</label>
      <select id="purpose">
        <option>Escrow</option>
        <option>NFT</option>
        <option>DAO</option>
        <option>Voting</option>
        <option>DeFi</option>
      </select>

      <label for="type">Contract Type:</label>
      <select id="type">
        <option>Stateful</option>
        <option>Stateless</option>
      </select>

      <label for="lang">Language:</label>
      <select id="lang">
        <option>TEAL</option>
        <option>PyTeal</option>
      </select>

      <label for="customPrompt">Custom Description (optional):</label>
      <textarea id="chat" rows="3" cols="50" placeholder="Explain the purpose of the contract"></textarea>
      

      <button id="generate">Generate</button>
      <div id="output" style="margin-top: 20px; padding: 10px; background: #f4f4f4; border-radius: 5px;">
  <p id="output-text" style="white-space: pre-wrap; color: black ; font-family: monospace;">
    Output will be displayed here
  </p>
</div>

      <script src="${scriptUri}"></script>
    </body>
    </html>
  `;
}
