import * as vscode from 'vscode';
import { getWebviewContent } from './webview';
import { PythonShell } from 'python-shell';
import * as path from 'path';
import * as fs from 'fs';

function getPythonPath(): string {
    const venvPath = path.join(__dirname, '..', '.venv', 'bin', 'python');
    return fs.existsSync(venvPath) ? venvPath : 'python'; //change to python3 if needed
}

async function getDropdownSuggestions(prompt: string): Promise<string[]> {
    return new Promise((resolve) => {
        const scriptPath = path.resolve(__dirname, '../inferenceDropDown.py');
        const pyshell = new PythonShell(scriptPath, {
            mode: 'json',
            pythonPath: getPythonPath(),
            pythonOptions: ['-u'],
        });

        console.log(`[Python] Using interpreter: ${getPythonPath()}`);
        console.log('📩 [Dropdown] Fetching dropdown suggestions for:', prompt);

        pyshell.send({ prompt });

        pyshell.on('message', (message) => {
            if (message.suggestions && Array.isArray(message.suggestions)) {
                console.log('🎯 [Dropdown] Suggestions:', message.suggestions);
                resolve(message.suggestions);
            } else {
                console.error('[Dropdown] Invalid response from Python:', message);
                resolve(['No suggestions available']);
            }
        });

        pyshell.on('stderr', (stderr) => console.error('[Dropdown] Python stderr:', stderr));
        pyshell.on('error', (err) => {
            console.error('[Dropdown] Python error:', err);
            resolve(['No suggestions available']);
        });

        pyshell.end((err) => {
            if (err) {console.error('[Dropdown] End error:', err);}
        });
    });
}

async function getInlineCompletion(prompt: string): Promise<string> {
    return new Promise((resolve) => {
        const scriptPath = path.resolve(__dirname, '../inferenceLora.py');
        const pyshell = new PythonShell(scriptPath, {
            mode: 'json',
            pythonPath: getPythonPath(),
            pythonOptions: ['-u'],
        });

        console.log(`[Python] Using interpreter: ${getPythonPath()}`);
        console.log('[Inline] Sending prefix to model:', prompt);

        pyshell.send({ prompt });

        pyshell.on('message', (message) => {
            if (message.response) {
                console.log('[Inline] Model response:', message.response);
                resolve(message.response);
            } else if (message.error) {
                console.error('[Inline] Model error:', message.error);
                resolve('');
            } else {
                console.error('[Inline] Unexpected response from Python:', message);
                resolve('');
            }
        });

        pyshell.on('stderr', (stderr) => console.error('[Inline] Python stderr:', stderr));
        pyshell.on('error', (err) => {
            console.error('[Inline] Python error:', err);
            resolve('');
        });

        pyshell.end((err) => {
            if (err) {console.error('[Inline] End error:', err);}
        });
    });
}

export function deploySmartContract(code: string, contractType: string, lang: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const scriptPath = path.resolve(__dirname, '../deploy.py');
        const pyshell = new PythonShell(scriptPath, {
            mode: 'json',
            pythonPath: getPythonPath(),
            pythonOptions: ['-u'],
        });

        console.log(`[Python] Using interpreter: ${getPythonPath()}`);

        pyshell.send({ action: 'deploy', code, contract_type: contractType, lang });

        pyshell.on('message', (message) => {
            if (message.response) {
                resolve(message.response);
            } else if (message.error) {
                reject(new Error(message.error));
            } else {
                reject(new Error("Unexpected response from deploy script"));
            }
        });

        pyshell.on('stderr', (stderr) => console.error("Deploy stderr:", stderr));
        pyshell.on('error', (err) => reject(err));
        pyshell.end((err) => {
            if (err) {reject(err);}
        });
    });
}

export function callModel(prompt: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const scriptPath = path.resolve(__dirname, '../inferenceLora.py');
        const pyshell = new PythonShell(scriptPath, {
            mode: 'json',
            pythonPath: getPythonPath(),
            pythonOptions: ['-u'],
        });

        console.log(`[Python] Using interpreter: ${getPythonPath()}`);

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

        pyshell.on('stderr', (stderr) => console.error("Python stderr:", stderr));
        pyshell.on('error', (err) => reject(err));
        pyshell.end((err) => {
            if (err) {reject(err);}
        });
    });
}

export function activate(context: vscode.ExtensionContext) {
    console.log("[Extension] Activating Algorand Dev Assistant extension!");

    context.subscriptions.push(
        vscode.commands.registerCommand('algorand-dev-assistant.openPanel', () => {
            const panel = vscode.window.createWebviewPanel(
                'algorandDev',
                'Algorand Contract Builder',
                vscode.ViewColumn.One,
                { enableScripts: true }
            );

            panel.webview.html = getWebviewContent(panel.webview, context.extensionUri);

            panel.webview.onDidReceiveMessage(async (message) => {
                console.log('[Webview] Received message:', message);

                if (message.command === 'generate') {
                    const { purpose, type, lang, chat } = message;
                    const prompt = `instruction: ${chat}\noutput:`;
                    vscode.window.showInformationMessage(`⏳ Generating ${lang} contract for ${chat} with purpose as ${purpose} (${type})...`);
                    try {
                        const code = await callModel(prompt);
                        const formattedOutput = `\`\`\`${message.lang || ''}\n${code}\n\`\`\``;
                        panel.webview.postMessage({ command: 'displayOutput', output: formattedOutput });
                    } catch (err: any) {
                        panel.webview.postMessage({ command: 'error', error: err.message });
                    }
                }

                if (message.command === 'deploy') {
                    try {
                        vscode.window.showInformationMessage('🚀 Deploying smart contract...');
                        const deployResult = await deploySmartContract(message.code, message.contractType, message.lang);
                        panel.webview.postMessage({ command: 'displayOutput', output: deployResult });
                    } catch (err: any) {
                        panel.webview.postMessage({ command: 'error', error: err.message });
                    }
                }

                if (message.command === 'retry') {
                    const { purpose, type, lang, chat, output } = message;
                    const prompt = `instruction: Improve or modify the following Python contract based on the original request.\n\noutput:\n${output}\n\nOriginal instruction: ${chat}`;
                    vscode.window.showInformationMessage(`⏳ Regenerating Python contract for ${chat}...`);
                    try {
                        const code = await callModel(prompt);
                        const formattedOutput = `\`\`\`${message.lang || ''}\n${code}\n\`\`\``;
                        panel.webview.postMessage({ command: 'displayOutput', output: formattedOutput });
                    } catch (err: any) {
                        panel.webview.postMessage({ command: 'error', error: err.message });
                    }
                }
            }, undefined, context.subscriptions);
        })
    );

    const inlineProvider: vscode.InlineCompletionItemProvider = {
        async provideInlineCompletionItems(document, position) {
            const linePrefix = document.lineAt(position).text.slice(0, position.character);
            console.log('[Inline] Triggered for linePrefix:', linePrefix);
            try {
                const suggestion = await getInlineCompletion(linePrefix);
                if (!suggestion) {return;}
                return {
                    items: [
                        {
                            insertText: suggestion,
                            range: new vscode.Range(position, position),
                        },
                    ],
                };
            } catch (err: any) {
                console.error('[Inline] Completion error:', err.message);
            }
        }
    };

    context.subscriptions.push(
        vscode.languages.registerInlineCompletionItemProvider({ language: 'python', scheme: 'file' }, inlineProvider)
    );

    const dropdownProvider = vscode.languages.registerCompletionItemProvider(
        { language: 'python', scheme: 'file' },
        {
            async provideCompletionItems(document, position, token, context) {
                const linePrefix = document.lineAt(position).text.slice(0, position.character);
                console.log('[Dropdown] Triggered with context:', {
                    linePrefix,
                    triggerCharacter: context?.triggerCharacter,
                    position,
                });

                const isDotTrigger = linePrefix.endsWith('.');
                const isWordStart = /\w$/.test(linePrefix);

                if (!isDotTrigger && !isWordStart) {
                    console.log('[Dropdown] Not at a trigger position');
                    return [];
                }

                try {
                    const textBefore = document.getText(new vscode.Range(new vscode.Position(0, 0), position));
                    console.log('[Dropdown] Getting suggestions for textBefore:', textBefore);

                    const suggestions = await getDropdownSuggestions(textBefore);
                    console.log('[Dropdown] Received suggestions:', suggestions);

                    return suggestions.map((sugg, index) => {
                        const item = new vscode.CompletionItem(sugg, vscode.CompletionItemKind.Snippet);
                        item.sortText = String(index).padStart(5, '0');
                        return item;
                    });
                } catch (err: any) {
                    console.error('[Dropdown] Error:', err);
                    vscode.window.showErrorMessage('[Dropdown] Completion Error: ' + err.message);
                    return [];
                }
            }
        },
        '.', ' '
    );

    context.subscriptions.push(dropdownProvider);
}
