import uuid
from django.db import models

# Create your models here.
class QuestionBank(models.Model):
    question_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.JSONField()
    topic = models.JSONField(blank=True, null=True)
    difficulty = models.FloatField(blank=True, null=True)
    discrimation  = models.FloatField(blank=True, null=True)
    guessing  = models.FloatField(blank=True, null=True)
    school = models.CharField(max_length=255, blank=True, null=True)
    others = models.TextField(blank=True, null=True)
    question_image_base64 = models.TextField(blank=True, null=True)
    options_image_base64 = models.TextField(blank=True, null=True)
    question_file = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['topic','difficulty','school','active']),
        ]

    def __str__(self):
        return self.question  # Return first 50 characters of the question
    
class LabelOptions(models.Model):
    label_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type= models.CharField(max_length=255, db_index=True, blank=True, null=True)
    option=models.CharField(max_length=255, db_index=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self  # Return first 50 characters of the question
