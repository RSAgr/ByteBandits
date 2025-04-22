const vscode = acquireVsCodeApi();

// Disable Retry button initially
document.getElementById('retry').disabled = true;

document.getElementById('copy-output').addEventListener('click', () => {
    const outputText = document.getElementById('output-text').innerText;
  
    navigator.clipboard.writeText(outputText)
      .then(() => {
        document.getElementById('copy-output').innerText = "Copied!";
        setTimeout(() => {
          document.getElementById('copy-output').innerText = "📋Copy";
        }, 1500);
      })
      .catch(err => {
        console.error('Failed to copy:', err);
      });
  });
  
document.getElementById('generate').addEventListener('click', () => {
    const purpose = document.getElementById('purpose').value;
    const type = document.getElementById('type').value;
    const lang = document.getElementById('lang').value;
    const chat = document.getElementById('chat').value;

    document.getElementById('output-text').innerText = "Generating Contract...!";

    // Send data to extension backend
    vscode.postMessage({ command: 'generate', purpose, type, lang, chat });

    // Enable Retry button after first generate
    document.getElementById('retry').disabled = false;
});

document.getElementById('deploy').addEventListener('click', () => {
    vscode.postMessage({
        command: 'deploy',
        code: document.getElementById('output-text').textContent,
        contractType: document.getElementById('type').value,
        lang: document.getElementById('lang').value
    });
    document.getElementById('output-text').innerText = "Deploying contract...!";
});

document.getElementById('retry').addEventListener('click', () => {
    // Block retry if still disabled
    if (document.getElementById('retry').disabled) return;

    const purpose = document.getElementById('purpose').value;
    const type = document.getElementById('type').value;
    const lang = document.getElementById('lang').value;
    const chat = document.getElementById('chat').value;
    const output = document.getElementById('output-text').value;

    document.getElementById('output-text').innerText = "Retrying Contract...!";

    vscode.postMessage({ command: 'retry', purpose, type, lang, chat, output });
});

window.addEventListener('message', (event) => {
    const message = event.data;

    if (message.command === 'displayOutput') {
        document.getElementById('output-text').innerText = message.output;
    } else if (message.command === 'error') {
        document.getElementById('output-text').innerText = "❌ Error: " + message.error;
    }
});
