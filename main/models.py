from django.db import models


class Suggestion(models.Model):
    text = models.TextField()
    author = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.author}: {self.text[:30]}"


class Curator(models.Model):
    CURATOR_TYPES = (
        ("government", "Government"),
        ("criminal", "Criminal"),
    )

    discord_id = models.BigIntegerField(unique=True)

    discord_username = models.CharField(
        max_length=64, null=True, blank=True
    )

    server_nickname = models.CharField(
        max_length=64, null=True, blank=True
    )

    curator_types = models.JSONField(default=list)

    factions = models.JSONField(default=list)
    online = models.BooleanField(default=False)

    messages = models.IntegerField(default=0)
    replies = models.IntegerField(default=0)
    reactions = models.IntegerField(default=0)
    voice_minutes = models.IntegerField(default=0)

    score = models.IntegerField(default=0)

    def __str__(self):
        return (
            self.server_nickname
            or self.discord_username
            or f"Curator {self.discord_id}"
        )

    @property
    def voice_hours(self):
        return round(self.voice_minutes / 60, 1)

    @property
    def progress_percent(self):
        return min(100, max(3, int(self.score / 2)))

    @property
    def progress_color(self):
        s = self.score
        if s < 79: return "red"
        if s < 100: return "orange"
        if s < 159: return "yellow"
        if s < 200: return "blue"
        if s < 279: return "darkblue"
        return "purple"

class Server(models.Model):
    discord_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=128)
    icon = models.CharField(max_length=256, null=True, blank=True)
    owner_id = models.BigIntegerField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    backup_in_progress = models.BooleanField(default=False)
    restoring = models.BooleanField(default=False)
    restore_finished_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.discord_id})"

class Backup(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="backups")
    backup_id = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
  