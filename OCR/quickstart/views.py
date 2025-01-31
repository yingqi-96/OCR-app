from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from rest_framework import status
from rest_framework.response import Response

from .serializers import GroupSerializer, UserSerializer, FileUploadSerializer 
from .utils import performOCR, processData

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
        return Response("GET API")

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            uploaded_file =  serializer.validated_data['file']
            type = serializer.validated_data['type']

            if not uploaded_file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            
            file_content = uploaded_file.read()

            # Process image files
            if uploaded_file.content_type.startswith("image/"):
                # Convert file content to an image format easyOCR can process
                extracted_text = performOCR(file_content)
                print(extracted_text)
                processed_text = processData(extracted_text, type)

            else:
                return Response({"error": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)

        # Return structured JSON response
        return Response({
            "extracted_text": extracted_text,
            "processed_text": processed_text
        }, status=status.HTTP_200_OK)


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

