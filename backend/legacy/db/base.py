import json

class _Base(object):
    json_fields = []

    def cascade(self):
        return []

    def to_dict(self):
        ret_dict = self.__dict__
        for field in self.json_fields:
            data = ret_dict.get(field, '{}')
            ret_dict[field] = json.loads(data)
        return ret_dict
