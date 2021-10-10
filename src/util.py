def num_to_list(num, length):
    lis = [*map(lambda s: int(s), str(num))]
    for i in range(length - len(lis)):
        lis.insert(0, -1)
    return lis


def list_join(lis: list, v):
    return [*lis, v]


def default_num_parser(num):
    return 0 if num == -1 else num


def digital_num_parser(num, idx):
    if num == -1:
        return ''
    if idx == 0:
        b = num in [0, 2, 3, 5, 6, 8, 9]
    elif idx == 1:
        b = num in [0, 2, 3, 5, 6, 7, 8, 9]
    elif idx == 2:
        b = num in [0, 1, 3, 4, 5, 6, 7, 8, 9]
    elif idx == 3:
        b = num in [0, 2, 6, 8]
    elif idx == 4:
        b = num in [0, 4, 5, 6, 8, 9]
    elif idx == 5:
        b = num in [0, 1, 2, 3, 4, 7, 8, 9]
    else:
        b = num in [2, 3, 4, 5, 6, 8, 9]
    return b
