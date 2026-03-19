"""
NetworkBuster - Gemini CLI
Local terminal chat interface for Google Gemini API
Usage: python gemini_cli.py
       python gemini_cli.py "your question here"
"""

import os
import sys
import json
import urllib.request
import urllib.error

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
HISTORY = []


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        print("No GEMINI_API_KEY found in environment.")
        key = input("Enter your Gemini API key: ").strip()
        if not key:
            print("No API key provided. Exiting.")
            sys.exit(1)
        os.environ["GEMINI_API_KEY"] = key
    return key


def ask_gemini(api_key, user_message):
    HISTORY.append({"role": "user", "parts": [{"text": user_message}]})

    payload = json.dumps({"contents": HISTORY}).encode("utf-8")
    url = f"{GEMINI_API_URL}?key={api_key}"
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            msg = json.loads(error_body).get("error", {}).get("message", error_body)
        except Exception:
            msg = error_body
        HISTORY.pop()  # remove failed message
        return f"[API Error {e.code}] {msg}"
    except Exception as e:
        HISTORY.pop()
        return f"[Error] {e}"

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        HISTORY.append({"role": "model", "parts": [{"text": text}]})
        return text
    except (KeyError, IndexError):
        HISTORY.pop()
        return "[Error] Unexpected response format."


def print_banner():
    print("\033[95m" + "=" * 55)
    print("  NetworkBuster  ✦  Gemini CLI")
    print("=" * 55 + "\033[0m")
    print('Type your message and press Enter. Type "exit" to quit.')
    print()


def main():
    api_key = get_api_key()

    # One-shot mode: python gemini_cli.py "question"
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        response = ask_gemini(api_key, question)
        print(response)
        return

    # Interactive mode
    print_banner()

    while True:
        try:
            user_input = input("\033[96mYou:\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            print("Goodbye!")
            break
        if user_input.lower() in ("clear", "reset"):
            HISTORY.clear()
            print("[Conversation history cleared]\n")
            continue

        print("\033[93mGemini:\033[0m ", end="", flush=True)
        response = ask_gemini(api_key, user_input)
        print(response)
        print()


if __name__ == "__main__":
    main()
