from llama_index.llms.ollama import Ollama
from llama_index.core import Settings

llm = Ollama(model="llama3.2:1b", request_timeout=120.0)
Settings.llm = llm

response = llm.complete("What are the normal ranges for human vital signs? List heart rate, blood pressure, SpO2, temperature, and respiratory rate.")
print(response)