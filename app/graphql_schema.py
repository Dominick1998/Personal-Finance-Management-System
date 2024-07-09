from graphene import ObjectType, String, Schema
from flask_login import current_user

class Query(ObjectType):
    hello = String(name=String(default_value="stranger"))
    user = String()

    def resolve_hello(self, info, name):
        return f'Hello {name}!'

    def resolve_user(self, info):
        if current_user.is_authenticated:
            return f'Hello {current_user.username}!'
        return 'Hello Guest!'

schema = Schema(query=Query)
