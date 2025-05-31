# ByteBandits - Algorand Smart Contract Assistant

ByteBandits is a VS Code extension that enhances Algorand smart contract development with AI-powered assistance. It helps developers create, edit, and deploy smart contracts more efficiently on the Algorand blockchain.

## ✨ Features

### Smart Contract Generation
- **Purpose-based Templates**: Generate contracts for various use cases:
  - Escrow
  - NFT (Non-Fungible Tokens)
  - DAO (Decentralized Autonomous Organizations)
  - DeFi (Decentralized Finance)
  - Voting systems
  - And more...

### Contract Types
- Support for different Algorand contract types:
  - Stateful contracts
  - Stateless contracts
  - Signature-based contracts

### Development Tools
- **AI-Powered Code Completion**: Get intelligent code suggestions as you type
- **Inline Documentation**: Automatic generation of docstrings and documentation
- **Gas Fee Estimation**: Estimate transaction costs before deployment
- **Code Improvement Suggestions**: AI-powered code optimization recommendations

### Supported Languages
- Primary language: Python (PyTeal)
- Clean and readable code generation

## 🚀 Getting Started

### Prerequisites
- Node.js (v14+)
- VS Code (v1.70+)
- Python 3.8+
- Algorand Developer Tools (Goal, Sandbox, or TestNet access)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ByteBandits.git
   cd ByteBandits
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up Python dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Set your Google API key in a `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. Build and run the extension in VS Code:
   - Press `F5` to open a new VS Code window with the extension loaded
   - Or use the command palette: `Developer: Run Extension`

## 🛠️ Usage

1. Open the Algorand Contract Builder panel using the command palette (`Ctrl+Shift+P` or `Cmd+Shift+P`):
   ```
   Open Algorand Contract Panel
   ```

2. Configure your contract:
   - Select the contract purpose
   - Choose the contract type
   - Select the programming language
   - Enter any specific requirements

3. Generate and deploy your contract with a single click

## 🤖 AI Features

### Code Completion
- Get context-aware suggestions by typing `.` after an object
- AI-powered method and property recommendations

### Documentation Generation
- Automatic docstring generation for smart contracts
- Real-time documentation as you code

### Code Improvement
- Get suggestions for optimizing your smart contract code
- Security best practices for Algorand development

## 📦 Project Structure

```
ByteBandits/
├── src/                    # TypeScript source code
├── media/                  # Extension assets
├── data/                   # Sample contracts and templates
├── .vscode/                # VS Code configuration
├── .venv/                  # Python virtual environment
├── .gitignore
├── package.json            # Extension manifest
├── requirements.txt        # Python dependencies
└── README.md
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [VS Code Extension API](https://code.visualstudio.com/api)
- Powered by Google's Generative AI
- Part of the Algorand Developer Ecosystem

---

Made with ❤️ for the Algorand community

