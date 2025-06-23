# pylint: disable=import-error
from extract_from_esteticals import extract_from_esteticals
from sheets import write_to_sheet, create_credential_file


def main():
    create_credential_file()
    data = extract_from_esteticals()
    write_to_sheet(data)


if __name__ == "__main__":
    main()
