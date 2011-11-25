import dircache, directDwnld, py_compile, win32ui, sys

def bulk(dir, ending, f):
    for file in dircache.listdir(dir):
        if file.endswith(ending):
            f(file)

def main(argv):
    # Compile
    bulk(argv[0], "py", py_compile.compile)
    # Download
    bulk(argv[0], "pyo", directDwnld.Dwnld)

if __name__ == "__main__":
    main(sys.argv[1:])
