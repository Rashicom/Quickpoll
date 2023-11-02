from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
# overriding usermanager
class CustomUserManager(BaseUserManager):

    # overriding user based authentication methord to email base authentiction
    def _create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError("The given mail must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)


    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


# custom customer for user 
# extrafields are added to by inheriting the django user
class CustomUser(AbstractUser):

    # field doesnot needed
    username = None
    last_name = None

    # extra fields
    email = models.EmailField(unique=True)
    profile_photo = models.ImageField(upload_to="Profile_photos", null=True, blank=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


# polls
class Polls(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    poll_id = models.AutoField(primary_key=True)
    poll_question = models.TextField()
    published_on = models.DateField(auto_now=True)
    close_on = models.DateField()
    total_vote_count = models.IntegerField(default=0)


# table for choices
# polls can have multiple choices
class PollChoices(models.Model):
    poll_id = models.ForeignKey(Polls,related_name="poll_choice_set" , on_delete=models.CASCADE)

    pollchoice_id = models.AutoField(primary_key=True)
    choice_discription = models.TextField()
    vote_count = models.IntegerField(default=0)


# voting list
# choices can have multiple votings
# pols can have multiple votings
class VotingList(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    poll_id = models.ForeignKey(Polls,related_name="voted_list" , on_delete=models.CASCADE)
    pollchoice_id = models.ForeignKey(PollChoices, related_name="voted_list", on_delete=models.CASCADE)

    vote_id = models.AutoField(primary_key=True)

    # Enforcing that, user cannot vote multiple choices of a single poll
    # Enforcing that, user cannot vote multiple times for the same poll
    class Meta:
        unique_together = ["user","poll_id"]
    
    