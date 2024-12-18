from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_job_profile(sender, instance, created, **kwargs):
    if created:
        JobProfile.objects.create(user=instance)

class JobProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_profile')
    service_offered = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    service_description = models.TextField()
    institution_name = models.CharField(max_length=255, null=True, blank=True)
    certification = models.CharField(max_length=255, null=True, blank=True)
    document = models.FileField(upload_to='documents/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Job Profile"


class Job(models.Model):
    job_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs")
    job_name = models.CharField(max_length=255)
    job_description = models.TextField()
    location = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)  # New field for admin approval
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Job {self.job_id}: {self.job_name}"


    class Meta:
        verbose_name = "Job"
        verbose_name_plural = "Jobs"
        ordering = ['-time_created']

    def get_applicants(self):
        """Fetch all applicants for this job."""
        return self.applications.all()
 
        
class JobApplication(models.Model):
    """Model for Job Application."""

    # Fields
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    approved = models.BooleanField(null=True)  # True for Approved, False for Rejected, None for Pending
    status = models.CharField(max_length=20, default="Pending")  # New field for explicit status
    applied_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Application by {self.user.username} for {self.job.job_name}"

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        ordering = ['-applied_at']
        
        
###################### JOB APPROVAL ##################

class JobApproved(models.Model):
    """Model to track the approval of job applications and payment details."""
    
    application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, related_name='approved_job')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_status = models.BooleanField(default=False)
    time_approved = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Job Approved: {self.application.job.job_name} - {self.application.user.username}"

    class Meta:
        verbose_name = "Job Approval"
        verbose_name_plural = "Job Approvals"
        ordering = ['-time_approved']  
        

