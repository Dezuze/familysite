from django.db import models
from django.conf import settings


class Gallery(models.Model):
	image = models.ImageField(upload_to='gallery/')
	date = models.DateField(null=True, blank=True)
	description = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Gallery {self.id} - {self.date}"


class Committee(models.Model):
	# linked to a user (the 'other id' requested)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='committee_entries')
	pic = models.ImageField(upload_to='committee/')
	role = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Committee {self.id} - {self.user.username}"
