import os
import base64
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

def encode_image(image_path):
    """Encodes an image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        return

    # Initialize Gemini 2.5 Flash
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)

    base_dir = r"c:\Users\Musaddique Qazi\.gemini\antigravity\playground\spinning-quasar\whatsapp_export\extracted"
    image_files = [
        "00000279-PHOTO-2025-10-21-19-39-53.jpg"
    ]

    all_extracted_text = ""

    for img_file in image_files:
        img_path = os.path.join(base_dir, img_file)
        if not os.path.exists(img_path):
            print(f"Warning: File not found: {img_path}")
            continue

        print(f"Processing {img_file}...")
        try:
            image_data = encode_image(img_path)
            
            message = HumanMessage(
                content=[
                    {
                        "type": "text", 
                        "text": "Transcribe the text in this image. If it contains a list of 12 points or guidelines, please extract them clearly. preserving the original numbering if possible."
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                    }
                ]
            )

            response = llm.invoke([message])
            print(f"--- Extracted from {img_file} ---")
            print(response.content)
            print("-----------------------------------")
            
            all_extracted_text += f"\n\n--- Source: {img_file} ---\n{response.content}"

        except Exception as e:
            print(f"Error processing {img_file}: {e}")

    # Append to file
    output_file = "extracted_12_points.txt"
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(all_extracted_text)
    
    print(f"\nExtraction complete. Appended to {output_file}")

if __name__ == "__main__":
    main()

