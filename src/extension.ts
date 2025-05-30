import * as vscode from 'vscode';
import { getWebviewContent } from './webview';
import { PythonShell } from 'python-shell';
import * as path from 'path';
import * as fs from 'fs';

// Set up logging
const logFile = path.join(__dirname, '..', 'extension.log');
const logStream = fs.createWriteStream(logFile, { flags: 'w' });

function logToFile(message: string) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}\n`;
    logStream.write(logMessage);
    console.log(logMessage);
}

// Utility function to get Python path
function getPythonPath(): string {
    // First try the virtual environment
    const venvPath = path.join(__dirname, '..', '.venv', 'bin', 'python');
    if (fs.existsSync(venvPath)) {
        console.log(`[Python] Using virtual environment: ${venvPath}`);
        return venvPath;
    }
    // Fall back to system Python
    console.log('[Python] Using system Python');
    return 'python3';
}

// Utility function to resolve script paths
function getScriptPath(scriptName: string): string {
    try {
        // Log current working directory and __dirname for debugging
        logToFile(`[Path] Current working directory: ${process.cwd()}`);
        logToFile(`[Path] __dirname: ${__dirname}`);
        logToFile(`[Path] Resolving path for script: ${scriptName}`);
        
        // Try multiple possible locations for the script
        const possiblePaths = [
            // Relative to extension root (for development)
            path.join(__dirname, '..', 'src', 'bytebandits', 'core', scriptName),
            // Relative to src directory (for production)
            path.join(__dirname, 'bytebandits', 'core', scriptName),
            // Direct path (for debugging)
            path.resolve(scriptName)
        ];
        
        // Find the first path that exists
        for (const scriptPath of possiblePaths) {
            const resolvedPath = path.resolve(scriptPath);
            logToFile(`[Path] Checking: ${resolvedPath}`);
            
            if (fs.existsSync(resolvedPath)) {
                logToFile(`[Path] Found script at: ${resolvedPath}`);
                return resolvedPath;
            }
        }
        
        // If we get here, no path was found
        const errorMsg = `Python script '${scriptName}' not found in any of these locations:\n${possiblePaths.join('\n')}`;
        logToFile(`[ERROR] ${errorMsg}`);
        
        // Try to list the contents of the expected directories for debugging
        const dirsToCheck = [
            path.join(__dirname, '..', 'src', 'bytebandits', 'core'),
            path.join(__dirname, 'bytebandits', 'core')
        ];
        
        for (const dir of dirsToCheck) {
            try {
                if (fs.existsSync(dir)) {
                    const files = fs.readdirSync(dir);
                    logToFile(`[Path] Files in ${dir}:\n  ${files.join('\n  ')}`);
                } else {
                    logToFile(`[Path] Directory does not exist: ${dir}`);
                }
            } catch (err) {
                logToFile(`[Path] Error reading directory ${dir}: ${err}`);
            }
        }
        
        throw new Error(errorMsg);
    } catch (error) {
        const errorMsg = `Error in getScriptPath: ${error instanceof Error ? error.message : String(error)}`;
        logToFile(`[ERROR] ${errorMsg}`);
        throw new Error(errorMsg);
    }
}

async function getDropdownSuggestions(prompt: string): Promise<string[]> {
    return new Promise((resolve, reject) => {
        try {
            const scriptPath = getScriptPath('inferenceDropDown.py');
            const pythonPath = getPythonPath();
            
            console.log(`[Python] Using interpreter: ${pythonPath}`);
            console.log(`[Python] Script path: ${scriptPath}`);
            
            // Create Python shell with error handling
            // Create PythonShell options with type assertion for maxBuffer
            const pythonShellOptions = {
                mode: 'json' as const,
                pythonPath: pythonPath,
                pythonOptions: ['-u'],
                env: { 
                    ...process.env,
                    PYTHONUNBUFFERED: '1',
                    PYTHONIOENCODING: 'utf-8'
                },
                // @ts-ignore - maxBuffer is not in the type definition but is supported by the underlying child_process
                maxBuffer: 10 * 1024 * 1024 // 10MB buffer
            };
            
            const pyshell = new PythonShell(scriptPath, pythonShellOptions);

            // Set a timeout for the Python script execution
            const timeout = setTimeout(() => {
                console.error('[Dropdown] Python script timeout');
                pyshell.childProcess?.kill();
                resolve(['No suggestions (timeout)']);
            }, 10000); // 10 second timeout

            console.log('📩 [Dropdown] Fetching dropdown suggestions for:', prompt);
            
            // Send the prompt to the Python script
            pyshell.send(JSON.stringify({ prompt }));
            
            let responseReceived = false;
            
            pyshell.on('message', (message) => {
                try {
                    console.log('[Dropdown] Raw Python response:', message);
                    
                    // Handle both string and object responses
                    const response = typeof message === 'string' ? JSON.parse(message) : message;
                    
                    if (response && Array.isArray(response.suggestions)) {
                        console.log('🎯 [Dropdown] Received suggestions:', response.suggestions);
                        responseReceived = true;
                        clearTimeout(timeout);
                        resolve(response.suggestions);
                    } else if (response && response.error) {
                        console.error('[Dropdown] Python script error:', response.error);
                        resolve(['Error: ' + response.error]);
                    } else {
                        console.error('[Dropdown] Invalid response format from Python:', message);
                        resolve(['No suggestions available']);
                    }
                } catch (parseError) {
                    console.error('[Dropdown] Error parsing Python response:', parseError);
                    resolve(['Error parsing response']);
                }
            });

            pyshell.on('stderr', (stderr) => {
                console.error('[Dropdown] Python stderr:', stderr);
            });

            pyshell.on('error', (err) => {
                console.error('[Dropdown] Python shell error:', err);
                if (!responseReceived) {
                    clearTimeout(timeout);
                    resolve(['Error: ' + (err.message || 'Python script error')]);
                }
            });

            pyshell.end((err) => {
                clearTimeout(timeout);
                if (err && !responseReceived) {
                    console.error('[Dropdown] Python script end error:', err);
                    resolve(['Error: ' + (err.message || 'Script execution failed')]);
                } else if (!responseReceived) {
                    console.log('[Dropdown] Python script ended without response');
                    resolve(['No suggestions available']);
                }
            });
            
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            console.error('[Dropdown] Error in getDropdownSuggestions:', errorMessage);
            resolve(['Error: ' + errorMessage]);
        }
    });
}

async function getInlineCompletion(prompt: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const scriptPath = getScriptPath('inferenceLora.py');
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
            if (err) {
                console.error('[Inline] End error:', err);
            }
        });
    });
}

export function deploySmartContract(code: string, contractType: string, lang: string): Promise<string> {
    return new Promise((resolve, reject) => {
        try {
            const scriptPath = path.resolve(__dirname, '../deploy.py');
            const pythonPath = getPythonPath();
            
            logToFile(`[Deploy] Using Python path: ${pythonPath}`);
            logToFile(`[Deploy] Using script path: ${scriptPath}`);
            
            const pyshell = new PythonShell(scriptPath, {
                mode: 'json',
                pythonPath: pythonPath,
                pythonOptions: ['-u'],
                env: { ...process.env, PYTHONUNBUFFERED: '1' },
            });

            pyshell.send({
                action: 'deploy',
                code,
                contract_type: contractType,
                lang
            });
            logToFile('[Deploy] Sent deploy request to Python script');

            pyshell.on('message', (message) => {
                logToFile(`[Deploy] Received message: ${JSON.stringify(message)}`);
                if (message.response) {
                    logToFile(`[Deploy] Resolving with response: ${message.response}`);
                    resolve(message.response);
                } else if (message.error) {
                    const error = new Error(message.error);
                    logToFile(`[Deploy] Error from Python: ${error.message}`);
                    reject(error);
                } else {
                    const error = new Error('Unexpected response format from deploy script');
                    logToFile(`[Deploy] ${error.message}`);
                    reject(error);
                }
            });

            pyshell.on('error', (err) => {
                logToFile(`[Deploy] Python shell error: ${err}`);
                reject(err);
            });

            pyshell.on('stderr', (stderr) => {
                logToFile(`[Deploy] Python stderr: ${stderr}`);
            });

            pyshell.on('pythonError', (error) => {
                logToFile(`[Deploy] Python error: ${error}`);
                reject(new Error(`Python error: ${error}`));
            });

            pyshell.end((err) => {
                if (err) {
                    logToFile(`[Deploy] Error in Python shell end: ${err}`);
                    reject(err);
                } else {
                    logToFile('[Deploy] Python shell execution completed');
                }
            });
        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : String(error);
            logToFile(`[Deploy] Unhandled error: ${errorMsg}`);
            reject(error);
        }
    });
}

export function callModel(prompt: string): Promise<string> {
    return new Promise((resolve, reject) => {
        try {
            const scriptPath = getScriptPath('inferenceLora.py');
            console.log(`[Python] Attempting to execute script at: ${scriptPath}`);
            
            // Verify the script exists
            if (!fs.existsSync(scriptPath)) {
                const errorMsg = `Python script not found at: ${scriptPath}`;
                console.error(errorMsg);
                throw new Error(errorMsg);
            }

            const pythonPath = getPythonPath();
            console.log(`[Python] Using interpreter: ${pythonPath}`);
            
            const pyshell = new PythonShell(scriptPath, {
                mode: 'json',
                pythonPath: pythonPath,
                pythonOptions: ['-u'],
                env: { ...process.env, PYTHONUNBUFFERED: '1' },
            });

            console.log('[Python] Sending prompt to model...');
            pyshell.send({ prompt });

            pyshell.on('message', (message) => {
                console.log('[Python] Received message:', message);
                if (message.response) {
                    resolve(message.response);
                } else if (message.error) {
                    reject(new Error(message.error));
                } else {
                    reject(new Error("Unexpected response format from model"));
                }
            });

            pyshell.on('error', (err) => {
                console.error('[Python] Error event:', err);
                reject(err);
            });

            pyshell.on('stderr', (stderr) => {
                console.error('[Python] stderr:', stderr);
            });

            pyshell.on('pythonError', (err) => {
                console.error('[Python] Python error:', err);
                reject(new Error(`Python error: ${err}`));
            });

            pyshell.end((err) => {
                if (err) {
                    console.error('[Python] End error:', err);
                    reject(err);
                } else {
                    console.log('[Python] Python script execution completed');
                }
            });
        } catch (error) {
            console.error('[Python] Exception in callModel:', error);
            reject(error);
        }
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
                {
                    enableScripts: true,
                }
            );
            panel.webview.html = getWebviewContent(panel.webview, context.extensionUri);
            panel.webview.onDidReceiveMessage(
                async (message) => {
                    console.log('[Webview] Received message:', message);
                    if (message.command === 'generate') {
                        const { purpose, type, lang, chat } = message;
                        const prompt = `instruction: ${chat}\noutput:`;
                        vscode.window.showInformationMessage(`⏳ Generating ${lang} contract for ${chat} with purpose as ${purpose} (${type})...`);
                        try {
                            var code = await callModel(prompt);
                            // Format the output as a code block with the specified language
                            const formattedOutput = `\`\`\`${message.lang || ''}
${code}
\`\`\``;
                            panel.webview.postMessage({ command: 'displayOutput', output: formattedOutput });
                        } catch (err: any) {
                            panel.webview.postMessage({ command: 'error', error: err.message });
                        }
                    }
                    if (message.command === 'deploy'){
                        try {
                            vscode.window.showInformationMessage('🚀 Deploying smart contract...');
                            const deployResult = await deploySmartContract(message.code, message.contractType, message.lang);
                            panel.webview.postMessage({ command: 'displayOutput', output: deployResult });
                        } catch (err: any) {
                            panel.webview.postMessage({ command: 'error', error: err.message });
                        }
                    }
                    if (message.command === 'retry'){
                        const { purpose, type, lang, chat, output } = message;
                        const prompt = `instruction: Improve or modify the following Python contract based on the original request.\n\noutput:\n${output}\n\nOriginal instruction: ${chat}`;
                        vscode.window.showInformationMessage(`⏳ Generating Python contract for ${chat} with purpose as ${purpose} (${type})...`);
                        try {
                            const code = await callModel(prompt);
                            // Format the output as a code block with the specified language
                            const formattedOutput = `\`\`\`${message.lang || ''}
${code}
\`\`\``;
                            panel.webview.postMessage({ command: 'displayOutput', output: formattedOutput });
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
    // Inline completion provider for Python only
    const provider = vscode.languages.registerInlineCompletionItemProvider(
        { language: 'python', scheme: 'file' },
        {
            async provideInlineCompletionItems(document, position, context, token) {
                const linePrefix = document.lineAt(position).text.slice(0, position.character);
                console.log('[Inline] Triggered for linePrefix:', linePrefix);
                
                try {
                    // Get the full text of the current line
                    const currentLine = document.lineAt(position).text;
                    
                    // Don't trigger on empty lines or whitespace-only lines
                    if (!linePrefix.trim()) {
                        return null;
                    }
                    
                    // Get the current word/context
                    const wordRange = document.getWordRangeAtPosition(position);
                    const currentWord = wordRange ? document.getText(wordRange) : '';
                    
                    // Get the full text up to the cursor position for better context
                    const textUntilPosition = document.getText(
                        new vscode.Range(
                            new vscode.Position(0, 0),
                            position
                        )
                    );
                    
                    // Get suggestions based on the current context
                    const suggestion = await getInlineCompletion(textUntilPosition);
                    
                    if (!suggestion) {
                        return null;
                    }

                    return {
                        items: [{
                            insertText: suggestion,
                            range: new vscode.Range(position, position),
                            command: {
                                title: 'Accept Suggestion',
                                command: 'editor.action.triggerSuggest',
                            },
                        }],
                    };
                } catch (err) {
                    console.error('[Inline] Error:', err);
                    return null;
                }
            }
        }
    );
    context.subscriptions.push(provider);
    // Dropdown provider for Python only
    const dropdownProvider = vscode.languages.registerCompletionItemProvider(
        { language: 'python', scheme: 'file' },
        {
            async provideCompletionItems(document, position, token, context) {
                try {
                    const linePrefix = document.lineAt(position).text.slice(0, position.character);
                    console.log('[Dropdown] Triggered with context:', { 
                        linePrefix,
                        triggerCharacter: context?.triggerCharacter,
                        position: position
                    });

                    // Only trigger after a dot or at the start of a word
                    const isDotTrigger = linePrefix.endsWith('.');
                    const isWordStart = /\w$/.test(linePrefix);
                    
                    if (!isDotTrigger && !isWordStart) {
                        console.log('[Dropdown] Not at a trigger position');
                        return [];
                    }

                    // Get the text before the cursor
                    const textBefore = document.getText(new vscode.Range(new vscode.Position(0, 0), position));
                    console.log('[Dropdown] Getting suggestions for textBefore:', textBefore);
                    
                    // Get suggestions from the Python script
                    const suggestions = await getDropdownSuggestions(textBefore);
                    console.log('[Dropdown] Received suggestions:', suggestions);
                    
                    // Create completion items
                    const completionItems = suggestions.map((suggestion, index) => {
                        const item = new vscode.CompletionItem(
                            suggestion,
                            isDotTrigger ? vscode.CompletionItemKind.Method : vscode.CompletionItemKind.Snippet
                        );
                        
                        // For dot completions, remove the dot prefix if present
                        if (isDotTrigger && suggestion.startsWith('.')) {
                            item.insertText = suggestion.substring(1);
                        }
                        
                        item.sortText = String(index).padStart(5, '0');
                        item.preselect = index === 0;
                        
                        return item;
                    });
                    
                    return completionItems;
                    
                } catch (error) {
                    const errorMessage = error instanceof Error ? error.message : String(error);
                    console.error('[Dropdown] Error in provideCompletionItems:', errorMessage);
                    vscode.window.showErrorMessage(`[Dropdown] Completion Error: ${errorMessage}`);
                    return [];
                }
            }
        },
        '.', // Trigger on dot
        ' '  // Also trigger on space
    );
    context.subscriptions.push(dropdownProvider);
    
    console.log('[Extension] Dropdown provider registered');
}
