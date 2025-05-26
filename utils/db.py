import os
import pyodbc

def get_hub_connection():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('SQL_SERVER', 'tcp:ibizlinkaus.database.windows.net,1433')};"
        f"DATABASE={os.getenv('SQL_DB', 'ibizlink_hub')};"
        f"UID={os.getenv('SQL_UID', 'ibizlinkg')};"
        f"PWD={os.getenv('SQL_PWD', 'ibzHello2019Friends=')};"
    )

def fetch_all_users():
    conn = get_hub_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_email, pw_hash, user_id, chk_sysadmin
        FROM ibizlink.hub_users
        WHERE pw_hash is not null
    """)
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def fetch_domains(user_id=None, is_admin=False):
    conn = get_hub_connection()
    cursor = conn.cursor()
    if is_admin:
        cursor.execute("""
            SELECT domain_code, target_database
            FROM ibizlink.hub_domains
        """)
    else:
        cursor.execute("""
            SELECT domain_code, target_database
            FROM ibizlink.hub_users_domains_link L
            INNER JOIN ibizlink.hub_domains D ON L.domain_id = D.domain_id
            WHERE L.user_id = ?
        """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"domain_code": r[0], "target_database": r[1]} for r in rows]