import json

def formJson(code, *args):
    if code == "usr":
        return json.dumps({'code' : code, 'from' : args[0], 'text' : args[1]})
    elif code == "srv":
        return json.dumps({'code' : code, 'text' : args[0]})
    elif code == "roster":
        roster = []
        for user in args[0]:
            roster.append(user.nick) 
        return json.dumps({'code' : code, 'ext' : roster})