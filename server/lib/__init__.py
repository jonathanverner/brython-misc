def update_params(dict_a,dict_b, keys):
    for k in keys:
        if k in dict_b:
            dict_a[k] = dict_b[k]
