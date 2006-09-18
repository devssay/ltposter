import os
path = '/home/tinuviel/.lt-account'
if os.path.exists(path):
    f = open(path)
    username = f.readline().strip()
    password = f.readline().strip()
    naverkey = f.readline().strip()
    f.close()
else:
    username = ''
    password = ''
    naverkey = ''
