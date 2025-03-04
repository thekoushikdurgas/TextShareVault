import os
import base64
from openai import OpenAI
from urllib.parse import urlparse

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

def analyze_content(text, image_url=None, model="google/gemini-exp-1206:free"):
    """Analyze text content and optional image using AI"""
    try:
        messages = [
            {
                "role": "system",
                "content": "Analyze the following content and provide insights. If there's an image, describe it and include it in the analysis."
            },
            {
                "role": "user",
                "content": []
            }
        ]

        # Add text content
        messages[1]["content"].append({
            "type": "text",
            "text": text
        })

        # Add image if provided
        if image_url:
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })

        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            extra_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Text Share Analysis",
            }
        )

        return completion.choices[0].message.content
    except Exception as e:
        return f"Analysis failed: {str(e)}"