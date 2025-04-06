const vscode = acquireVsCodeApi();

document.getElementById('generate').addEventListener('click', () => {
    const purpose = document.getElementById('purpose').value;
    const type = document.getElementById('type').value;
    const lang = document.getElementById('lang').value;

    document.getElementById('output-text').innerText = "🚀 Hello from the backend!";

    // Send data to extension backend
    vscode.postMessage({ command: 'generate', purpose, type, lang });
  });
  