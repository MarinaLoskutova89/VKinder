
def compare(item_1, item_2):

    photo_type = {'s': 0, 'm': 1, 'x': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'y': 7, 'z': 8, 'w': 9}

    if photo_type[item_1['type']] > photo_type[item_2['type']]:
        return 1
    elif photo_type[item_1['type']] < photo_type[item_2['type']]:
        return -1
    else:
        return 0