import pyotp

def gen_otp(secret_key):
    try:
        otp_code = pyotp.TOTP(secret_key).now()
        return otp_code
    except Exception as e:
        print("fatal: ", e)