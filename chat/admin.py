from django.contrib import admin

from .models import Record,RoomMember,RoomMemberMap, TempRecord,UserProfile,RoomMemberHistory

# admin.site.register(UserProfile)

@admin.register(RoomMemberHistory)
class RoomMemberHistoryAdmin(admin.ModelAdmin):
    list_display = ("roomname","room_member_name","date","email","company_name")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user","contact_number","company_name")
@admin.register(TempRecord)
class TempRecordAdmin(admin.ModelAdmin):
    list_display = ("voice_record",)

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ("id", "language", "voice_record","name_of_room","record_number")

@admin.register(RoomMember)
class RoomAdmin(admin.ModelAdmin):
    list_display = ( "room_name",
                    "room_creater_name",    
                    "room_members",
                    "room_record_flag",
                    "room_creater_on_call",
                    "room_creater_channel",
                    "proxy_creater_name",
                    "proxy_creater_channel"
                    )

@admin.register(RoomMemberMap)
class RoomMemberMapAdmin(admin.ModelAdmin):
    list_display = ("roomname","room_member_name","user_channel","email")

