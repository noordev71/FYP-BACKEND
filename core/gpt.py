import json
import time
# from anthropic import Anthropic
import os
# import google.generativeai as genai
from django.conf import settings

# Replace this with the Gemini API URL
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# client = Anthropic(
#     api_key=os.environ.get("ANTHROPIC_API_KEY"),
# )


# def get_claude_completion(prompt_template, max_tokens=1024):
#     stream_prompt_completion = client.messages.create(
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt_template,
#             }
#         ],
#         model="claude-3-5-sonnet-20240620",
#         stream=True,
#         max_tokens=max_tokens,
#     )

#     for chunk in stream_prompt_completion:
#         message_dict = chunk.to_dict().get("delta")

#         if message_dict is not None:
#             text_chunk = message_dict.get("text")

#             if not text_chunk:
#                 return
#             data = json.dumps(
#                 {
#                     "message": "Response is being generated",
#                     "data": text_chunk,
#                 }
#             )
#             yield f"data: {data}\n\n"


# def claude_complete_response_integration(prompt_id, variables):
#     response = client.prompts.completions.create(
#         prompt_id=prompt_id, variables=variables, stream=False
#     )

#     if "choices" in response or response["choices"]:
#         choice = response["choices"][0]
#         if hasattr(choice, "message") and hasattr(choice.message, "content"):
#             content = choice.message.content
#             return content


# def get_gemini_completion(prompt_text):
#     try:
#         response = gemini_model.generate_content(prompt_text, stream=True)
#         for chunk in response:
#             if not chunk:
#                 break

#             if chunk:
#                 data = json.dumps(
#                     {
#                         "message": "Response is being generated",
#                         "data": chunk.text,
#                     }
#                 )
#                 yield f"data: {data}\n\n"
#     except requests.exceptions.RequestException as e:
#         print(f"Error: {e}")
#         return

def get_gemini_completion(prompt_text):
    # A list of fake chunks we will stream
    chunks = [
        "Hello ",
        "this ",
        "is ",
        "a ",
        "test ",
        "response."
    ]

    for part in chunks:
        data = json.dumps({
            "message": "streaming",
            "data": part
        })
        yield f"data: {data}\n\n"
        time.sleep(0.3)  # simulate delay

    # end message
    yield "data: {\"message\": \"completed\"}\n\n"


def get_gemini_title_completion(prompt_text):
    # try:
        # response = gemini_model.generate_content(prompt_text, stream=False)
        # full_data = ""

        # for chunk in response:
        #     if not chunk:
        #         break

        #     # Append each chunk's text to full_data
        #     full_data += chunk.text

        # Return the full data in the required JSON format
    full_data="Generated Title from Gemini"
    data = full_data
    return data

    # except requests.exceptions.RequestException as e:
    #     print(f"Error: {e}")
    #     return json.dumps(
    #         {
    #             "message": "Error occurred",
    #             "error": str(e),
    #         }
    #     )


def get_LLM_completion(prompt_template, **kwargs):
    for chunk in get_gemini_completion(prompt_template):
        yield chunk
    
