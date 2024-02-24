from django.db import models
from evennia.accounts.models import AccountDB


class WikiPage(models.Model):
    title = models.CharField(max_length=200, unique=True)
    content = models.TextField()
    created_by = models.ForeignKey(
        AccountDB, related_name='wiki_page_created_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WikiPageVersion(models.Model):
    wiki_page = models.ForeignKey(
        WikiPage, related_name='wiki_page_version', on_delete=models.CASCADE)
    content = models.TextField()
    created_by = models.ForeignKey(
        AccountDB, related_name='wiki_page_version_created_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
