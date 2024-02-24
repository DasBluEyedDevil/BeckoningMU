from django.db import models

# Create your models here.
from evennia.accounts.models import AccountDB


class Bucket(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        AccountDB,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='created_buckets',
    )


class Job(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed')
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High')
    ]

    # Other fields
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=6, choices=STATUS_CHOICES, default='OPEN')
    completed = models.BooleanField(default=False)  # Add this line
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        AccountDB, on_delete=models.SET_NULL, null=True, related_name='jobs')
    creator = models.ForeignKey(AccountDB, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(
        AccountDB,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='assigned_jobs',
    )
    bucket = models.ForeignKey(
        Bucket, related_name='jobs', on_delete=models.CASCADE)
    priority = models.CharField(
        max_length=6, choices=PRIORITY_CHOICES, default='LOW')
    deadline = models.DateTimeField(null=True)
    resolved_at = models.DateTimeField(null=True)
    tags = models.ManyToManyField('Tag')
    players = models.ManyToManyField(
        AccountDB, null=True, related_name='related_jobs')


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    job = models.ForeignKey(Job, related_name='comments',
                            on_delete=models.CASCADE)
    author = models.ForeignKey(
        AccountDB, related_name='comments', on_delete=models.CASCADE)
    public = models.BooleanField(default=False)


class Tag(models.Model):
    name = models.CharField(max_length=200)
