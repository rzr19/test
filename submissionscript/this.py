#!/usr/bin/env python3

import sys
import os
import re
import mysql.connector


def get_migration_files_and_versions(dir):
    """
    :type dir: path of a directory containing migration files for mysql
    :return migrations: a tuple as mentioned below
    ## this returns a tuple with (index, filename) for each migration sql script
    ## it fetches the index using re and assumes all scripts begin with numbers
    """
    migrations_versions_tuple = []
    try:
        if os.path.exists(dir) and os.path.isdir(dir):
            files = [
                f
                for f in os.listdir(dir)
                if os.path.isfile(os.path.join(dir, f)) and f.endswith(".sql")
            ]
            for file in files:
                full_file_path = os.path.join(dir, file)
                match = re.match(r"^\d+", file)
                if match:
                    number = int(match.group())
                    migrations_versions_tuple.append((number, full_file_path))
            sorted_migrations_versions_tuple = sorted(
                migrations_versions_tuple, key=lambda x: x[0]
            )
            return sorted_migrations_versions_tuple
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def migrate_mysql_to_latest(to_migrate, mysql_user, mysql_host, mysql_database_name, mysql_user_password):
    """
    :param to_migrate: tuple containing versions and filenames to migrate the db to
    :param mysql_user: the mysql username from env
    :param mysql_host: the mysql host container
    :param mysql_database_name: the mysql db name
    :param mysql_user_password: the mysql username password
    :return: just the execution log as stdout
    """
    db_config = {
        "host": mysql_host,
        "user": mysql_user,
        "password": mysql_user_password,
        "database": mysql_database_name,
    }
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    for version, script in to_migrate:
        try:
            with open(script, 'r') as script_file:
                script_content = script_file.read()
            cursor.execute(script_content)
            update_query = "UPDATE versionTable SET version = %s"
            cursor.execute(update_query, (version,))
            conn.commit()
            print(f"Script '{script}' executed and version updated to {version}")
        except Exception as e:
            print(f"Error while executing '{script}': {str(e)}")


if __name__ == "__main__":
    migrations = get_migration_files_and_versions(sys.argv[1])
    migrate_mysql_to_latest(migrations, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
