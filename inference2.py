import logging
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_model():
    try:
        model_path = Path(__file__).parent / "codet5-algorand"
        logger.info(f"Loading model from {model_path}")
        
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True)
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")
        
        model.to(device)
        model.eval()
        return model, tokenizer, device
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

def generate_code(instruction, model, tokenizer, device):
    try:
        logger.info(f"Generating code for instruction: {instruction}")
        
        # Add template to guide the model
        template = """
from pyteal import *

def approval_program():
    # Global state
    
    # Local state
    
    # Opt-in logic
    
    # Main logic
    
    return program

def clear_state_program():
    return Return(Int(1))

if __name__ == "__main__":
    print(compileTeal(approval_program(), mode=Mode.Application))
"""
        
        # Combine template with instruction
        full_prompt = f"""
{instruction}

Here's a template to follow:
{template}
"""
        
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, padding=True).to(device)
        
        # Use beam search with temperature for better quality
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=1024,  # Increased max length for more complex contracts
                num_beams=5,     # Use beam search
                temperature=0.7,  # Add some randomness
                do_sample=False,
                early_stopping=True,
                top_p=0.9,       # Add nucleus sampling
                repetition_penalty=1.2  # Prevent repetition
            )
        
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logger.info("Code generation completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        raise

def main():
    try:
        # Load model
        model, tokenizer, device = load_model()
        
        # Enhanced prompt with more specific details
        instruction = """
Create a PyTeal smart contract that implements a trustee-based approval system with the following requirements:

1. Account Management:
   - Support for multiple trustee accounts
   - Delegatee account management
   - Account opt-in functionality

2. Approval System:
   - Threshold-based approval tracking
   - Support for multiple approval levels
   - Vote counting mechanism

3. State Management:
   - Local state for individual account tracking
   - Global state for system-wide variables
   - State update validation

4. Security Features:
   - Proper error handling
   - Input validation
   - Reentrancy protection

5. Best Practices:
   - Follow PyTeal coding standards
   - Include proper comments
   - Use efficient TEAL operations

Generate complete, working code with proper structure and error handling.
"""
        
        # Generate code
        result = generate_code(instruction, model, tokenizer, device)
        
        print("\n📜 Generated Output:\n", result)
        
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
