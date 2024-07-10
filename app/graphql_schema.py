# Import necessary classes from graphene library
from graphene import ObjectType, String, Schema

# Import current_user from flask_login for user authentication
from flask_login import current_user

# Define a Query class that inherits from ObjectType
class Query(ObjectType):
    # Define a 'hello' field that returns a String
    # It takes an optional 'name' argument with a default value of "stranger"
    hello = String(name=String(default_value="stranger"))
    
    # Define a 'user' field that returns a String
    user = String()

    # Resolver function for the 'hello' field
    def resolve_hello(self, info, name):
        return f'Hello {name}!'

    # Resolver function for the 'user' field
    def resolve_user(self, info):
        # Check if the user is authenticated
        if current_user.is_authenticated:
            # If authenticated, return a greeting with the username
            return f'Hello {current_user.username}!'
        # If not authenticated, return a generic greeting
        return 'Hello Guest!'

# Create a Schema instance with the Query class
schema = Schema(query=Query)
