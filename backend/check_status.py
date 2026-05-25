import sqlite3

conn = sqlite3.connect('./sql_app.db')
cursor = conn.cursor()

cursor.execute("SELECT status, COUNT(*) FROM uploaded_files GROUP BY status")
print("=== File Upload Status ===")
for r in cursor.fetchall():
    print(f'  Status "{r[0]}": {r[1]} files')

print()
cursor.execute("SELECT match_status, COUNT(*) FROM reconciliation_results GROUP BY match_status")
print("=== Reconciliation Status ===")
for r in cursor.fetchall():
    print(f'  Match Status "{r[0]}": {r[1]} records')

conn.close()
