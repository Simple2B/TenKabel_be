from app import model as m


def check_location_notification(city: m.Location, user: m.User):
    if user.notification_locations_flag is False:
        return False
    return (city in user.notification_locations) or (
        not user.notification_locations and city in user.locations
    )


def check_profession_notification(profession: m.Profession, user: m.User):
    if user.notification_profession_flag is False:
        return False
    return (profession in user.notification_profession) or (
        not user.notification_profession and profession in user.professions
    )
