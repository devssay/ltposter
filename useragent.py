import urllib

version = '0.2'
user_agent = 'LTposter/%s (+http://ltposter.kldp.net/)' % (version,)

class AppURLopener(urllib.FancyURLopener):
    version = user_agent

def install():
    urllib._urlopener = AppURLopener()
