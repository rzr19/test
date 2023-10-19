#!/usr/bin/env python3

import sys
import os
import re


def get_migration_files_and_versions(dir):
    """
    :type dir: path of a directory containing migration files for mysql
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
                match = re.match(r"^\d+", file)
                if match:
                    number = int(match.group())
                    migrations_versions_tuple.append((number, file))
            sorted_migrations_versions_tuple = sorted(
                migrations_versions_tuple, key=lambda x: x[0]
            )
            return sorted_migrations_versions_tuple
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    migrations = get_migration_files_and_versions("/scripts")
    print(migrations)
