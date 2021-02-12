#!usr/bin/python3
import json


# used by makefile
print('Starting setup')

env ="""postgresql=
default_prefix=~
token=
dev-mode=
webhook-url="""

with open('src/.env', 'w') as tf:
    tf.write(env)

static_config = {
    "blacklisted-users": [],
    "blacklisted-guilds": []
}

with open('src/static-config.json', 'w') as cf:
    json.dump(static_config, cf, indent=4)

print('Completed setup.')
