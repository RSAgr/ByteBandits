import * as vscode from 'vscode';
import { getWebviewContent } from './webview';
import { PythonShell } from 'python-shell';
import * as path from 'path';

export function callModel(prompt: string): Promise<string> {
    return new Promise((resolve, reject) => {
        //const scriptPath = "D:\Extension\algoDev\codet5Algorand";
        const scriptPath = path.resolve(__dirname, '../inference.py');

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
                        const { purpose, type, lang } = message;

                        const prompt = `generate: ${purpose} ${type} in ${lang}`;
                        vscode.window.showInformationMessage(`⏳ Generating ${lang} contract for ${purpose} (${type})...`);

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
}
