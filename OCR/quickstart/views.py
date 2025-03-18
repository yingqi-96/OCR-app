import os 
import datetime
from django.conf import settings
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from rest_framework import status
from rest_framework.response import Response

from .serializers import GroupSerializer, UserSerializer, QuestionBankSerializer, LabelOptionsSerializer, FileUploadSerializer, ImageUploadSerializer 
from .utils import easyOCR, processData, convertImgToBase64, passDataThroughOpenAPI
from .models import QuestionBank, LabelOptions

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class UploadPDFView(viewsets.ViewSet):
    serializer_class = FileUploadSerializer

    def list(self, request):
        return Response("GET")

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            uploaded_file = request.FILES['file']

            if not uploaded_file.content_type.startswith("application/pdf"):
                return Response({"error": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)
           
            try: 
                # Get the original filename and extension
                filename, extension = os.path.splitext(uploaded_file.name)

                # Append current timestamp to filename
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"{filename}_{timestamp}{extension}"

                # Set a custom file path (e.g., 'uploads/')
                file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', new_filename)
                
                # Ensure the target directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Save the file to the desired location
                with open(file_path, 'wb') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                return Response({"message": "File uploaded successfully", "file_path": file_path}, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UploadImageView(viewsets.ViewSet):
    serializer_class = FileUploadSerializer

    def list(self, request):
        return Response("GET")

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            uploaded_file = request.FILES['file']

            if not uploaded_file.content_type.startswith("image/"):
                return Response({"error": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)
           
            try: 
                # Get the original filename and extension
                filename, extension = os.path.splitext(uploaded_file.name)

                # Append current timestamp to filename
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"{filename}_{timestamp}{extension}"

                # Set a custom file path (e.g., 'uploads/')
                file_path = os.path.join(settings.MEDIA_ROOT, 'images', new_filename)
                
                # Ensure the target directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Save the file to the desired location
                with open(file_path, 'wb') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                return Response({"message": "File uploaded successfully", "file_path": file_path}, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UploadImageAndProcessWithEasyOCR(viewsets.ViewSet):
    serializer_class = ImageUploadSerializer

    def list(self, request):
        # Fetch all QuestionBank objects, ordered by created_at
        queryset = QuestionBank.objects.all().order_by('created_at')
        # Serialize the queryset using the QuestionBankSerializer
        serializer = QuestionBankSerializer(queryset, many=True)
        # Return the serialized data in the response
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data)

        # Initialize variables for the extracted question and options
        extracted_question = None
        extracted_options = None
        processed_question = None
        processed_options = None
        question_base64 = None
        options_base64 = None
        new_question_serialised = QuestionBankSerializer()

        if serializer.is_valid():
            uploaded_question =  serializer.validated_data['question']
            uploaded_options =  serializer.validated_data['options']

            if not uploaded_question and not uploaded_options:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not uploaded_question.content_type.startswith("image/") and not uploaded_options.content_type.startswith("image/"):
                return Response({"error": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Process image files
            if uploaded_question is not None:
                question = uploaded_question.read()
                question_base64= convertImgToBase64(question)

                # Convert file content to an image format easyOCR can process
                extracted_question = easyOCR(question)
                 # Check if the function returned an error
                if isinstance(extracted_question, dict) and "error" in extracted_question:
                    return Response(extracted_question, status=status.HTTP_400_BAD_REQUEST)

                processed_question = processData(extracted_question, "question")
                if isinstance(processed_question, dict) and "error" in processed_question:
                    return Response(processed_question, status=status.HTTP_400_BAD_REQUEST)

            # Process image files
            if uploaded_options is not None:
                options = uploaded_options.read()
                options_base64= convertImgToBase64(options)

                # Convert file content to an image format easyOCR can process
                extracted_options = easyOCR(options)
                 # Check if the function returned an error
                if isinstance(extracted_options, dict) and "error" in extracted_options:
                    return Response(extracted_options, status=status.HTTP_400_BAD_REQUEST)

                processed_options = processData(extracted_options, "options")
                if isinstance(processed_options, dict) and "error" in processed_options:
                    return Response(processed_options, status=status.HTTP_400_BAD_REQUEST)
            
            # Add processed_text into db
            try: 
                new_question = QuestionBank.objects.create(
                    question= {
                        "question": processed_question,
                        "options": processed_options
                    },
                    question_image_base64= question_base64,
                    options_image_base64= options_base64
                )
                
                new_question_serialised = QuestionBankSerializer(new_question)
            except Exception as e:
                return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Return structured JSON response
            return Response({
                "extracted_question": extracted_question,
                "extracted_options": extracted_options,
                "processed_question": processed_question,
                "processed_options": processed_options,
                "new_question": new_question_serialised.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProcessData(viewsets.ViewSet):
    def list(self, request):
        return Response("GET")

    def post(self, request):
        # Add processed_text into db
        try: 
            chat = passDataThroughOpenAPI()        
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Return structured JSON response
        return Response(status=status.HTTP_201_CREATED)

class QuestionBankView(viewsets.ViewSet):
    serializer_class = QuestionBankSerializer

    def list(self, request):
        filter_params = request.query_params.dict() # Convert QueryDict to a regular dictionary

        # Convert known integer fields to integers
        if "difficulty" in filter_params:
            try:
                filter_params["difficulty"] = int(filter_params["difficulty"])
            except ValueError:
                return Response({"error": "Invalid difficulty value"}, status=status.HTTP_400_BAD_REQUEST)

        if filter_params:  
            queryset = QuestionBank.objects.filter(**filter_params)  # Apply filtering
        else:
            # Fetch all QuestionBank objects, ordered by created_at
            queryset = QuestionBank.objects.all().order_by('created_at')
        # Serialize the queryset using the QuestionBankSerializer
        serializer = QuestionBankSerializer(queryset, many=True)
        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = QuestionBankSerializer(data=request.data)

        if serializer.is_valid():
            # Save the updated data
            serializer.save()
            # Return the updated object as the response
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # If validation fails, return an error response with details
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
            try:
                # Retrieve the question by its primary key (id)
                question = QuestionBank.objects.get(question_id=request.data.get('question_id'))
            except QuestionBank.DoesNotExist:
                return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the incoming data to validate it (you can use partial=True for partial updates)
            serializer = QuestionBankSerializer(question, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data
                serializer.save()

                # Return the updated object as the response
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # If validation fails, return an error response with details
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    def destroy(self, request, pk=None):
        try:
            question = QuestionBank.objects.get(question_id=pk)
            question.delete()
            return Response({"message": "Question deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except QuestionBank.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        
class LabelOptionsView(viewsets.ViewSet):
    serializer_class = LabelOptionsSerializer

    def list(self, request):
        filter_params = request.query_params.dict() # Convert QueryDict to a regular dictionary

        if filter_params:  
            queryset = LabelOptions.objects.filter(**filter_params)  # Apply filtering
        else:
            # Fetch all QuestionBank objects, ordered by created_at
            queryset = LabelOptions.objects.all().order_by('created_at')
        # Serialize the queryset using the QuestionBankSerializer
        serializer = LabelOptionsSerializer(queryset, many=True)
        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = LabelOptionsSerializer(data=request.data)

        if serializer.is_valid():
            # Save the updated data
            serializer.save()
            # Return the updated object as the response
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # If validation fails, return an error response with details
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
            try:
                # Retrieve the question by its primary key (id)
                label_option = LabelOptions.objects.get(label_id=request.data.get('label_id'))
            except LabelOptions.DoesNotExist:
                return Response({"error": "Label Option not found"}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the incoming data to validate it (you can use partial=True for partial updates)
            serializer = LabelOptionsSerializer(label_option, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated data
                serializer.save()

                # Return the updated object as the response
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # If validation fails, return an error response with details
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    def destroy(self, request, pk=None):
        try:
            label_option = LabelOptions.objects.get(label_id=pk)
            label_option.delete()
            return Response({"message": "Label Option deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except LabelOptions.DoesNotExist:
            return Response({"error": "Label Option not found"}, status=status.HTTP_404_NOT_FOUND)
        

#   class UploadImage(ViewSet):
#     serializer_class = FileUploadSerializer

#     def list(self, request):
#         return Response("GET API")

#     def post(self, request):
#         uploaded_file = request.FILES['file']
#         file_content = uploaded_file.read()

#         if uploaded_file.content_type.startswith("image/"):
#             encoded_file = base64.b64encode(file_content).decode('utf-8')
#             file_type = "image"
#         elif uploaded_file.content_type.startswith("text/"):
#             encoded_file = file_content.decode('utf-8')
#             file_type = "text"
#         else:
#             return Response({"error": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST) 
    

#         # Send the base64 image to the DeepSeek OCR API (replace with actual API endpoint)
#         deepseek_url = "https://api.deepseek.com"  # Example URL
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": "sk-66f8054f66164713a758a0eb4708b129",  # Replace with your API key
#         }
#         payload = {
#             "image": encoded_file,
#         }

#         print(payload)

#         # Make the API request
#         response = requests.post(deepseek_url, json=payload, headers=headers)

#         # Return the OCR result
#         if response.status_code == 200:
#             return Response(response.json(), safe=False)
#         else:
#             return Response({"error": "Failed to process image"}, status=500)

