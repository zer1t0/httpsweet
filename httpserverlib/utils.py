

def lower_dict_keys(d):
    other_d = {}
    for key, value in d.items():
        other_d[key.lower()] = value
    return other_d
