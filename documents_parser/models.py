from django.db import models
from django.contrib.auth.models import User
import uuid
from accounts.models import CustomUser


class ExtractedData(models.Model):
    MATCH_TYPE_CHOICES = [
        ('exact', 'Exact Match'),
        ('partial', 'Partial Match'),
    ]

    search_id = models.UUIDField(default=uuid.uuid4, editable=False)  # Unique ID for each search operation
    source_file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)
    tag_searched = models.CharField(max_length=255)
    block_record = models.TextField()
    location_of_tag = models.CharField(max_length=255)
    date_of_search = models.DateTimeField(auto_now_add=True)  
    search_author = models.CharField(max_length=255)  # Changed to CharField temporarily
    search_author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Link to User table
    match_type = models.CharField(max_length=10, choices=MATCH_TYPE_CHOICES)  # New field for match type
    other = models.CharField(max_length=255, blank=True)
    line_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.search_id} - {self.source_file_name} - {self.tag_searched} ({self.match_type} - {self.date_of_search} - {self.search_author})"

    def save(self, *args, **kwargs):
        if not self.line_id:
            # Generate a unique line ID (e.g., UUID or any unique identifier)
            self.line_id = f"{self.pk}_{self.source_file_name}_{self.tag_searched[:10]}"
        super(ExtractedData, self).save(*args, **kwargs)

     