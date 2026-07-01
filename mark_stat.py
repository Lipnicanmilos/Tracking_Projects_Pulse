import sys, os
from datetime import datetime
from datetime import date
from datetime import time
from dateutil.relativedelta import relativedelta
import pandas as pd


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

now = datetime.now()
time = now.strftime("%H:%M:%S")

# connect DWH DB
from connect_settings import con_dwh, con_billdb

# 1 Drop Table if exists T_TMP_MKT_ROAD_USAGE_1
cur_dwh = con_dwh.cursor()
cur_dwh.execute('''declare n number(10);
                    begin
                    select count(*) into n from tab where tname='T_TMP_MKT_ROAD_USAGE_1';

                    if (n > 0) then 
                        execute immediate 
                        'DROP TABLE T_TMP_MKT_ROAD_USAGE_1';
                    end if;
                    end;''')

print("Table Deleted: T_TMP_MKT_ROAD_USAGE_1", time, " START")

# 1 Create table T_TMP_MKT_ROAD_USAGE_1
cur_dwh.execute('''CREATE TABLE T_TMP_MKT_ROAD_USAGE_1 AS
                    SELECT
                    /*+ NO_INDEX(pass)*/
                    pass.VEHICLE_ID,
                    to_char(pass.OBU_LOCAL_TIME,'mm') AS MONTH,
                    s.ROAD_TYPE_CODE,
                    pass.OBU_NUMBER_OF_AXLES,
                    NVL(pass.DISCOUNT_RATE, 0) AS DISCOUNT_RATE,
                    SUM(DECODE(TOLL_EVENT_TYPE_CODE, 1, 1, 2, -1, 3, 1, 0)) AS Transaction_count,
                    SUM(pass.PRICE_AMOUNT) AS Transaction_amount,
                    SUM (UNITS_USED) AS Tolled_km,
                    SUM(NVL(DISCOUNT_AMOUNT, 0)) AS Discount_amount
                    FROM BILLIEN_MAA.RATED_TOLL_EVENT pass
                    JOIN BILLIEN_MAA.ROAD_SEGMENTS s ON pass.TOLL_SEGMENT_ID=s.TOLL_SEGMENT_ID
                    WHERE pass.OBU_TIMESTAMP >= CAST(FROM_TZ(CAST(ADD_MONTHS(TRUNC(CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE), 'MM'), -1/*pri ročnom -12*/) AS TIMESTAMP), 'CET') AT TIME ZONE 'GMT' AS DATE)
                    AND pass.OBU_TIMESTAMP < CAST(FROM_TZ(CAST(TRUNC(CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE), 'MM') AS TIMESTAMP), 'CET') AT TIME ZONE 'GMT' AS DATE)
                    AND pass.EXEMPT_FLAG=0
                    AND pass.TEST_CUSTOMER_FLAG=0
                    GROUP BY pass.VEHICLE_ID, to_char(pass.OBU_LOCAL_TIME,'mm'), s.ROAD_TYPE_CODE, pass.OBU_NUMBER_OF_AXLES, NVL(pass.DISCOUNT_RATE, 0)''')
now = datetime.now()
time = now.strftime("%H:%M:%S")
print("Table Created: T_TMP_MKT_ROAD_USAGE_1", time)

# 2 Drop Table if exists T_TMP_MKT_ROAD_USAGE_2
cur_dwh.execute('''declare n number(10);
                    begin
                    select count(*) into n from tab where tname='T_TMP_MKT_ROAD_USAGE_2';

                    if (n > 0) then 
                        execute immediate 
                        'DROP TABLE T_TMP_MKT_ROAD_USAGE_2';
                    end if;
                    end;''')
print("Table Deleted: T_TMP_MKT_ROAD_USAGE_2", time)

# 2 Create table T_TMP_MKT_ROAD_USAGE_2
cur_dwh.execute('''CREATE TABLE T_TMP_MKT_ROAD_USAGE_2 AS
                    SELECT
                    /*+ NO_INDEX(pass)*/
                    pass.VEHICLE_ID,
                    to_char(pass.OBU_LOCAL_TIME,'yyyy.mm.dd') AS PassageDate,
                    SUM(DECODE(TOLL_EVENT_TYPE_CODE, 1, 1, 2, -1, 3, 1, 0)) AS Transaction_count,
                    SUM(pass.PRICE_AMOUNT) AS Transaction_amount,
                    SUM (UNITS_USED) AS Tolled_km
                    FROM BILLIEN_MAA.RATED_TOLL_EVENT pass
                    JOIN BILLIEN_MAA.ROAD_SEGMENTS s ON pass.TOLL_SEGMENT_ID=s.TOLL_SEGMENT_ID
                    WHERE pass.OBU_TIMESTAMP >= CAST(FROM_TZ(CAST(ADD_MONTHS(TRUNC(CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE), 'MM'), -1/*pri ročnom -12*/) AS TIMESTAMP), 'CET') AT TIME ZONE 'GMT' AS DATE)
                    AND pass.OBU_TIMESTAMP < CAST(FROM_TZ(CAST(TRUNC(CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE), 'MM') AS TIMESTAMP), 'CET') AT TIME ZONE 'GMT' AS DATE)
                    AND pass.EXEMPT_FLAG=0
                    AND pass.TEST_CUSTOMER_FLAG=0
                    GROUP BY pass.VEHICLE_ID,to_char(pass.OBU_LOCAL_TIME,'yyyy.mm.dd')''')
now = datetime.now()
time = now.strftime("%H:%M:%S")
print("Table Created: T_TMP_MKT_ROAD_USAGE_2", time)

# 3 Drop Table if exists T_TMP_MKT_ROAD_USAGE_3
cur_dwh.execute('''declare n number(10);
                    begin
                    select count(*) into n from tab where tname='T_TMP_MKT_ROAD_USAGE_3';

                    if (n > 0) then 
                        execute immediate 
                        'DROP TABLE T_TMP_MKT_ROAD_USAGE_3';
                    end if;
                    end;''')
print("Table Deleted: T_TMP_MKT_ROAD_USAGE_3", time)

# 3 Create table T_TMP_MKT_ROAD_USAGE_3
cur_dwh.execute('''CREATE TABLE T_TMP_MKT_ROAD_USAGE_3 AS
                    SELECT
                    /*+ NO_INDEX(pass)*/
                    pass.VEHICLE_ID,
                    TRUNC(pass.OBU_LOCAL_TIME) AS Passage_date,
                    pass.TOLL_SEGMENT_ID AS Segment_ID,
                    SUM(DECODE(TOLL_EVENT_TYPE_CODE, 1, 1, 2, -1, 3, 1, 0)) AS Transaction_count,
                    SUM(pass.PRICE_AMOUNT) AS Transaction_amount
                    FROM BILLIEN_MAA.RATED_TOLL_EVENT pass
                    WHERE pass.OBU_TIMESTAMP >= CAST(FROM_TZ(CAST(ADD_MONTHS(TRUNC(CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE), 'MM'), -1/*pri ročnom -12*/) AS TIMESTAMP), 'CET') AT TIME ZONE 'GMT' AS DATE)
                    AND pass.OBU_TIMESTAMP < CAST(FROM_TZ(CAST(TRUNC(CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE), 'MM') AS TIMESTAMP), 'CET') AT TIME ZONE 'GMT' AS DATE)
                    AND pass.EXEMPT_FLAG=0
                    AND pass.TEST_CUSTOMER_FLAG=0
                    GROUP BY pass.VEHICLE_ID, TRUNC(pass.OBU_LOCAL_TIME), pass.TOLL_SEGMENT_ID''')
now = datetime.now()
time = now.strftime("%H:%M:%S")
print("Table Created: T_TMP_MKT_ROAD_USAGE_3", time," END created tables")
# ---------- end created table --------------------------------------------------------
# ---------- start created reports --------------------------------------------------------

# settings date
today = datetime.now() + relativedelta(months=-1)
my = today.strftime("%m%Y")

# Save Script
filename=r"C:\NEW\Scripts\Marketing_stat\1_BILLDB_a.sql"

# open script filename
f = open(filename)
full_sql = f.read()
cur_billdb = con_billdb.cursor()
cur_billdb.execute(full_sql)

columns = [desc[0] for desc in cur_billdb.description]
data = cur_billdb.fetchall()
df = pd.DataFrame(list(data), columns=columns)

# generate report
writer = pd.ExcelWriter(r'C:\NEW\Reports\Marketing_stat\01a_'+my+'.xlsx')

df.to_excel(writer, sheet_name='01', index=False)
writer.save()
# cur_billdb.close()

now = datetime.now()
time = now.strftime("%H:%M:%S")
print("create report: 01a_"+my+".xlsx "+time)


# Save Script
filename=r"C:\NEW\Scripts\Marketing_stat\1_BILLDB_b.sql"

# open script filename
f = open(filename)
full_sql = f.read()
cur_billdb.execute(full_sql)

columns = [desc[0] for desc in cur_billdb.description]
data = cur_billdb.fetchall()
df = pd.DataFrame(list(data), columns=columns)

# generate report
writer = pd.ExcelWriter(r'C:\NEW\Reports\Marketing_stat\01b_'+my+'.xlsx')

df.to_excel(writer, sheet_name='01', index=False)
writer.save()
# cur_billdb.close()

now = datetime.now()
time = now.strftime("%H:%M:%S")
print("create report: 01b_"+my+".xlsx "+time)


# Save Script
filename=r"C:\NEW\Scripts\Marketing_stat\2_DWH_a.sql"

# open script filename
f = open(filename)
full_sql = f.read()
cur_dwh = con_dwh.cursor()
cur_dwh.execute(full_sql)

columns = [desc[0] for desc in cur_dwh.description]
data = cur_dwh.fetchall()
df = pd.DataFrame(list(data), columns=columns)

# generate report
writer = pd.ExcelWriter(r'C:\NEW\Reports\Marketing_stat\02a_'+my+'.xlsx')

df.to_excel(writer, sheet_name='01', index=False)
writer.save()
# cur_dwh.close()

now = datetime.now()
time = now.strftime("%H:%M:%S")
print("create report: 02a_"+my+".xlsx "+time)

# Save Script
filename=r"C:\NEW\Scripts\Marketing_stat\2_DWH_b.sql"

# open script filename
f = open(filename)
full_sql = f.read()
cur_dwh = con_dwh.cursor()
cur_dwh.execute(full_sql)

columns = [desc[0] for desc in cur_dwh.description]
data = cur_dwh.fetchall()
df = pd.DataFrame(list(data), columns=columns)

# generate report
writer = pd.ExcelWriter(r'C:\NEW\Reports\Marketing_stat\02b_'+my+'.xlsx')

df.to_excel(writer, sheet_name='01', index=False)
writer.save()
# cur_dwh.close()

now = datetime.now()
time = now.strftime("%H:%M:%S")
print("create report: 02b_"+my+".xlsx "+time)

# Save Script
filename=r"C:\NEW\Scripts\Marketing_stat\2_DWH_c.sql"

# open script filename
f = open(filename)
full_sql = f.read()
cur_dwh = con_dwh.cursor()
cur_dwh.execute(full_sql)

columns = [desc[0] for desc in cur_dwh.description]
data = cur_dwh.fetchall()
df = pd.DataFrame(list(data), columns=columns)

# generate report
writer = pd.ExcelWriter(r'C:\NEW\Reports\Marketing_stat\02c_'+my+'.xlsx')

df.to_excel(writer, sheet_name='01', index=False)
writer.save()
# cur_dwh.close()

now = datetime.now()
time = now.strftime("%H:%M:%S")
print("create report: 02c_"+my+".xlsx "+time)

# Save Script
filename=r"C:\NEW\Scripts\Marketing_stat\10_DWH_a.sql"

# open script filename
f = open(filename)
full_sql = f.read()
cur_dwh = con_dwh.cursor()
cur_dwh.execute(full_sql)

columns = [desc[0] for desc in cur_dwh.description]
data = cur_dwh.fetchall()
df = pd.DataFrame(list(data), columns=columns)

# generate report
writer = pd.ExcelWriter(r'C:\NEW\Reports\Marketing_stat\10a_'+my+'.xlsx')

df.to_excel(writer, sheet_name='01', index=False)
writer.save()
# cur_dwh.close()

now = datetime.now()
time = now.strftime("%H:%M:%S")
print("create report: 10a_"+my+".xlsx "+time)

# Save Script
filename=r"C:\NEW\Scripts\Marketing_stat\10_DWH_b.sql"

# open script filename
f = open(filename)
full_sql = f.read()
cur_dwh = con_dwh.cursor()
cur_dwh.execute(full_sql)

columns = [desc[0] for desc in cur_dwh.description]
data = cur_dwh.fetchall()
df = pd.DataFrame(list(data), columns=columns)

# generate report
writer = pd.ExcelWriter(r'C:\NEW\Reports\Marketing_stat\10b_'+my+'.xlsx')

df.to_excel(writer, sheet_name='01', index=False)
writer.save()
# cur_dwh.close()

now = datetime.now()
time = now.strftime("%H:%M:%S")
print("create report: 10b_"+my+".xlsx "+time)

# Save Script
filename=r"C:\NEW\Scripts\Marketing_stat\10_DWH_c.sql"

# open script filename
f = open(filename)
full_sql = f.read()
cur_dwh = con_dwh.cursor()
cur_dwh.execute(full_sql)

columns = [desc[0] for desc in cur_dwh.description]
data = cur_dwh.fetchall()
df = pd.DataFrame(list(data), columns=columns)

# generate report
writer = pd.ExcelWriter(r'C:\NEW\Reports\Marketing_stat\10c_'+my+'.xlsx')

df.to_excel(writer, sheet_name='01', index=False)
writer.save()
# cur_dwh.close()

now = datetime.now()
time = now.strftime("%H:%M:%S")
print("create report: 10c_"+my+".xlsx "+time)

# Save Script
filename=r"C:\NEW\Scripts\Marketing_stat\10_DWH_d.sql"

# open script filename
f = open(filename)
full_sql = f.read()
cur_dwh = con_dwh.cursor()
cur_dwh.execute(full_sql)

columns = [desc[0] for desc in cur_dwh.description]
data = cur_dwh.fetchall()
df = pd.DataFrame(list(data), columns=columns)

# generate report
writer = pd.ExcelWriter(r'C:\NEW\Reports\Marketing_stat\10d_'+my+'.xlsx')

df.to_excel(writer, sheet_name='01', index=False)
writer.save()
# cur_dwh.close()

now = datetime.now()
time = now.strftime("%H:%M:%S")
print("create report: 10d_"+my+".xlsx "+time)

# Save Script
filename=r"C:\NEW\Scripts\Marketing_stat\11_DWH_a.sql"

# open script filename
f = open(filename)
full_sql = f.read()
cur_dwh = con_dwh.cursor()
cur_dwh.execute(full_sql)

columns = [desc[0] for desc in cur_dwh.description]
data = cur_dwh.fetchall()
df = pd.DataFrame(list(data), columns=columns)

# generate report
writer = pd.ExcelWriter(r'C:\NEW\Reports\Marketing_stat\11a_'+my+'.xlsx')
df.to_excel(writer, sheet_name='01', index=False)
writer.save()
# cur_dwh.close()

now = datetime.now()
time = now.strftime("%H:%M:%S")
print("create report: 11a_"+my+".xlsx "+time)