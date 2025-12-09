import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("No GROQ_API_KEY found.")
else:
    client = Groq(api_key=api_key)
    print("Listing available Groq models...")
    try:
        models = client.models.list()
        for m in models.data:
            print(f"ID: {m.id}")
            print(f"Owned by: {m.owned_by}")
            print("-" * 20)
    except Exception as e:
        print(f"Error listing models: {e}")
