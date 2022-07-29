# from django.db import models
# from django.contrib.auth.models import User

# class UserProfile(models.Model):
# 	user = models.OneToOneField(User, on_delete=models.CASCADE)
# 	contact_number = models.CharField(blank=True, null=True, max_length=10)
# 	company_name = models.CharField(blank=True, null=True, max_length=255)

# 	def __str__(self):
# 	    return self.user.username


# from PIL import Image
# from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager


# # class Users(AbstractUser):
	# contact_number = models.CharField(blank=True, null=True, max_length=10)
	# company_name = models.CharField(blank=True, null=True, max_length=255)

# # class User(PermissionsMixin, AbstractBaseUser):
# #     username = models.CharField(max_length=32, unique=True, )
# #     email = models.EmailField(max_length=32)
# #     # gender_choices = [("M", "Male"), ("F", "Female"), ("O", "Others")]
# #     # gender = models.CharField(choices=gender_choices, default="M", max_length=1)
# #     nickname = models.CharField(max_length=32, blank=True, null=True)

# #     is_active = models.BooleanField(default=True)
# #     is_staff = models.BooleanField(default=False)
# #     # REQUIRED_FIELDS = ["email", "gender"]
# #     USERNAME_FIELD = "username"
# #     objects = User_manager()

# #     def __str__(self):
# #         return self.username


# # Extending User Model Using a One-To-One Link

