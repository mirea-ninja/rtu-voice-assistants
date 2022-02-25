array_1 = ['123', '456']
array_2 = ['789', '000']

global_array = [
    array_1,
    array_2
]

check_elem = '123'
print(any(check_elem in sublist for sublist in global_array))