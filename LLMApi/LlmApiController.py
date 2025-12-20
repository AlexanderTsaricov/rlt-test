import requests

class LlmApiController:
    def __init__(self, api_url="https://apifreellm.com/api/chat"):
        """
        api_url: URL для POST-запроса к бесплатному LLM
        """
        self.api_url = api_url

    def send(self, text):
        """
        Отправляет текст в AI и возвращает ответ
        """
        headers = {"Content-Type": "application/json"}
        payload = {"message": text}

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response") or data.get("output") or str(data)
        except Exception as e:
            print("Ошибка при запросе к AI:", e)
            return None



    
