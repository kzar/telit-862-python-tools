import dircache, directDwnld, win32ui, sys

def bulk_download(dir):
    for file in dircache.listdir(dir):
        if file.endswith("pyo"):
            directDwnld.Dwnld(file)

def main(argv):
    bulk_download(argv[0])

if __name__ == "__main__":
    main(sys.argv[1:])