#
#   Call ALL your CI scripts from here
#
from import_test import test as import_test

if __name__ == '__main__':
    print (" ===> BEGIN CI TEST <=== ")
    import_test()