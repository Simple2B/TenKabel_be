import base64


def get_default_avatar():
    with open("app/utility/default_user_picture.png", "rb") as f:
        picture = base64.b64encode(f.read())

    return picture
