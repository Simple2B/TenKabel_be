# flake8: noqa F401
from .user import User
from .profession import Profession
from .superuser import SuperUser

from .jobs import Job
from .applications import Application

from .rate import Rate
from .location import Location
from .user_profession import UserProfession
from .user_location import UserLocation
from .user_notifications_professions import UserNotificationsProfessions
from .user_notifications_location import UserNotificationLocation
from .device import Device

from .notification import Notification
from .platform_comission import PlatformCommission
from .platform_payment import PlatformPayment

from app.database import db
