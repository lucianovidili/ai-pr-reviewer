import os
import requests

# 1. Get secrets and environment variables that GitHub Actions provides
# - GITHUB_TOKEN: allows the script to authenticate back to GitHub and post comments
# - MISTRAL_API_KEY: your Mistral API key stored as a GitHub secret
# - GITHUB_REPOSITORY: "owner/repo" format (e.g., "user/myproject")
# - GITHUB_PR_NUMBER: pull request number triggered by the workflow
github_token = os.getenv("GITHUB_TOKEN")
mistral_api_key = os.getenv("MISTRAL_API_KEY")
repo = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("GITHUB_PR_NUMBER")

# 2. Define HTTP headers for GitHub API calls (auth + JSON content)
headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github+json"}

# 3. Build the URL to fetch all changed files (diffs/patches) from the PR
files_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"

# 4. Make GET request to GitHub to get all file changes in the PR
response = requests.get(files_url, headers=headers)
files = response.json()  # JSON response contains filename + diff (patch)

# 5. Collect all the code patches (diff hunks) into a single string
diffs = []
for f in files:
    patch = f.get("patch")  # each file may or may not have a diff
    if patch:
        diffs.append(f"File: {f['filename']}\n{patch}")  # label by filename

# 6. Join all diffs into one big text block (to send to the AI model)
code_diff = "\n\n".join(diffs)

# 7. Prepare the review prompt for Mistral.
# We instruct the model to act like a senior engineer and review the diff.
prompt = f"""
You are a senior software engineer. 
Review the following code changes and provide constructive feedback:
- Identify potential bugs
- Suggest best practices
- Point out missing tests or documentation
- Mention possible performance improvements

Code changes:
{code_diff}
"""

# 8. Define the Mistral API endpoint for chat completions
mistral_url = "https://api.mistral.ai/v1/chat/completions"

# 9. Set up headers for Mistral API (bearer token auth + JSON content)
mistral_headers = {
    "Authorization": f"Bearer {mistral_api_key}",
    "Content-Type": "application/json"
}

# 10. Build the JSON payload for the request
# - model: which Mistral model to use ("mistral-medium" or "codestral" for code tasks)
# - messages: conversation with the AI (we only need one user message here)
# - max_tokens: cap the length of response
data = {
    "model": "mistral-medium",  # could also use "codestral" for code reviews
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 500
}

# 11. Send POST request to Mistral API with the diff prompt
ai_response = requests.post(mistral_url, headers=mistral_headers, json=data)

# 12. Parse the response JSON and extract the model’s review text
review_text = ai_response.json()["choices"][0]["message"]["content"]

# 13. Build the URL to post a comment back into the PR (comments API is under "issues")
comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

# 14. Create the body of the comment with AI review text, include a 🤖 label
comment_body = {"body": f"🤖 **AI Code Review (Mistral)**:\n\n{review_text}"}

# 15. Send POST request to GitHub API to post the review comment on the PR
requests.post(comment_url, headers=headers, json=comment_body)

# 16. Print a log message (useful for debugging in GitHub Actions logs)
print("✅ AI review (Mistral) posted successfully!")

# 17. Modifying a file
print("Hello")
