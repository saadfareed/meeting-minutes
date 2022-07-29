from django.conf import settings

# returns numb turn credential and username
def get_turn_info():

    print("settings.NUMB_TURN_CREDENTIAL",settings.NUMB_TURN_CREDENTIAL)
    print("settings.NUMB_TURN_USERNAME",settings.NUMB_TURN_USERNAME)
    return {
        'numb_turn_credential': settings.NUMB_TURN_CREDENTIAL,
        'numb_turn_username': settings.NUMB_TURN_USERNAME,
    }