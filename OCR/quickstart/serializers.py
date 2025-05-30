from django.contrib.auth.models import Group, User
from rest_framework import serializers
from .models import QuestionBank, LabelOptions


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class QuestionBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = '__all__'  # Serialize all fields of the model

class LabelOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabelOptions
        fields = '__all__'  # Serialize all fields of the model

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=False, allow_null=True)

class ImageUploadSerializer(serializers.Serializer):
    question = serializers.FileField(required=False, allow_null=True)
    options = serializers.FileField(required=False, allow_null=True)
