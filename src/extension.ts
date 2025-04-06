import * as vscode from 'vscode';
import { getWebviewContent } from './webview'; // you'll create this

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
      panel.webview.onDidReceiveMessage(message => {
        switch (message.command) {
          case 'generate':
            vscode.window.showInformationMessage(`Generating ${message.lang} contract for ${message.purpose} with type ${message.type}`);
            // Insert or generate logic here
            
            break;
        }
      });
      
    })
  );
}
