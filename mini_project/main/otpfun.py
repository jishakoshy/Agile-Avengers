from twilio.rest import Client
import pyotp
from datetime import datetime, timedelta
from django.contrib import messages

def sent_otp(request):
    totp = pyotp.TOTP(pyotp.random_base32(), interval=60)
    otp = totp.now()
    request.session['otp_secret_key'] = totp.secret
    valid_date = datetime.now() + timedelta(minutes=1)
    request.session['otp_valid_date'] = str(valid_date)
    account_sid = 'AC93906130cf2f8039f4f9dad613d46c6c'
    auth_token = 'a74da085fccc375d7d70069061f9327b'
    client = Client(account_sid, auth_token)
    from_number = '+16562186679'
    to_number = '+919061731669'
    try:
        print("SEnding otp")
        message = client.messages.create(
            body=f"Your OTP is: {otp}",
            from_=from_number,
            to=to_number
        )
        print(message)
        print('OTP sent successfully')
        return True
    except Exception as e:
        print(f'Error sending OTP: {str(e)}')
        messages.error(request, 'Error sending OTP')
        return False