from Scanner import Scanner


def main():
    source = input("Enter source code: ")
    scanner = Scanner(source)
    tokens = scanner.scan()
    for token in tokens:
        print(token)


if __name__ == "__main__":
    main()
