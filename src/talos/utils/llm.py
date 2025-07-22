from openai import OpenAI
from openai.types.chat import ChatCompletionToolParam

from talos.tools.web_search import WebSearchTool


class LLMClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.web_search_tool = WebSearchTool()

    def reasoning(self, prompt: str, model: str = "o4-mini", web_search: bool = False) -> str:
        tools: list[ChatCompletionToolParam] = []
        if web_search:
            tools.append(
                {"type": "web_search_preview"}  # type: ignore
            )
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            tools=tools,
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("The response from the LLM was empty.")
        return content

    def deep_research(self, query: str, model: str = "o3-deep-research") -> str:
        search_results = self.web_search_tool.run(query)
        prompt = f"Based on the following search results, please answer the query: {query}\n\nSearch results:\n{search_results}"
        return self.reasoning(prompt, model)
