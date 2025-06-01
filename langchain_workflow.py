import os
from langchain_google_genai import GoogleGenerativeAI

api_key="AIzaSyD3rI3wtUKgflYhQ5rcTlmloOGMiyn3e0E"
def analyze_pull_request(title: str, body: str) -> str:
    # Initialize Gemini LLM (make sure GEMINI_API_KEY is set in env)
    llm = GoogleGenerativeAI(model="gemini-1.5-flash-002", api_key=api_key)

    # Craft prompt to analyze PR content
    prompt = (
        f"Analyze the following GitHub pull request and provide:\n"
        f"1. A concise summary.\n"
        f"2. Suggestions for improvement.\n\n"
        f"Title: {title}\n"
        f"Body: {body}\n\n"
        f"Response:"
    )

    # Get the AI-generated response
    response = llm(prompt)
    return response

# If running standalone for testing locally
if __name__ == "__main__":
    # Example PR title and body for local test
    example_title = "Add new feature to automate data processing"
    example_body = (
        "This PR adds a new LangChain workflow for processing data automatically "
        "when new files arrive. It includes unit tests and README updates."
    )

    analysis = analyze_pull_request(example_title, example_body)
    print("Analysis of pull request:")
    print(analysis)
