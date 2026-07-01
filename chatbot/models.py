import uuid
from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        user_label = self.user.email if self.user else 'Anonymous'
        return f'Chat - {user_label} ({self.created_at:%Y-%m-%d %H:%M})'


class ChatMessage(models.Model):
    ROLES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    legacy_session_id = models.CharField(max_length=255, blank=True, help_text='Backward compatibility for old messages')
    role = models.CharField(max_length=10, choices=ROLES, default='user')
    message = models.TextField()
    response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.message[:50]}'
