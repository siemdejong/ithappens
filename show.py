import pprint
from zipfile import ZipFile

path = 'dist\shithappens-0.4.0-py3-none-any.whl'
names = ZipFile(path).namelist()
pprint.pprint(names)