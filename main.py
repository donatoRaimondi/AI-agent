import os
import sys
from dotenv import load_dotenv
from google import genai
from argparse import ArgumentParser
from google.genai import types
from prompts import system_prompt
from call_function import call_function, available_functions

MAX_ITERS = 20

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("Key has not been found")
    client = genai.Client(api_key=api_key)

    args = parse_arguments()
    prompt = args.user_prompt

    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]

    for _ in range(MAX_ITERS):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0,
                tools=[available_functions],
            ),
        )

        if response.usage_metadata is None:
            raise RuntimeError("Usage Metadata not returned!")

        # Add model candidates to conversation history
        if not response.candidates:
            raise RuntimeError("No candidates returned!")
        for cand in response.candidates:
            if cand.content is not None:
                messages.append(cand.content)

        function_responses = model_response(prompt, response, verbose=args.verbose)

        if function_responses:
            messages.append(types.Content(role="user", parts=function_responses))
        else:
            break
    else:
        print(
            f"Error: reached the maximum number of iterations ({MAX_ITERS}) "
            "without the model producing a final response."
        )
        sys.exit(1)

def model_response(prompt, response, verbose=False):
    if verbose:
        print(f"User prompt: {prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    function_responses = []

    if isinstance(response.function_calls, list) and response.function_calls:
        for function_call in response.function_calls:
            function_call_result = call_function(function_call, verbose=verbose)

            if not (isinstance(function_call_result.parts, list) and function_call_result.parts):
                raise Exception("Error: tool did not return a non-empty parts list")

            if function_call_result.parts[0].function_response is None:
                raise Exception("Error: tool did not return a valid function_response")

            if function_call_result.parts[0].function_response.response is None:
                raise Exception("Error: tool did not return a valid function_response.response")

            function_responses.append(function_call_result.parts[0])

            if verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")

        return function_responses

    print(f"Response:\n{response.text}")
    return None

def parse_arguments():
    parser = ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()

if __name__ == "__main__":
    main()
