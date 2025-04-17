const vscode = acquireVsCodeApi();

document.getElementById('generate').addEventListener('click', () => {
    const purpose = document.getElementById('purpose').value;
    const type = document.getElementById('type').value;
    const lang = document.getElementById('lang').value;
    

    document.getElementById('output-text').innerText = "🚀 Hello from the backends!";
    

    // Send data to extension backend
    vscode.postMessage({ command: 'generate', purpose, type, lang });


  });
  

  window.addEventListener('message', (event) => {
    const message = event.data;

    if (message.command === 'displayOutput') {
        document.getElementById('output-text').innerText = message.output;
    } else if (message.command === 'error') {
        document.getElementById('output-text').innerText = "❌ Error: " + message.error;
    }
});