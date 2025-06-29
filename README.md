# AlgoMate - organization specific assistance

AlgoMate is a VS Code extension that enhances Algorand smart contract development with AI-powered assistance. It helps developers create, edit, and deploy smart contracts more efficiently on the Algorand blockchain. We are offering two versions of our extension : 
- LLM based (ideal for small users since the call is made through API)
- SLM based (ideal for organizations wanting full privacy over model calls)

Refer to this presentation for a better understanding of the project : [Canva Link](https://www.canva.com/design/DAGpI6Uph7w/Lh5caAVq_RUpfJLE3NIzIA/edit)
Refer to this video for the live demo : [Youtube Link](https://youtu.be/e8IfH2FDAbw?si=VRnxti8MqT8Us8P4)
   
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
- **Code Improvement Suggestions**: AI-powered code optimization recommendations

### Difference from other AI
- No Hallucinations due to RAG
- Cosine Similarity to log down relevent examples from the community
- Can be modified to have LLM as a fallback for SLM
- Retry option with prompt and code passed as context
- Direct Deployment options

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

4. Set your Google API key in a `.env` file (if using LLM based):
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
- Powered by Google's Generative AI and Salesforce's Codegen Model 
- Part of the Algorand Developer Ecosystem

---

Made with ❤️ for organizaton specific AI assistance

