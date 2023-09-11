import configparser


def get_database_config(filename="database.ini", section="postgresql"):
    config_file_path = "db_config/" + filename
    # create a parser
    parser = configparser.ConfigParser()
    # read config file
    parser.read(config_file_path)

    # get section
    if parser.has_section(section):
        params = parser.items(section)
        db_conn_string = ""
        # Loop in the list
        for param in params:
            # Join key and value to string
            db_conn_string = f"{db_conn_string} {param[0]} = {param[1]}"
    else:
        raise Exception(f"Section {section} not found in {filename} file")

    return db_conn_string


if __name__ == "__main__":
    print(get_database_config())
