a = (1, 2, 3)
b = {"x": 1, "y": 2, "z": 3}

print({*[*a, 4]})
print({**b, "z2": 12})

# print(**a)
# print(*b)
