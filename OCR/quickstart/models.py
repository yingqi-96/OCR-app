import uuid
from django.db import models

# Create your models here.
class QuestionBank(models.Model):
    question_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.JSONField()
    topic = models.CharField(max_length=255, db_index=True)
    difficulty = models.PositiveSmallIntegerField()
    school = models.CharField(max_length=255, blank=True, null=True)
    others = models.TextField(blank=True, null=True)
    question_image_base64 = models.TextField(blank=True, null=True)
    options_image_base64 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['topic','difficulty', 'school']),
        ]

    def __str__(self):
        return self.question  # Return first 50 characters of the question