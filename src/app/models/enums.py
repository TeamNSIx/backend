from enum import Enum


class UserRole(str, Enum):
    admin = 'admin'
    user = 'user'
    moderator = 'moderator'


class MessageSender(str, Enum):
    user = 'user'
    bot = 'bot'
    system = 'system'


class SourceType(str, Enum):
    website = 'website'
    document = 'document'
    api = 'api'
