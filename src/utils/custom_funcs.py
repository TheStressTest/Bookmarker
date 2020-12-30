from src.utils.errors import InvalidTimeFormat


async def trim_message(message, length: int = 12):
    if len(message) <= length:
        return message
    else:
        return f'{message[:length]}...'


async def time_convert(time):
    if time[-1:].lower() == 's':
        formatted_time = int(time[:-1])
    elif time[-1:].lower() == 'm':
        formatted_time = int(time[:-1]) * 60
    elif time[-1:].lower() == 'h':
        formatted_time = int(time[:-1]) * 3600
    elif time[-1:].lower() == 'd':
        formatted_time = int(time[:-1]) * 86400
    elif time[-1:].lower() == 'w':
        formatted_time = int(time[:-1]) * 604800
    else:
        raise InvalidTimeFormat
    return int(formatted_time)
