import base64
import easyocr

def convertImgToBase64(img):
    encoded_file = base64.b64encode(img).decode('utf-8')
    return encoded_file

def convertBase64ToImg(base64string):
    decoded_file = base64.b64decode(base64string)
    return decoded_file

def performOCR(img):
    reader = easyocr.Reader(['en'])
    extracted_text = reader.readtext(img)
    print(extracted_text)
    return extracted_text

def processData(extracted_text, type):
    # Extract only the text
    if type == "question":
        processed_text = [item[1] for item in extracted_text]
        concatenated_text = " ".join(processed_text)
        print(concatenated_text)
        return concatenated_text
    elif type == "options":
        processed_text = [item[1] for item in extracted_text]
        print(processed_text)
        return processed_text
