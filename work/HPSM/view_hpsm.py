import pyodbc

def HPSM(request):
    connection_string = (
            r'DRIVER={SQL Server};'
            r'SERVER=HPSMDB;'
            r'DATABASE=HPSMPROD;'
            r'UID=XOSA_APP;'
            r'PWD=UdiCVkraFwgv3i4IqXq7;'
        )

    connection = pyodbc.connect(connection_string)

        # Create a cursor object
    cursor = connection.cursor()

    sql = """SELECT *, DATEADD(hour, 2, OPEN_TIME) as My_time
                FROM dbo.PROBSUMMARYM1 p 
                where ASSIGNEE_NAME is NULL
                and ASSIGNMENT='Prevadzka App' or ASSIGNMENT='Prevadzka TCS/MD' and ASSIGNEE_NAME is NULL
                /*and STATUS='OPEN'*/
                ORDER by OPEN_TIME desc
            """

    # Execute the SQL query to list all the tables
    cursor.execute(sql)

    # Fetch and print the table names
    APP_INC = cursor.fetchall()
# for table in APP_INC:
#     print(table.NUMBER+' / ' +table.ASSIGNMENT+' / ' +table.ACTION+ ' / '+str(table.UPDATE_ACTION))
#     print()


#         # print(table[0])
#         # print(table[7])
#         # print(table[37])
#         # print(table[38])

# # Close the database connection
# connection.close()



