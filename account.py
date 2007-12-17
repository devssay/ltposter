import os
path = '/home/tinuviel/.lt-account'
apikey = {}
if os.path.exists(path):
    f = open(path)
    username = f.readline().strip()
    password = f.readline().strip()
    for line in f:
        api, key = line.strip().split('=')
        apikey[api] = key
    f.close()
else:
    username = ''
    password = ''
