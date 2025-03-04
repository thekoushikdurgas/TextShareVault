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
        system_prompt = """
        Analyze the provided content and structure your response in the following format:

        1. Summary
        - Brief overview of the content
        - Key points or main ideas

        2. Technical Analysis (if applicable)
        - Code quality assessment
        - Best practices evaluation
        - Potential improvements

        3. Content Analysis
        - Writing style and tone
        - Organization and structure
        - Clarity and readability

        4. Image Analysis (if provided)
        - Description of visual elements
        - Relevance to the content
        - Technical details

        5. Recommendations
        - Specific suggestions for improvement
        - Additional considerations

        Format the response with clear headers and bullet points for readability.
        Use Markdown formatting for better presentation:
        - Use ## for section headers
        - Use * for bullet points
        - Use ` for code snippets
        - Use > for important quotes or highlights
        """

        messages = [
            {
                "role": "system",
                "content": system_prompt
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