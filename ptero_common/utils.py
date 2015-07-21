
def format_dict_of_lists(data):
    result = {}
    for key, value in data.iteritems():
        if len(value) == 1:
            result[key] = value[0]
        else:
            result[key] = sorted(value)
    return result
