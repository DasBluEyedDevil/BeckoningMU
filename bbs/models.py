from django.db import models
from django.db.models import Max
from evennia.accounts.models import AccountDB


class Board(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    read_perm = models.CharField(
        max_length=200, default='all', help_text="Permission required to read this board.")
    write_perm = models.CharField(
        max_length=200, default='all', help_text="Permission required to post to this board.")

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(AccountDB, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sequence_number = models.IntegerField(default=0)  # Add this line for the sequence number
    read_perm = models.CharField(max_length=200, default='all', help_text="Permission required to read this post.")
    write_perm = models.CharField(max_length=200, default='all', help_text="Permission required to comment on this post.")

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if this is a new post
            # Calculate the next sequence number
            current_max_sequence = Post.objects.filter(board=self.board).aggregate(Max('sequence_number'))['sequence_number__max'] or 0
            self.sequence_number = current_max_sequence + 1
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    author = models.ForeignKey(AccountDB, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, related_name='comments', on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_perm = models.CharField(
        max_length=200, default='all', help_text="Permission required to read this comment.")
    write_perm = models.CharField(max_length=200, default='all',
                                  help_text="Permission required to comment on this comment.")

    def __str__(self):
        return 'Comment by {} on {}'.format(self.author, self.post)
