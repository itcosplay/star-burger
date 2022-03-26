data = [
    {'restaurant': 'Москва, ул. Новый Арбат, 15', 'distance_to_client': 1.8933733384805558},
    {'restaurant': 'Москва, Цветной бульвар, 11с2', 'distance_to_client': 1.8812591354885442}
]

import operator

data.sort(key=operator.itemgetter('distance_to_client'))

print(data)