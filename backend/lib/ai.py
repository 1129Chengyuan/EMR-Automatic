from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

openai = OpenAI(
    api_key=os.getenv("AI_API_KEY"),
)


