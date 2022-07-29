import uuid
from cloudinary_storage.storage import RawMediaCloudinaryStorage
from django.db import models
from django.urls.base import reverse
from django.contrib.auth.models import User
from datetime import datetime

class TempRecord(models.Model):
    voice_record = models.FileField(
        upload_to="records", storage=RawMediaCloudinaryStorage())

class Record(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voice_record = models.FileField(
        upload_to="records", storage=RawMediaCloudinaryStorage())
    language = models.CharField(max_length=50, null=True, blank=True)
    name_of_room = models.CharField(max_length=200, default=None,null=True,blank=True)
    record_number = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Record"
        verbose_name_plural = "Records"

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse("core:record_detail", kwargs={"id": str(self.id)})

class RoomMember(models.Model):
    room_name = models.CharField(max_length=200)
    room_creater_name = models.CharField(max_length=1000,null=True, blank=True, default=None)
    room_members = models.IntegerField(default=0)
    room_record_flag = models.BooleanField(default=False,null=True, blank=True)
    room_creater_on_call = models.BooleanField(default=False,null=True, blank=True)
    room_creater_channel = models.CharField(max_length=200,null=True, blank=True,default= None)
    proxy_creater_name = models.CharField(max_length=1000,null=True, blank=True, default=None)
    proxy_creater_channel = models.CharField(max_length=200,null=True, blank=True,default= None)

    def __str__(self):
        return str(self.room_name)

class RoomMemberMap(models.Model):
    roomname = models.CharField(max_length=200, default=None,null=True,blank=True)
    room_member_name = models.CharField(max_length=1000,null=True, blank=True, default=None)
    user_channel = models.CharField(max_length=200,null=True, blank=True,default= None)
    email = models.CharField(max_length=500,null=True, blank=True,default= None)

    def __str__(self):
        return str(self.roomname)

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(blank=True, null=True, max_length=10)
    company_name = models.CharField(blank=True, null=True, max_length=255)

    def __str__(self):
        return self.user.username

class RoomMemberHistory(models.Model):
    roomname = models.CharField(max_length=200, default=None,null=True,blank=True)
    room_member_name = models.CharField(max_length=1000,null=True, blank=True, default=None)
    email = models.CharField(max_length=500,null=True, blank=True,default= None)
    company_name = models.CharField(blank=True, null=True, max_length=255)
    current_date = datetime.now()
    date_current = str(current_date.day)+"/"+str(current_date.month) +"/"+str(current_date.year)
    date = models.CharField(default=date_current,max_length=50)

    def __str__(self):
        return str(self.roomname)