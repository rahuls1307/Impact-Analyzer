"""
gemini_impact_analysis.py
Example: Perform impact analysis using Google Gemini API
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()


# Load your API key (make sure it's set in environment variables)
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def analyze_impact(change_description: str, context: str) -> str:
    """
    Ask Gemini to analyze the potential impact of a software/system change.
    """
    prompt = f"""
    You are an expert software architect.
    Analyze the potential impacts of the following change.

    CHANGE:
    {change_description}

    CONTEXT:
    {context}

    Provide:
    1. A summary of affected components/modules.
    2. Possible risks or dependencies.
    3. Suggested mitigation or test strategies.
    """

    # Create the model (Gemini 1.5 Pro or Flash are current)
    model = genai.GenerativeModel("gemini-pro-latest")

    response = model.generate_content(prompt)
    return response.text.strip()

if __name__ == "__main__":
    change = "We are renaming the 'customer_id' field to 'client_id' in the main database schema."
    context = """
    The application has:
    - A REST API for customer data.
    - Analytics pipelines using the customer_id field.
    - Billing system integrated via microservice architecture.
    """

    print("\n--- GEMINI IMPACT ANALYSIS ---\n")
    print(analyze_impact(change, context))
