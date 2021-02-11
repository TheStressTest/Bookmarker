import json

print('Starting setup')

env = """
postgresql=
default_prefix=~
token=
dev-mode=
webhook-url=
"""

with open('src/.env', 'w') as tf:
    tf.write(env)