from openai import OpenAI

class Chat:
    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key: str = api_key
        self.base_url: str = base_url
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def default_chat(
        self,
        model: str,
        messages: list,
        max_tokens: int,
        temperature: float,
        top_p: float,
        frequency_penalty: float,
        presence_penalty: float,
        stop: list = None,
        stream: bool = True):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            stream=stream)
        return response