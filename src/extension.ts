import * as vscode from 'vscode';
import { getWebviewContent } from './webview';
import { PythonShell } from 'python-shell';
import * as path from 'path';

async function getDropdownSuggestions(prompt: string): Promise<string[]> {
    return new Promise((resolve, reject) => {
        const scriptPath = path.resolve(__dirname, '../inferenceLora.py');

        const pyshell = new PythonShell(scriptPath, {
            mode: 'json',
            pythonOptions: ['-u'],
        });

        console.log('📩 Fetching dropdown suggestions for:', prompt);
        pyshell.send({ prompt });

        pyshell.on('message', (message) => {
            if (message.suggestions && Array.isArray(message.suggestions)) {
                console.log('🎯 Suggestions:', message.suggestions);
                resolve(message.suggestions);
            } else {
                reject(new Error("Invalid response from Python"));
            }
        });

        pyshell.on('stderr', (stderr) => console.error("Python stderr:", stderr));
        pyshell.on('error', (err) => reject(err));
        pyshell.end((err) => { if (err) {reject(err);}; });
    });
}

async function getInlineCompletion(prompt: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const scriptPath = path.resolve(__dirname, '../inferenceLora.py');

        const pyshell = new PythonShell(scriptPath, {
            mode: 'json',
            pythonOptions: ['-u'],
        });
        console.log('Sending prefix to model:', prompt);
        pyshell.send({ prompt });

        pyshell.on('message', (message) => {
            if (message.response) {
                resolve(message.response);
                console.log('Model response:', message.response);

            } else if (message.error) {
                reject(new Error(message.error));
            } else {
                reject(new Error("Unexpected response from Python"));
            }
        });

        pyshell.on('stderr', (stderr) => console.error("Python stderr:", stderr));
        pyshell.on('error', (err) => reject(err));
        pyshell.end((err) => { if (err) 
            {
                reject(err);
            }
         });
    });
}

export function deploySmartContract(code: string, contractType: string, lang: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const scriptPath = path.resolve(__dirname, '../deploy.py');

        const pyshell = new PythonShell(scriptPath, {
            mode: 'json',
            pythonOptions: ['-u'],
        });

        pyshell.send({
            action: 'deploy',
            code,
            contract_type: contractType,
            lang
        });

        pyshell.on('message', (message) => {
            if (message.response) {
                resolve(message.response);
            } else if (message.error) {
                reject(new Error(message.error));
            } else {
                reject(new Error("Unexpected response from deploy script"));
            }
        });

        pyshell.on('error', (err) => reject(err));
        pyshell.on('stderr', (stderr) => console.error("Deploy stderr:", stderr));
        pyshell.end((err) => {
            if (err) {reject(err);};
        });
    });
}

export function callModel(prompt: string): Promise<string> {
    return new Promise((resolve, reject) => {
        //const scriptPath = "D:\Extension\algoDev\codet5Algorand";
        const scriptPath = path.resolve(__dirname, '../inferenceLora.py');

        const pyshell = new PythonShell(scriptPath, {
            mode: 'json',
            pythonOptions: ['-u'],
        });

        pyshell.send({ prompt });

        pyshell.on('message', (message) => {
            if (message.response) {
                resolve(message.response);
            } else if (message.error) {
                reject(new Error(message.error));
            } else {
                reject(new Error("Unexpected response format from model"));
            }
        });

        pyshell.on('error', (err) => {
            reject(err);
        });

        pyshell.on('stderr', (stderr) => {
            console.error("Python stderr:", stderr);
        });

        pyshell.end((err) => {
            if (err) {reject(err);};
        });
    });
}

export function activate(context: vscode.ExtensionContext) {
    context.subscriptions.push(
        vscode.commands.registerCommand('algorand-dev-assistant.openPanel', () => {
            const panel = vscode.window.createWebviewPanel(
                'algorandDev',
                'Algorand Contract Builder',
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                }
            );

            panel.webview.html = getWebviewContent(panel.webview, context.extensionUri);

            panel.webview.onDidReceiveMessage(
                async (message) => {
                    if (message.command === 'generate') {
                        const { purpose, type, lang, chat } = message;
                        
                        const prompt = `generate: ${chat} with purpose ${purpose} and type as ${type} in ${lang}`;
                
                        vscode.window.showInformationMessage(`⏳ Generating ${lang} contract for ${chat} with purpose as ${purpose} (${type})...`);

                        try {
                            var output = await callModel(prompt);                    
                            panel.webview.postMessage({ command: 'displayOutput', output });
                        } catch (err: any) {
                            panel.webview.postMessage({ command: 'error', error: err.message });
                        }
                    }
                    if (message.command === 'deploy'){
                        try {
                            vscode.window.showInformationMessage("🚀 Deploying smart contract...");
                            
                            // Call a deploySmartContract function (you’ll define this next)
                            const deployResult = await deploySmartContract(message.code, message.contractType, message.lang);
                  
                            panel.webview.postMessage({ command: 'displayOutput', output: deployResult });
                          } catch (err: any) {
                            panel.webview.postMessage({ command: 'error', error: err.message });
                          }
                    }
                    if (message.command === 'retry'){
                        const { purpose, type, lang, chat, output } = message;

                        const prompt = `retry: improve or modify the following contract:\n${output}\n\nOriginal request: ${chat} with purpose ${purpose}, type ${type}, language ${lang}`;
                        vscode.window.showInformationMessage(`⏳ Generating Python contract for ${chat} with purpose as ${purpose} (${type})...`);

                        try {
                            const output = await callModel(prompt);
                            panel.webview.postMessage({ command: 'displayOutput', output });
                        } catch (err: any) {
                            panel.webview.postMessage({ command: 'error', error: err.message });
                        }
                    }
                },
                undefined,
                context.subscriptions
            );
        })
    );
    const provider: vscode.InlineCompletionItemProvider = {
        async provideInlineCompletionItems(document, position, context, token) {
            const linePrefix = document.lineAt(position).text.slice(0, position.character);
            if (!linePrefix.trim()) {return;};

            try {
                const suggestion = await getInlineCompletion(linePrefix);
                return {
                    items: [
                        {
                            insertText: suggestion,
                            range: new vscode.Range(position, position),
                        },
                    ],
                };
            } catch (err: any) {
                console.error("Completion error:", err.message);
            }
        }
    };

    context.subscriptions.push(
        vscode.languages.registerInlineCompletionItemProvider({ pattern: '**' }, provider)
    );
    const dropdownProvider = vscode.languages.registerCompletionItemProvider(
        { language: 'python', scheme: 'file' }, // or 'javascript', etc.
        {
            async provideCompletionItems(document, position) {
                const textBefore = document.getText(new vscode.Range(new vscode.Position(0, 0), position));
    
                try {
                    const suggestions = await getDropdownSuggestions(textBefore);
    
                    return suggestions.map((sugg, index) => {
                        const item = new vscode.CompletionItem(sugg, vscode.CompletionItemKind.Snippet);
                        item.sortText = String(index); // Maintain order
                        return item;
                    });
                } catch (err: any) {
                    vscode.window.showErrorMessage('Dropdown Completion Error: ' + err.message);
                    return [];
                }
            }
        },
        '.' // Trigger dropdown after dot
    );
    
    context.subscriptions.push(dropdownProvider);
    
}
