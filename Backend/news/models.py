from django.db import models

class Post(models.Model):
    # 3. CONTENT & UPDATES (News/Events)
    POST_TYPES = (
        ('news', 'News'),
        ('event', 'Event'),
    )

    creator = models.ForeignKey('families.FamilyMember', on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=20, choices=POST_TYPES)
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    event_date = models.DateTimeField(null=True, blank=True) # Null if post_type is 'news'
    location = models.CharField(max_length=255, blank=True, null=True)
    is_kudumbayogam = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.post_type})"
    
    class Meta:
        ordering = ['-created_at']


class Media(models.Model):
    # 4. MEDIA GALLERY
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )
    
    uploader = models.ForeignKey('families.FamilyMember', on_delete=models.CASCADE, related_name='uploaded_media')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='media') # Linked if part of a news/event
    
    media_url = models.FileField(upload_to='media_gallery/') # using FileField to support videos too
    caption = models.CharField(max_length=255, blank=True, null=True)
    
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default='image')
    is_personal_gallery = models.BooleanField(default=False)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Media {self.id} ({self.media_type})"
