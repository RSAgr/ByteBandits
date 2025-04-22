import * as vscode from 'vscode';
import { getWebviewContent } from './webview';
import { PythonShell } from 'python-shell';
import * as path from 'path';

// async function deploySmartContract(): Promise<string> {
//     return new Promise((resolve, reject) => {
//         const scriptPath = path.resolve(__dirname, '../deploy.py');

//         const pyshell = new PythonShell(scriptPath, {
//             mode: 'json',
//             pythonOptions: ['-u'],
//         });

//         // You could pass deployment parameters if needed
//         pyshell.send({ action: 'deploy',  });

//         pyshell.on('message', (message) => {
//             if (message.response) {
//                 resolve(message.response);
//             } else if (message.error) {
//                 reject(new Error(message.error));
//             } else {
//                 reject(new Error("Unexpected response from deploy script"));
//             }
//         });

//         pyshell.on('error', (err) => reject(err));
//         pyshell.on('stderr', (stderr) => console.error("Deploy stderr:", stderr));
//         pyshell.end((err) => {
//             if (err) 
//                 {reject(err);
//                 };
//         });
//     });
// }

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
                        const { purpose, type, lang, chat } = message;

                        const prompt = `generate: ${chat} with purpose ${purpose} and type as ${type} in ${lang}`;
                        vscode.window.showInformationMessage(`⏳ Generating ${lang} contract for ${chat} with purpose as ${purpose} (${type})...`);

                        try {
                            const output = await callModel(prompt);
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
                        vscode.window.showInformationMessage(`⏳ Generating ${lang} contract for ${chat} with purpose as ${purpose} (${type})...`);

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
