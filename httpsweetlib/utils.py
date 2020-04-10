

def lower_dict_keys(d):
    other_d = {}
    for key, value in d.items():
        other_d[key.lower()] = value
    return other_d


def define_starwith_methods(cls):
    class_variables = {
        key: value for key, value in cls.__dict__.items()
        if not key.startswith('__') and not callable(key)
    }

    for key, value in class_variables:
        setattr(
            cls,
            'is_{}'.format(key.lower()),
            classmethod(lambda cls, key: key.startswith(value))
        )
