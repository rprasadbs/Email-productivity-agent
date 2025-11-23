import requests
import json

def run_llm(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": True
        },
        stream=True
    )

    final_output = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            final_output += data.get("response", "")
    return final_output.strip()
