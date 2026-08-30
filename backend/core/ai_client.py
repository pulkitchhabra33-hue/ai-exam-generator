from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client= OpenAI(
    api_key= os.getenv("OPENAI_API_KEY"),
    timeout= 60.0,
    max_retries=0
)