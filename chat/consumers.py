import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import redirect
import asyncio
from .models import RoomMember, RoomMemberMap, Record, TempRecord, RoomMemberHistory, UserProfile
from asgiref.sync import sync_to_async
from django.http.response import JsonResponse
from django.contrib.auth.models import User

@sync_to_async
def update_room_details(roomname,username,channel):
    try:
        room_data = RoomMember.objects.get(room_name = roomname,room_creater_name = username)
        room_data.room_members = int(room_data.room_members) + 1
        room_data.room_creater_on_call = True
        room_data.room_creater_channel = str(channel)
        room_data.save()
    except:
        print("user is not creator")
        try:
            user_email = User.objects.get(username = username).email
            print("user_email at line 22",user_email)
            try:
                res = RoomMemberMap.objects.get(roomname = roomname,room_member_name=username,user_channel = channel,email = user_email)
            except:
                res = RoomMemberMap.objects.create(roomname = roomname,room_member_name=username, user_channel = channel,email = user_email)
                res.save()
                res = RoomMemberMap.objects.filter(roomname = roomname)
                if len(res)==1:
                    room_data = RoomMember.objects.get(room_name = roomname)
                    room_data.proxy_creater_name = username
                    room_data.proxy_creater_channel = channel
                    room_data.save()
                else:
                    pass
        except:
            print("user already joined the meeting!")
        
    print("Room data updated successfully")

@sync_to_async
def disconnect_update_room_details(roomname,username,channel):
    try:
        room_data = RoomMember.objects.get(room_name = roomname,room_creater_name = username)
        room_data.room_members = int(room_data.room_members) - 1
        room_data.room_creater_on_call = False
        room_data.room_creater_channel = None
        room_data.save()
        RoomMemberHistory.objects.create(roomname = roomname,room_member_name=username, email = User.objects.get(username = username).email,company_name=UserProfile.objects.get(user = User.objects.get(username = username)).company_name)
    except:
        try:
            res = RoomMemberMap.objects.get(roomname = roomname,room_member_name=username)
            RoomMemberHistory.objects.create(roomname = roomname,room_member_name=username, email = res.email,company_name=UserProfile.objects.get(user = User.objects.get(username = username)).company_name )
            res.delete()
            try:
                res = RoomMemberMap.objects.filter(roomname = roomname)[0]
                room_data = RoomMember.objects.get(room_name = roomname)
                room_data.room_members = int(room_data.room_members) - 1
                room_data.proxy_creater_name = res.room_member_name
                room_data.proxy_creater_channel = res.user_channel
                room_data.save()
                
            except:
                room_data = RoomMember.objects.get(room_name = roomname)
                room_data.room_members = int(room_data.room_members) - 1
                room_data.proxy_creater_name = None
                room_data.proxy_creater_channel = None
                room_data.save()
                
        except Exception as e:
            room_data = RoomMember.objects.get(room_name = roomname)
            room_data.room_members = int(room_data.room_members) - 1
            room_data.save()

            

@sync_to_async
def get_all_rooms(roomname,username):
    try:
        d = RoomMember.objects.get(room_name = roomname)
        
        try:
            data = RoomMember.objects.get(room_name = roomname,room_creater_name=username)
            return 'isCreator'
        except:
            return True
        return True
    except:
        return JsonResponse(
            {
                "message": "room name not exists"
            }
        )

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self): 
        await self.accept()
        

    async def disconnect(self, close_code):
        await disconnect_update_room_details(self.room_group_name,self.username_disconnect,self.channel_name)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        print('Disconnected!')
        

    # Receive message from WebSocket
    async def receive(self, text_data):
        receive_dict = json.loads(text_data)
        print("receive_dict",receive_dict)
        peer_username = receive_dict['peer']
        self.username_disconnect = receive_dict['peer']
        action = receive_dict['action']
        message = receive_dict['message']
        try:
            roomname = receive_dict['roomname']
            self.room_group_name =roomname
        except:
            roomname = ""
            print("roomname not found")

        await update_room_details(roomname,peer_username,self.channel_name)
        
        await self.channel_layer.group_add(
            roomname,
            self.channel_name
        )
        if(action == 'new-offer') or (action =='new-answer'):
            # in case its a new offer or answer
            # send it to the new peer or initial offerer respectively

            receiver_channel_name = receive_dict['message']['receiver_channel_name']

            # set new receiver as the current sender
            receive_dict['message']['receiver_channel_name'] = self.channel_name

            await self.channel_layer.send(
                receiver_channel_name,
                {
                    'type': 'send.sdp',
                    'receive_dict': receive_dict,
                }
            )

            return

        # set new receiver as the current sender
        # so that some messages can be sent
        # to this channel specifically
        receive_dict['message']['receiver_channel_name'] = self.channel_name

        # send to all peers
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send.sdp',
                'receive_dict': receive_dict,
            }
        )

    async def send_sdp(self, event):
        receive_dict = event['receive_dict']

        this_peer = receive_dict['peer']
        action = receive_dict['action']
        message = receive_dict['message']
        
        roomname = self.room_group_name
        
        data = await get_all_rooms(roomname,this_peer)
        
        if data==True:
            res = {
            'peer': this_peer,
            'action': action,
            'message': message,
            }
        elif data=='isCreator':
            message['isCreator'] = True
            res = {
            'peer': this_peer,
            'action': action,
            'message': message,
            }
        else:
            message['error'] = True
            res = {
            'peer': this_peer,
            'action': action,
            'message': message,
            }
            
        await self.send(text_data=json.dumps(res))