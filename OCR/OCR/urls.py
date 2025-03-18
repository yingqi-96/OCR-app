"""
URL configuration for OCR project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from rest_framework import routers
from tutorial.quickstart import views
from quickstart.views import QuestionBankView, LabelOptionsView, UploadPDFView, UploadImageView, UploadImageAndProcessWithEasyOCR, ProcessData

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'question-bank', QuestionBankView, basename="question-bank")
router.register(r'label-options', LabelOptionsView, basename="label-options")
router.register(r'upload-pdf', UploadPDFView, basename="upload-pdf")
# router.register(r'upload-image', UploadImageView, basename="upload-image")
router.register(r'upload-and-process-with-easyOCR', UploadImageAndProcessWithEasyOCR, basename="upload-and-process-with-easyOCR")
router.register(r'upload-and-process-with-LLM', ProcessData, basename="upload-and-process-with-LLM")


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]