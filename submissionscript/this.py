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
            files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and f.endswith(".sql")]
            for file in files:
                full_file_path = os.path.join(dir, file)
                match = re.match(r"^\d+", file)
                if match:
                    number = int(match.group())
                    migrations_versions_tuple.append((number, full_file_path))
            sorted_migrations_versions_tuple = sorted(migrations_versions_tuple, key=lambda x: x[0])
            return sorted_migrations_versions_tuple
    except Exception as e:
        print(f"Error: {str(e)}")


def migrate_mysql_to_latest(to_migrate, mysql_user, mysql_host, mysql_database_name, mysql_user_password):
    """
    :param to_migrate: tuple containing versions and filenames to migrate the db to
    :param mysql_user: the mysql username from env
    :param mysql_host: the mysql host container
    :param mysql_database_name: the mysql db name
    :param mysql_user_password: the mysql username password
    :return: just the execution log as stdout
    """
    try:
        conn = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_user_password,
            database=mysql_database_name
        )
        cursor = conn.cursor()
        # The database upgrade is based on looking up the current version
        # in the database and comparing this number to the numbers in the script names
        cursor.execute("SELECT version FROM versionTable")
        init_version = cursor.fetchone()[0]
        just_versions = [version for version, _ in to_migrate]
        last_version = just_versions[-1]
        # If the version number from the db matches the highest number from the scripts then nothing is executed
        if init_version == last_version:
            print(f"No need to execute the SQL migrations at all. The DB is already at the latest version #{init_version}.")
            return
        # All scripts that contain a number higher than the current db version
        # will be executed against the database in numerical order
        to_migrate_filtered = [(version, script) for version, script in to_migrate if version > init_version]
        for version, script in to_migrate_filtered:
            with open(script, "r") as script_file:
                script_content = script_file.read()
                cursor.execute(script_content)
                update_query = "UPDATE versionTable SET version = %s"
                cursor.execute(update_query, (version,))
                conn.commit()
                print(f"Script '{script}' executed and versionTable updated to version #{version}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    migrations = get_migration_files_and_versions(sys.argv[1])
    migrate_mysql_to_latest(migrations, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
