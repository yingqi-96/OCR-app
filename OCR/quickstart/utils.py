import base64, easyocr, os, fitz
from openai import OpenAI

# option_index = {0:"A",1:"B",2:"C",3:"D"}
option_index = ["A","B","C","D"]

def convertImgToBase64(img):
    try:
        encoded_file = base64.b64encode(img).decode('utf-8')
        print(encoded_file)
        return encoded_file
    except Exception as e:
        return None

def convertBase64ToImg(base64string):
    try:
        decoded_file = base64.b64decode(base64string)
        print(decoded_file)
        return decoded_file
    except Exception as e:
        return None

##functions using easyOCR
def easyOCR(img):
    reader = easyocr.Reader(['en'])
    try:
        extracted_text = reader.readtext(img)  # Perform OCR
        print(extracted_text)
        return extracted_text  # Return results if successful
    except FileNotFoundError:
        return {"error": "File not found. Please check the image path."}
    except ValueError as e:
        return {"error": f"Invalid image format: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def processData(extracted_text, type):
    # Extract only the text
    try:
        if type == "question":
            processed_text = [item[1] for item in extracted_text]
            concatenated_text = " ".join(processed_text)
            print(concatenated_text)
            return concatenated_text
        elif type == "options":
            processed_text = {option_index[index]: item[1] for index, item in enumerate(extracted_text)}
            print(processed_text)
            return processed_text
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
    
def passDataThroughOpenAPI():
    # Extract only the text
    try:
        client = OpenAI(
        api_key="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"
        )

        completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": "write a haiku about ai"}
        ]
        )
        print(completion.choices[0].message);    
        return completion
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def convert_pdf_to_images(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # 0-based page index
        pix = page.get_pixmap()
        image_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
        pix.save(image_path)
        image_paths.append(image_path)

    return image_paths