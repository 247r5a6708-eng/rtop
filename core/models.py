import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver


class ActivityLog(models.Model):
    """One row per user per day an action was taken - powers the git-style calendar heatmap."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    date = models.DateField()
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.count})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    theme = models.CharField(max_length=10, choices=[('dark', 'Dark'), ('light', 'Light')], default='dark')
    is_pirate_king = models.BooleanField(default=False)
    crowned_at = models.DateTimeField(null=True, blank=True)
    bio = models.CharField(max_length=200, blank=True, default="A rookie pirate setting sail.")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    coins = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profile({self.user.username})"


@receiver(pre_save, sender=Profile)
def delete_old_avatar_on_change(sender, instance, **kwargs):
    """
    Whenever a Profile is saved with a NEW avatar (or the avatar is cleared),
    delete the previously-stored image file from disk so old avatars never
    pile up in /media/avatars/.
    """
    if not instance.pk:
        return  # new profile, nothing to clean up yet
    try:
        old = Profile.objects.get(pk=instance.pk)
    except Profile.DoesNotExist:
        return
    old_avatar = old.avatar
    new_avatar = instance.avatar
    if old_avatar and old_avatar != new_avatar:
        old_avatar.storage.delete(old_avatar.name)


# ---------------------------------------------------------------------------
# Quote of the Day — One Piece quotes shown on the Dashboard, Attack on Titan
# quotes shown on the Nakama / Profile crew page. One new quote per day,
# picked sequentially (in id order, wrapping around) — never random/shuffled.
# ---------------------------------------------------------------------------
class Quote(models.Model):
    ONE_PIECE = 'OP'
    ATTACK_ON_TITAN = 'AOT'
    SERIES = [(ONE_PIECE, 'One Piece'), (ATTACK_ON_TITAN, 'Attack on Titan')]

    series = models.CharField(max_length=3, choices=SERIES)
    text = models.CharField(max_length=300)
    speaker = models.CharField(max_length=80, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['series', 'order', 'id']

    def __str__(self):
        return f"[{self.series}] {self.text[:40]}"


# ---------------------------------------------------------------------------
# One Piece themed milestone badges — one is unlocked every 50 active days.
# ---------------------------------------------------------------------------
ONE_PIECE_MILESTONES = [
    (50, "East Blue Rookie", "Set sail with Luffy and left East Blue behind."),
    (100, "Alabasta Ally", "Helped Vivi save the Kingdom of Alabasta."),
    (150, "Skypiea Voyager", "Rode the Knock Up Stream into the sky."),
    (200, "Water Seven Shipwright", "Rebuilt your resolve at Water Seven."),
    (250, "Thriller Bark Survivor", "Escaped Gecko Moria's shadow army."),
    (300, "Sabaody Veteran", "Survived the Sabaody Archipelago and the timeskip."),
    (350, "Fish-Man Island Diver", "Dove 10,000 meters to Fish-Man Island."),
    (400, "Dressrosa Liberator", "Freed Dressrosa from Doflamingo's strings."),
    (450, "Whole Cake Escapee", "Escaped Big Mom's Whole Cake Island."),
    (500, "Wano Warrior", "Fought in the raid on Onigashima in Wano."),
]


class Badge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    milestone = models.PositiveIntegerField()
    title = models.CharField(max_length=120)
    description = models.CharField(max_length=200, blank=True)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'milestone')
        ordering = ['milestone']

    def __str__(self):
        return f"{self.user.username} - {self.title} (Day {self.milestone})"
