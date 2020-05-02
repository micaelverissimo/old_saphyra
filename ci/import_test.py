# Example CI script

def test():
    print ("Import test...", end='')
    try:
        import saphyra
        print (" success!")
    except Exception as e:
        print (" failed :(")
        raise e
