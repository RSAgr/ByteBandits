const vscode = acquireVsCodeApi();

document.getElementById('generate').addEventListener('click', () => {
    const purpose = document.getElementById('purpose').value;
    const type = document.getElementById('type').value;
    const lang = document.getElementById('lang').value;
    const chat = document.getElementById('chat').value;
    const output = document.getElementById('output-text').value;
    

    document.getElementById('output-text').innerText = "Generating Contract...!";
    

    // Send data to extension backend
    vscode.postMessage({ command: 'generate', purpose, type, lang, chat });


  });
  
  document.getElementById('deploy').addEventListener('click', () => {

    vscode.postMessage({ command: 'deploy', 
      code: document.getElementById('output-text').textContent, 
      contractType: document.getElementById('type').value ,
      lang: document.getElementById('lang').value });
    document.getElementById('output-text').innerText = "Deploying contract...!";
});


  window.addEventListener('message', (event) => {
    const message = event.data;

    if (message.command === 'displayOutput') {
        document.getElementById('output-text').innerText = message.output;
    } else if (message.command === 'error') {
        document.getElementById('output-text').innerText = "❌ Error: " + message.error;
    }
});