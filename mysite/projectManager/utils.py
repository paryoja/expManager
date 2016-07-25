import json
from json import JSONDecodeError


def toList( result ):
    try:
        dumped = json.loads( result )
    except JSONDecodeError:
        return []
    return list( dumped.items() )


def toDictionary( result ):
    try:
        dumped = json.loads( result )
    except JSONDecodeError:
        return {}
    return dumped
