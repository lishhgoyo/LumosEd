from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    badges = models.ManyToManyField('Badge', blank=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", default="default.jpg")
    last_active = models.DateField(null=True, blank=True)
    streak = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def add_xp(self, points):
        self.xp += points
        self.level = self.xp // 100 + 1  # Level up for every 100 XP
        self.save()
        
    def update_streak(self):
        today = now().date()
        if self.last_active:
            if self.last_active == today - timedelta(days=1):
                self.streak += 1  # Continue streak
            elif self.last_active < today - timedelta(days=1):
                self.streak = 0  # Streak resets
        else:
            self.streak = 1  # First day

        self.last_active = today
        self.save()

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/', null=True, blank=True)

    def __str__(self):
        return self.name
    
class Reward(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    required_xp = models.IntegerField()

    def __str__(self):
        return self.name
    
class LearningActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)  # Quiz scores or performance points

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    level = models.CharField(max_length=50, choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')])



