class ModelMixin:
    def to_dict(self):
        data = {}
        for field in self._meta.fields:
            key = field.attname
            value = self.__dict__[key]
            data[key] = value
        return data
