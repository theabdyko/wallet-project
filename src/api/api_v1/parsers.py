from rest_framework.parsers import JSONParser


class JSONAPIParser(JSONParser):
    media_type = "application/vnd.api+json"
