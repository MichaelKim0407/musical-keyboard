import sys
from os.path import abspath, dirname, join

path = join(dirname(dirname(abspath(__file__))), 'src')
sys.path.append(path)
