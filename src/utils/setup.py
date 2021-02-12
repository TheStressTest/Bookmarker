if __name__ == '__main__':
    print('Refrain from running this file directly, instead use the command: make')
    exit(1)
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