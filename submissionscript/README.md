The proposed solution works by just running 

    docker-compose up --build -d

The above command starts both the exec and db containers
After startup, inspecting the logs of the exec container should provide this stdout

    $ docker logs -f a29c
    The SQL migrations will begin shortly.
    Script '/scripts/01.createPersonLink.sql' executed and versionTable updated to version #1
    Script '/scripts/02.someTableinsert.sql' executed and versionTable updated to version #2
    Script '/scripts/04 app table.sql' executed and versionTable updated to version #4
    Script '/scripts/33. appTable data.sql' executed and versionTable updated to version #33

The requirement to execute all scripts with a version higher than the current one in the db can be tested 
by changing the INSERT value from db_scripts/seed_data/seeddata.sql from 0 to say 3.

    docker logs -f 034a
    The SQL migrations will begin shortly.
    Script '/scripts/04 app table.sql' executed and versionTable updated to version #4
    Script '/scripts/33. appTable data.sql' executed and versionTable updated to version #33

The script tablething.sql is not currently taken into account. One must provide it a number with a mv prior to that.

    docker logs -f fdc7
    The SQL migrations will begin shortly.
    Script '/scripts/01.createPersonLink.sql' executed and versionTable updated to version #1
    Script '/scripts/02.someTableinsert.sql' executed and versionTable updated to version #2
    Script '/scripts/04 app table.sql' executed and versionTable updated to version #4
    Script '/scripts/33. appTable data.sql' executed and versionTable updated to version #33
    Script '/scripts/34__tablething.sql' executed and versionTable updated to version #34

By declaring ./test/ as volume and mounting it to execute the tests, there are no assert errors:

    root@41c165ca09ff:/test# pytest db_test.py
    ============================================================================================== test session starts ==============================================================================================
    platform linux -- Python 3.8.10, pytest-7.4.2, pluggy-1.3.0
    rootdir: /test
    collected 3 items
    
    db_test.py ...                                                                                                                                                                                            [100%]
    
    =============================================================================================== 3 passed in 0.02s ===============================================================================================
    root@41c165ca09ff:/test#

Note:
    
I added a container health check for the db_container and a sleep for a few seconds in entrypoint.sh 
That is why the first log from the exec_container stdout is ``The SQL migrations will begin shortly.``
    
That is because right after startup, a lot of times the execution of the scripts failed with MySQL connection errors.