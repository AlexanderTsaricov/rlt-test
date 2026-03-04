import requests

class LlmApiController:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key отсутствует")

        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def send(self, text):
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "user", "content": text}
            ]
        }

        response = requests.post(self.base_url, headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]