from json import loads

from app import mem_cache


def generate_room_name(*args):
    return ''.join(sorted(args))


def serialize_msg(obj):
    return {
        'msg': obj.msg,
        'datetime': str(obj.datetime),
        'sender': obj.sender.username,
        'receiver': obj.receiver.username
    }


def serialize_cache(key):
    data = mem_cache.get(key, b'{}')
    return loads(data.decode().replace("'", '"'))
