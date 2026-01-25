import os
from dotenv import load_dotenv
from google import genai
from argparse import ArgumentParser
from google.genai import types


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError('Key has not been found')
    client = genai.Client(api_key=api_key)

    args = parse_arguments()
    prompt = args.user_prompt

    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])] 

    response = client.models.generate_content(
        model='gemini-2.5-flash', contents=messages
    )

    if response.usage_metadata is None:
        raise RuntimeError('Usage Metadata not returned!')

    model_response(prompt, response, verbose=args.verbose)

    
def model_response(prompt, response, verbose=False):
    if verbose:
        print(f'User prompt: {prompt}')
        print(f'Prompt tokens: {response.usage_metadata.prompt_token_count}')
        print(f'Response tokens: {response.usage_metadata.candidates_token_count}')
    print(f'Response:\n{response.text} ')


def parse_arguments():
    parser = ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()

if __name__ == "__main__":
    main()
