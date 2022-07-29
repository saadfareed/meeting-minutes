from django.shortcuts import render
from .utils import get_turn_info
from django.contrib import messages
from django.http.response import JsonResponse
from django.shortcuts import render
from .models import Record, RoomMember, TempRecord, RoomMemberMap, RoomMemberHistory, UserProfile
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
import wave
from datetime import datetime
import time
import os
from django.contrib.auth.decorators import login_required
import json
from django.contrib.auth.models import User
import pyaudio
import socket
import json
from pydub import AudioSegment
import math
import threading
from mysite.settings import EMAIL_HOST_USER

sampleRate = 44100.0
global_video_room_data = []

@login_required
@csrf_exempt
def fetch(request):
    global global_video_room_data
    if request.method == "POST":
        audio_file = request.FILES.get("video")
        language = request.POST.get("language")
        room_name = request.POST.get("roomname")
        user_name = request.POST.get("username")
        date = datetime.now().strftime('%d/%m/%Y')
        if len(global_video_room_data)!=0:
            for i in global_video_room_data:
                try:
                    if i['date']==date and i['room_name']==room_name:
                        i['record'].append(audio_file)
                        record = Record.objects.create(name_of_room = room_name)
                        record.save()
                        time.sleep(3)

                except:
                    print("at line 30")

        else:
            global_video_room_data.append({'date':date,'record':[audio_file],'room_name':room_name})
            record = Record.objects.create(voice_record=audio_file,name_of_room = room_name)
            record.save()
            time.sleep(3)

        return JsonResponse(
            {
                "url": "/fetch-data/",
                "success": True,
            }
        )
# @login_required
@csrf_exempt
def record(request):
    print("request.method 64",request.method)
    if request.method == "POST":
        date = datetime.now().strftime('%d/%m/%Y')
        audio_file = request.FILES.get("video")
        language = request.POST.get("language")
        room_name = request.POST.get("roomname")

        try:
            room = RoomMember.objects.get(room_name = room_name)
            if room.room_record_flag:
                rec = Record.objects.filter(name_of_room = room_name)

                record = Record.objects.create(language=language, voice_record=audio_file,name_of_room = room_name, record_number = len(rec)+1)
                record.save()
                fname = str(record.voice_record).split("/")[-1]
                with open(f'./temp_record/{fname}', 'wb+') as destination:
                    for chunk in audio_file.chunks():
                        destination.write(chunk)

                roomname = room_name
                room_data = RoomMember.objects.get(room_name = roomname)
                if room_data.room_members == 0 and room_data.room_record_flag==True:
                    print("roomname++++++++++++",type(roomname),roomname)
                    rec = Record.objects.filter(name_of_room = roomname)
                    final_record = None
                    record_list = []
                    print("rec at line 107",rec)
                    for i in rec:
                        record_list.append(str(i.voice_record).split("/")[-1])

                    if len(record_list)==0:
                        return
                    if len(record_list)==1:
                        ffmpeg_string = f"ffmpeg -i ./temp_record/{record_list[0]} -filter_complex amerge=inputs=1 -ac 1 ./room_recording/{roomname}_output.wav"
                        file = os.system(ffmpeg_string)
                    else:
                        ffmpeg_string = "ffmpeg -i "
                        count = 0
                        for i in record_list:
                            ffmpeg_string = ffmpeg_string + './temp_record/'+str(i)

                            count+=1
                            if len(record_list)>count:
                                ffmpeg_string = ffmpeg_string + ' -i '

                        ffmpeg_string = ffmpeg_string + f" -filter_complex amerge=inputs={count} -ac {count} ./room_recording/{roomname}_output.wav"

                        file = os.system(ffmpeg_string)

                        file_ = TempRecord.objects.create(voice_record = f'/room_recording/{roomname}_output.wav')
                        run_temp(roomname)
            else:
                print("host not started recording")
        except Exception as e:
            print("e at 99 ",e)
        return JsonResponse(
            {
                "url": "/join-room/",
                "success": True,
            }
        )
    context = get_turn_info()
    return render(request, "chat/peer.html", context)
@login_required
@csrf_exempt
def peer(request):
    # get numb turn info
    context = get_turn_info()
    print('context context context context: ', context)

    return render(request, 'chat/peer.html', context=context)
# @login_required
@csrf_exempt
def create_or_join(request):
    if request.method == "POST":
        try:
            roomname = request.POST.get("roomname")
            username = request.POST.get("username")
            try:
                if RoomMember.objects.get(room_name = roomname):
                    return render(request,'chat/index.html',{'error':f'Room Already Exists with name - '+roomname})
            except:
                pass
            room = RoomMember.objects.create(room_name = roomname,room_creater_name= username)
            room.save()
            return render(request,'chat/peer.html',{'roomname':roomname,'isCreater':True,'username':username})
        except:
            return render(request,'chat/peer.html',{'roomname':roomname,'isCreater':True,'username':username})
            pass


    return render(request,'chat/index.html')
# @login_required
@csrf_exempt
def record_verify(request):
    if request.method == "POST":
        room_name = request.POST.get("roomname")
        peeruser_name = request.POST.get("peerusername")
        user_name = request.POST.get("username")
        try:
            record = RoomMember.objects.get(room_name=str(room_name),room_record_flag=True,proxy_creater_name = user_name)
            res = JsonResponse(
                {
                    "url": "/record-verify/",
                    "success": True,
                }
            )
            return res
        except:
            return JsonResponse(
                {
                    "url": "/record-verify/",
                    "success": False,
                }
            )
    context = get_turn_info()
    return render(request, "chat/peer.html", context)

@login_required
@csrf_exempt
def temp_redirect(request):
    return render(request,'main.html',{'error':'Room Not Exists!'})

# @login_required
@csrf_exempt
def set_recording(request):
    if request.method == "POST":
        room_name = request.POST.get("roomname")
        user_name = request.POST.get("username")
        recording = request.POST.get("recording")
        recording = str(recording).split('\"')[0]
        try:
            record = RoomMember.objects.get(room_name=str(room_name), room_creater_name=user_name)
            if (recording=="false"):
                recording = False
            else:
                recording = True
            record.room_record_flag = recording
            record.save()
            res = JsonResponse(
                {
                    "url": "/set-recording/",
                    "success": True,
                }
            )
            print("res",res)
            return res
        except Exception as e:
            print("e at line 182",e)
            return JsonResponse(
                {
                    "url": "/set-recording/",
                    "success": False,
                }
            )
    context = get_turn_info()
    return render(request, "chat/peer.html", context)

@csrf_exempt
def view_participant(request):
    print("request.method 224",request.method)
    if request.method == "POST":
        room_name = request.POST.get("roomname")

        data = RoomMemberMap.objects.filter(roomname=room_name)

        result_list=[]
        room_creater_on_call = RoomMember.objects.get(room_name=room_name,room_creater_on_call=True)
        if room_creater_on_call:
            print("room_creater_on_call.room_creater_name",room_creater_on_call.room_creater_name)
            result_list.append({"username":room_creater_on_call.room_creater_name,"email":User.objects.get(username= room_creater_on_call.room_creater_name).email})
        for i in data:
            result_list.append({"username":i.room_member_name,"email":i.email})

        data = result_list
        res = JsonResponse(
                {
                    "url": "/set-recording/",
                    "success": True,
                    "data" : json.dumps(list(data))
                }
            )
        return res
    context = get_turn_info()
    return render(request, "chat/peer.html", context)



text_file_name_to_email = []
def background_process(filenames):
    global text_file_name_to_email
    print("inside background_process")
    CHUNK = 4096
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 4

    for filename in filenames:
        wf = wave.open(filename, 'rb')
        print("reading file is : ",filename)
        # instantiate PyAudio (1)
        p = pyaudio.PyAudio()
        RATE = wf.getframerate()
        # open stream (2)
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []
        #parameters for cle tech
        lang = "ur"
        token="30795ce7-73c9-4363-a3da-26ee18178e41"#write your access token here
        accessToken = token + "/" + lang
        host_ip="202.142.147.156"
        port=3000

        try:
            s = socket.socket()

            s.connect((host_ip, port))
            # print("socket connection made.")
            s.sendall(accessToken.encode('utf-8'))
            # print("send accessToken through socket")
            while True:
                # print("inside while loop")
                for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    # print("inside for loop")
                    data = stream.read(CHUNK)
                    # print("seding stream data via socket")
                    s.sendall(data)
                    # print("data send via socket")

                # print("outside for loop")
                try:
                    text_file_name = filename.split(".")[-2]+'.txt'
                    text_file_name = text_file_name.split("/")
                    text_file_name = "./text_files/"+text_file_name[2]

                    temp_file_name = filename.split(".")[-2]
                    room_name = filenames[0].split("_")[1:][1]


                    text_file_name_to_email = []
                    f = open(text_file_name,"w")

                    room_host = RoomMember.objects.get(room_name = room_name).room_creater_name
                    user_object = User.objects.get(username = room_host)
                    company_name = UserProfile.objects.get(user = user_object).company_name

                    msg = f"""Company Name : {company_name} \nDate : {datetime.now()} \nAttendees are as below : \n"""
                    current_date = datetime.now()

                    date_current = str(current_date.day)+"/"+str(current_date.month) +"/"+str(current_date.year)

                    attendees = RoomMemberHistory.objects.filter(roomname = room_name,date = date_current)

                    attendees_list = ",".join([str(i.room_member_name) for i in attendees])

                    msg = msg + " " +str(attendees_list)

                    f.write(msg)

                    f.close()
                    print(s.recv(2048).decode("utf-8"),"s.recv(2048).decode('utf-8')")
                    print("json data fetching")
                    json_obj=json.loads(s.recv(2048).decode("utf-8"))
                    # print(json_obj["text"])
                    # print(json_obj["final"])

                    with open(text_file_name,"a") as file:
                        file.write(str(json_obj["text"]))
                        text_file_name_to_email.append(text_file_name)
                        file = TempRecord.objects.create(voice_record = file)

                    if json_obj["final"] == 'true':
                        break
                except Exception as e:
                    print("Data not fetched from Audio to text script due to -> ",e)
                    pass
            send_email(text_file_name_to_email)

        except KeyboardInterrupt:
            pass


def run_temp(roomname):
    global spliteed_audio
    print("inside run_temp")
    folder = r'./room_recording'
    # file = 'test_output.wav'
    file = f'{roomname}_output.wav'
    print("spliting is start")
    split_wav = SplitWavAudioMubin(folder, file)
    print("spliting is initialized")
    split_wav.multiple_split(min_per_split=1)
    print("spliting is done")

    t = threading.Thread(target=background_process, args=[spliteed_audio], kwargs={})
    t.setDaemon(True)
    t.start()


spliteed_audio= []
class SplitWavAudioMubin():
    print("inside splitWavAudio")
    global spliteed_audio
    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.filepath = folder + '/' + filename

        self.audio = AudioSegment.from_wav(self.filepath)

    def get_duration(self):
        print("self.audio.duration_seconds",self.audio.duration_seconds)
        return self.audio.duration_seconds

    def single_split(self, from_min, to_min, split_filename):
        t1 = from_min * 60 * 1000
        t2 = to_min * 60 * 1000
        split_audio = self.audio[t1:t2]
        spliteed_audio.append(str(self.folder + '/' + split_filename))

        split_audio.export(self.folder + '/' + split_filename, format="wav")

    def multiple_split(self, min_per_split):
        total_mins = math.ceil(self.get_duration() / 30)
        for i in range(0, total_mins, min_per_split):
            split_fn = str(i) + '_' + self.filename
            self.single_split(i, i+min_per_split, split_fn)
            print(str(i) + ' Done')
            if i == total_mins - min_per_split:
                print('All splited successfully')
                print("spliteed_audio",spliteed_audio)


from email.mime.text import MIMEText
def send_email(filenames):
    print("filenames",filenames)
    room_name = filenames[0].split("_")[1:][0]

    file_path = os.path.abspath('media/bg-2.jpg')

    subject = f'Minutes Of Meeting with Roomname : {room_name}'

    room_host = RoomMember.objects.get(room_name = room_name).room_creater_name
    user_object = User.objects.get(username = room_host)
    company_name = UserProfile.objects.get(user = user_object).company_name

    msg = f"""Company Name : {company_name} <br>
    Date : {datetime.now()} <br>
    Attendees are as below : <br>
    """


    current_date = datetime.now()

    date_current = str(current_date.day)+"/"+str(current_date.month) +"/"+str(current_date.year)

    attendees = RoomMemberHistory.objects.filter(roomname = room_name,date = date_current)
    # to_email = [i.email for i in attendees]

    attendees_list = ",".join([str(i.room_member_name) for i in attendees])

    msg = msg + " " +str(attendees_list)

    #to send email of summary to meeting host only
    room_host = RoomMember.objects.get(room_name = room_name).room_creater_name
    user_object = User.objects.get(username = room_host).email
    to_email1 = [user_object]


    from_email = EMAIL_HOST_USER
    mail = EmailMessage(
        subject,
        msg,
        from_email,
        to_email1,
    )

    mail.content_subtype='html'
    # print("filenames",filenames)
    for j in filenames:
        mail.attach_file('./text_files/'+j)

    email_res = mail.send()

    print("email_res at line 419",email_res)

#To check email functionality
# send_email(["0_test_output.txt"])

#To check socket code Threading process
# run_temp('test')
