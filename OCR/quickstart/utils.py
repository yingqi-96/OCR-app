import base64
import easyocr

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

def performOCR(img):
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
