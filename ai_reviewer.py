import os
import sys
import requests

# This script sends the PR diff to Mistral API for review
# and prints AI-generated feedback as a PR comment. 1111

def review_code(diff_text):
    """Send PR diff to Mistral API and return review text."""

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-tiny",  # you can try mistral-small or mistral-medium too
        "messages": [
            {"role": "system", "content": "You are an AI code reviewer. Provide clear, actionable feedback."},
            {"role": "user", "content": diff_text}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    ai_response = response.json()

    # Debug: print raw response for troubleshooting
    print("🔎 Raw response from Mistral:", ai_response)

    # If choices are missing, show error and stop
    if "choices" not in ai_response:
        print("❌ Error: 'choices' not found in response.")
        sys.exit(1)

    return ai_response["choices"][0]["message"]["content"]


if __name__ == "__main__":
    # Read the diff text from stdin (GitHub Action passes PR diff here)
    diff_text = sys.stdin.read()

    if not diff_text.strip():
        print("⚠️ No diff text provided. Exiting.")
        sys.exit(0)

    review_text = review_code(diff_text)
    print("✅ AI Review:\n", review_text)
