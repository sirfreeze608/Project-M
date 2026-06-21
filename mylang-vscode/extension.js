const vscode = require("vscode");
const path   = require("path");
const cp     = require("child_process");

function activate(context) {
    const run = vscode.commands.registerCommand("mylang.runFile", () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage("mylang: No active file to run.");
            return;
        }
        const filePath = editor.document.fileName;
        if (!filePath.endsWith(".ml")) {
            vscode.window.showErrorMessage("mylang: Not a .ml file.");
            return;
        }

        editor.document.save().then(() => {
            // Try 'mylang' CLI first, fall back to python main.py
            let terminal = vscode.window.terminals.find(t => t.name === "mylang");
            if (!terminal) {
                terminal = vscode.window.createTerminal({ name: "mylang" });
            }
            terminal.show(true);

            // Use the CLI if available, otherwise python fallback
            const cmd = process.platform === "win32"
                ? `mylang "${filePath}" 2>&1 || python "${path.join(path.dirname(filePath), '..', 'mylang', 'main.py')}" "${filePath}"`
                : `mylang "${filePath}" 2>&1 || python3 "${path.join(path.dirname(filePath), '..', 'mylang', 'main.py')}" "${filePath}"`;
            terminal.sendText(cmd);
        });
    });

    context.subscriptions.push(run);

    // Status bar item showing language
    const statusItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left, 100);
    statusItem.command = "mylang.runFile";

    const updateStatus = (editor) => {
        if (editor && editor.document.fileName.endsWith(".ml")) {
            statusItem.text = "$(play) Run mylang";
            statusItem.tooltip = "Run this .ml file (F5)";
            statusItem.show();
        } else {
            statusItem.hide();
        }
    };

    vscode.window.onDidChangeActiveTextEditor(updateStatus, null, context.subscriptions);
    updateStatus(vscode.window.activeTextEditor);
    context.subscriptions.push(statusItem);
}

function deactivate() {}

module.exports = { activate, deactivate };
