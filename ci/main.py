#
#   Call ALL your CI scripts from here
#
from import_test import test as import_test
from basic_SP_train_test import test as SP_train_test

if __name__ == '__main__':
    print (" ===> BEGIN CI TEST <=== ")
    print (" ==> Import saphyra test")
    import_test()
    print (" ==> Training a basic model with SP callback")
    SP_train_test()