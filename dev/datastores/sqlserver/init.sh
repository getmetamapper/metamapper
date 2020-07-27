for i in {1..12};
do
    /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -d master -i init.sql
    if [ $? -eq 0 ]
    then
        echo "init.sql completed"
        break
    else
        echo "not ready yet..."
        sleep 5
    fi
done
