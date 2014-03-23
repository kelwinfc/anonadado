def balance(x, y):
    sx = str(x)
    sy = str(y)
    while len(sx) < len(sy):
        sx = "0" + sx
    return sx
