import base64


def get_default_avatar() -> str:
    with open("app/utility/default_user_picture.png", "rb") as f:
        byte_data = f.read()
        picture = base64.b64encode(byte_data).decode("utf-8")
    return picture
