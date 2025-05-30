import sys
import json
import torch
import os
from typing import List, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Common completions for various contexts
COMMON_COMPLETIONS = [
    "True", "False", "None", "[]", "{}", "()", "0", "''",
    "print()", "return", "yield", "pass", "continue", "break",
    "if", "else", "elif", "for", "while", "try", "except", "finally",
    "def", "class", "with", "import", "from"
]

def load_model():
    """Load the model and tokenizer."""
    # Initialize device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[INFO] Using device: {device}", file=sys.stderr)
    
    # Load base model and tokenizer
    base_model = "EleutherAI/gpt-neo-125M"
    print("[INFO] Loading tokenizer...", file=sys.stderr)
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    
    print("[INFO] Loading model...", file=sys.stderr)
    model = AutoModelForCausalLM.from_pretrained(
        base_model, 
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True
    ).to(device)
    
    # Try to load LoRA fine-tuned weights if available
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        lora_path = os.path.join(script_dir, "lora-output")
        
        if os.path.exists(lora_path):
            print(f"[INFO] Loading LoRA weights from {lora_path}", file=sys.stderr)
            model = PeftModel.from_pretrained(model, lora_path).to(device)
            print("[INFO] Successfully loaded LoRA weights", file=sys.stderr)
        else:
            print("[WARNING] LoRA weights not found. Using base model without fine-tuning.", file=sys.stderr)
    except Exception as e:
        print(f"[WARNING] Could not load LoRA weights: {str(e)}. Using base model.", file=sys.stderr)
    
    return model, tokenizer, device

def get_completions(prompt: str, model, tokenizer, device) -> List[str]:
    """
    Generate code completions for the given prompt using the language model.
    
    Args:
        prompt: The input code context to complete
        model: The language model for generating completions
        tokenizer: The tokenizer for the model
        device: The device (CPU/GPU) to run the model on
        
    Returns:
        List of completion strings, or fallback completions if an error occurs
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Clean and validate input
        if not prompt or not isinstance(prompt, str):
            logger.warning("Empty or invalid prompt, using fallback completions")
            return COMMON_COMPLETIONS[:8]
            
        prompt = prompt.strip()
        
        # For very short or empty prompts, return common completions
        if len(prompt) < 3:
            logger.info("Short prompt, returning common completions")
            return COMMON_COMPLETIONS[:8]
            
        # Check if we're in a specific context (e.g., after a dot)
        is_after_dot = prompt.endswith('.')
        is_after_space = prompt.endswith(' ')
        
        # Create a more detailed system prompt
        system_prompt = """You are an expert Python code completion assistant. 
Your task is to provide relevant code completions for the given code context.

Guidelines:
- Return ONLY the completion text, no explanations
- Each completion must be a single line
- Keep completions concise (max 30 characters)
- Include relevant method/property names after dots
- Include relevant keywords in the current scope
- Never include the prompt in the response
- Never include markdown or code blocks
- Never include the word "completion" or "suggestion"
- Never include the word "here" or similar
- Never include the word "code" or similar
- Never include the word "example" or similar
- Never include the word "context" or similar
- Never include the word "prompt" or similar
- Never include the word "input" or similar
- Never include the word "output" or similar
- Never include the word "result" or similar
- Never include the word "function" or similar
- Never include the word "method" or similar
- Never include the word "class" or similar
- Never include the word "object" or similar
- Never include the word "variable" or similar
- Never include the word "parameter" or similar
- Never include the word "argument" or similar
- Never include the word "value" or similar
- Never include the word "return" or similar
- Never include the word "yield" or similar
- Never include the word "raise" or similar
- Never include the word "except" or similar
- Never include the word "finally" or similar
- Never include the word "import" or similar
- Never include the word "from" or similar
- Never include the word "as" or similar
- Never include the word "in" or similar
- Never include the word "is" or similar
- Never include the word "not" or similar
- Never include the word "and" or similar
- Never include the word "or" or similar
- Never include the word "if" or similar
- Never include the word "else" or similar
- Never include the word "elif" or similar
- Never include the word "for" or similar
- Never include the word "while" or similar
- Never include the word "try" or similar
- Never include the word "with" or similar
- Never include the word "def" or similar
- Never include the word "class" or similar
- Never include the word "return" or similar
- Never include the word "yield" or similar
- Never include the word "raise" or similar
- Never include the word "except" or similar
- Never include the word "finally" or similar
- Never include the word "import" or similar
- Never include the word "from" or similar
- Never include the word "as" or similar
- Never include the word "in" or similar
- Never include the word "is" or similar
- Never include the word "not" or similar
- Never include the word "and" or similar
- Never include the word "or" or similar
- Never include the word "if" or similar
- Never include the word "else" or similar
- Never include the word "elif" or similar
- Never include the word "for" or similar
- Never include the word "while" or similar
- Never include the word "try" or similar
- Never include the word "with" or similar
"""

        # Format the prompt for the model
        full_prompt = f"{system_prompt}\n\nCode context:\n{prompt}\n\nCompletions (one per line):\n"
        
        logger.info(f"Generating completions for prompt (length: {len(prompt)})")
        
        # Tokenize input with truncation to avoid exceeding max length
        inputs = tokenizer(
            full_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
            padding='max_length'
        ).to(device)
        
        # Generate completions with adjusted parameters
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=20,  # Keep completions short
                do_sample=True,
                temperature=0.7,    # Balance between creativity and determinism
                top_k=50,           # Consider top 50 tokens at each step
                top_p=0.95,         # Nucleus sampling
                num_return_sequences=8,  # Generate more sequences to get diverse completions
                pad_token_id=tokenizer.eos_token_id,
                no_repeat_ngram_size=2,  # Avoid repetition
                early_stopping=True,
            )
        
        # Process and deduplicate completions
        completions = set()
        for out in output:
            # Decode and clean up the generated text
            text = tokenizer.decode(out, skip_special_tokens=True)
            
            # Extract just the completion part (after the prompt)
            completion = text[len(full_prompt):].strip()
            
            # Split by newlines and process each line
            for line in completion.split('\n'):
                line = line.strip()
                
                # Skip empty lines or very short completions
                if not line or len(line) < 2:
                    continue
                    
                # Remove any remaining prompt fragments
                if 'Code context:' in line:
                    continue
                    
                # Clean up the completion
                line = line.split('\n')[0]  # Only take first line
                line = line.split('#')[0]    # Remove comments
                line = line.split('"')[0]    # Remove string literals
                line = line.split("'")[0]    # Remove string literals
                line = line.strip()
                
                # Skip if too short after cleaning
                if len(line) < 2:
                    continue
                    
                # Add to completions set (automatically deduplicates)
                completions.add(line)
        
        # Convert to list and limit number of suggestions
        completions = list(completions)[:8]
        
        # If no valid completions, use fallback
        if not completions:
            logger.warning("No valid completions generated, using fallback")
            return COMMON_COMPLETIONS[:8]
            
        logger.info(f"Generated {len(completions)} completions")
        return completions
        
    except Exception as e:
        logger.error(f"Error in get_completions: {str(e)}", exc_info=True)
        return COMMON_COMPLETIONS[:8]  # Return fallback completions on error

def main():
    """Main function to handle the completion request."""
    # Set up logging to stderr
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )
    logger = logging.getLogger(__name__)
    
    # Read prompt from stdin
    try:
        # Read all input until EOF
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            raise ValueError("Empty input received")
            
        logger.info(f"Received input (length: {len(raw_input)})")
        
        # Parse JSON input
        data = json.loads(raw_input)
        prompt = data.get("prompt", "")
        
        logger.info(f"Processing prompt (length: {len(prompt)}): {prompt[:100]}...")
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON input: {str(e)}"
        logger.error(error_msg)
        print(json.dumps({"error": error_msg, "input_sample": str(raw_input)[:100]}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        error_msg = f"Error reading input: {str(e)}"
        logger.error(error_msg)
        print(json.dumps({"error": error_msg}), file=sys.stderr)
        sys.exit(1)
    
    try:
        # Load model (this is cached after first load)
        logger.info("Loading model...")
        model, tokenizer, device = load_model()
        
        # Get completions
        logger.info("Generating completions...")
        completions = get_completions(prompt, model, tokenizer, device)
        
        # Ensure we have some completions
        if not completions:
            logger.warning("No completions generated, using fallback")
            completions = COMMON_COMPLETIONS[:5]
        
        # Clean and validate completions
        valid_completions = []
        for comp in completions:
            if isinstance(comp, str) and comp.strip():
                # Remove any line breaks and extra whitespace
                clean_comp = ' '.join(comp.split()).strip()
                if clean_comp and clean_comp not in valid_completions:
                    valid_completions.append(clean_comp)
        
        if not valid_completions:
            logger.warning("No valid completions after cleaning, using fallback")
            valid_completions = COMMON_COMPLETIONS[:5]
        
        # Return the suggestions
        result = {
            "suggestions": valid_completions[:8],  # Max 8 suggestions
            "status": "success",
            "count": len(valid_completions[:8])
        }
        
        logger.info(f"Returning {len(result['suggestions'])} suggestions")
        print(json.dumps(result), file=sys.stdout, flush=True)
        
    except Exception as e:
        import traceback
        error_msg = f"Error processing completion: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        
        # Return error response with fallback completions
        error_result = {
            "suggestions": COMMON_COMPLETIONS[:5],
            "status": "error",
            "error": str(e)
        }
        print(json.dumps(error_result), file=sys.stdout, flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
