from django.db import models
from django.contrib.auth.models import User





class PilotProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    license_date = models.DateField(blank=True, null=True)
    license_image = models.ImageField(upload_to='licenses/', blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()



class TrainingRecord(models.Model):
    pilot = models.ForeignKey(PilotProfile, on_delete=models.CASCADE, related_name='trainings')
    training_name = models.CharField(max_length=200)
    date_completed = models.DateField()
    location = models.CharField(max_length=100, default='Online')
    certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    is_annual = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.training_name} on {self.date_completed}"
    
    class Meta:
        ordering = ['-date_completed']

