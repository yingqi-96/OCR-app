from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from rest_framework import status
from rest_framework.response import Response

from .serializers import GroupSerializer, UserSerializer, QuestionBankSerializer, FileUploadSerializer 
from .utils import performOCR, processData, convertImgToBase64
from .models import QuestionBank

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

class UploadImage(viewsets.ViewSet):
    serializer_class = FileUploadSerializer

    def list(self, request):
        # Fetch all QuestionBank objects, ordered by created_at
        queryset = QuestionBank.objects.all().order_by('created_at')
        # Serialize the queryset using the QuestionBankSerializer
        serializer = QuestionBankSerializer(queryset, many=True)
        # Return the serialized data in the response
        return Response(serializer.data)
    
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            uploaded_question =  serializer.validated_data['question']
            uploaded_options =  serializer.validated_data['options']

            if not uploaded_question or not uploaded_options:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            # Process image files
            if uploaded_question.content_type.startswith("image/") and uploaded_options.content_type.startswith("image/"):
                question = uploaded_question.read()
                options = uploaded_options.read()
                question_base64= convertImgToBase64(question)
                options_base64= convertImgToBase64(options)

                # Convert file content to an image format easyOCR can process
                extracted_question = performOCR(question)
                 # Check if the function returned an error
                if isinstance(extracted_question, dict) and "error" in extracted_question:
                    return Response(extracted_question, status=status.HTTP_400_BAD_REQUEST)

                processed_question = processData(extracted_question, "question")
                if isinstance(processed_question, dict) and "error" in processed_question:
                    return Response(processed_question, status=status.HTTP_400_BAD_REQUEST)

                # Convert file content to an image format easyOCR can process
                extracted_options = performOCR(options)
                 # Check if the function returned an error
                if isinstance(extracted_options, dict) and "error" in extracted_options:
                    return Response(extracted_options, status=status.HTTP_400_BAD_REQUEST)

                processed_options = processData(extracted_options, "options")
                if isinstance(processed_options, dict) and "error" in processed_options:
                    return Response(processed_options, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)
            
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

class QuestionBankView(viewsets.ViewSet):
    serializer_class = QuestionBankSerializer

    def list(self, request):
        # Fetch all QuestionBank objects, ordered by created_at
        queryset = QuestionBank.objects.all().order_by('created_at')
        # Serialize the queryset using the QuestionBankSerializer
        serializer = QuestionBankSerializer(queryset, many=True)
        # Return the serialized data in the response
        return Response(serializer.data)
    
    def put(self, request, pk=None):
            try:
                # Retrieve the question by its primary key (id)
                question = QuestionBank.objects.get(pk=pk)
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

