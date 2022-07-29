from django.urls import re_path
# from .views import peer1, peer2, peer
from .views import peer, record, create_or_join,temp_redirect, fetch, record_verify, set_recording,view_participant

urlpatterns = [
    re_path('join-room/', record, name='peer'),
    re_path('dashboard/', create_or_join, name='create_or_join'),
    re_path('not-able-to-join/', temp_redirect, name='temp_redirect'),
    re_path('fetch-data/', fetch, name='fetch'),
    re_path('record-verify/', record_verify, name='record_verify'),
    re_path('set-recording/', set_recording, name='set_recording'),
    re_path('view-participant/', view_participant, name='view_participant'),


]
