import json
from json import JSONDecodeError


def toList( result ):
    try:
        dumped = json.loads( result )
    except JSONDecodeError:
        return []
    return list( dumped.items() )



