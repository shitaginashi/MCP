import sys
import requests
import time
import yaml # NEW: Import PyYAML for compliant data handling

# NOTE: This agent no longer uses argparse or a main block.
# It is designed to be called by the Mark 3 harness.

def brand_content_with_llm(generic_content: str, config: dict) -> dict:
    """
    Applies branding to the generic content by using a local vLLM server.
    
    Args:
        generic_content: The raw text string to be branded.
        config: A dictionary containing agent configuration, including the 
                'vllm_api_url' and 'llm_params'.
    
    Returns:
        A YAML-compliant dictionary of branded metadata.
    """
    
    # 1. Compliant Configuration (URL and Parameters from the config dictionary)
    api_url = config.get("vllm_api_url", "http://localhost:8080/generate")
    llm_params = config.get("llm_params", {})
    
    # Base payload structure
    payload = {
        "prompt": f"Act as a world-class financial analyst and digital marketer. Your task is to take the following raw, generic text and re-write it to be compelling, professional, and SEO-optimized for a corporate blog post. The re-written content must be a single, concise paragraph.\n\nRaw Text: {generic_content}\n\nRe-written Content:",
        "use_beam_search": False,
        "n": 1,
        "best_of": 1,
        "max_tokens": 256,
        "temperature": 0.5,
        "stop": ["\n", "\n\n", "Re-written Content:"],
        # Merge with LLM parameters from YAML config (top_p, etc.)
        **llm_params
    }

    max_retries = config.get("max_retries", 3)
    retry_delay = config.get("retry_delay", 1)

    for attempt in range(max_retries):
        try:
            print(f"Calling vLLM server for content branding (Attempt {attempt + 1}/{max_retries})...", file=sys.stderr)
            
            # 2. Renounced JSON for API Call (Still uses JSON for API protocol, but output is YAML-ready)
            response = requests.post(api_url, json=payload, timeout=60)
            response.raise_for_status()

            api_result = response.json()

            if api_result and api_result.get('text'):
                branded_text = api_result['text'][0]

                # 3. YAML-Compliant Output Structure (Returns a dictionary)
                return {
                    "title": "Optimized by vLLM DSOP",
                    "keywords": ["AI", "branding", "LLM", "SEO", "vLLM"],
                    "branded_description": branded_text,
                    "model": "vLLM"
                }
            
            # Error handling remains functional
            ...

    # Final return block (still YAML-compliant dictionary)
    return {
        "title": "LLM Branding Failed",
        "keywords": [],
        "branded_description": "Failed to generate branded content from vLLM.",
        "model": "vLLM"
    }

# NOTE: The Argparse and if __name__ == "__main__": block is entirely removed.