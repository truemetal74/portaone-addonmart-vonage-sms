# Add-On Mart module for sending SMS via Vonage (Nexmo) API
## Introduction
It is a Google Cloud function that will serve as a part of [PortaOne
Add-On Mart](https://www.portaone.com/telecom-products/add-on-mart/marketplace/),
allowing telecom operators to send SMS messages from their PortaSwitch system
via Vonage.

### Debugging in VS Code
Add the following configuration into your launch.json
```json
{
    "name": "Python: Run Functions Framework",
    "type": "python",
    "request": "launch",
    "module": "functions_framework",
    "args": ["--target", "send_message", "--debug"],
    "envFile": "${workspaceFolder}/.env",
    "console": "integratedTerminal",
    "cwd": "${workspaceFolder}"
}
```
