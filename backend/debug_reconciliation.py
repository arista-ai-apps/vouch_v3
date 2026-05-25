"""
Show GSTIN mismatches side by side to understand the pattern.
"""
import sqlite3

conn = sqlite3.connect('./sql_app.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT rr.invoice_number, rr.vendor_gstin, rr.total_value
    FROM register_rows rr
    JOIN registers r ON rr.register_id = r.id
    WHERE r.engagement_id = 1
""")
reg_rows = {(row['invoice_number'] or '').strip().lower(): dict(row) for row in cursor.fetchall()}

cursor.execute("""
    SELECT ei.invoice_number, ei.vendor_gstin, ei.total_value, ei.vendor_name
    FROM extracted_invoices ei
    JOIN uploaded_files uf ON ei.file_id = uf.id
    JOIN reconciliation_results rr ON ei.id = rr.invoice_id
    WHERE uf.engagement_id = 1
      AND rr.match_status = 'not_in_purchase_registry'
    ORDER BY ei.invoice_number
    LIMIT 20
""")
unmatched = cursor.fetchall()

print(f"First 20 GSTIN mismatches:")
print()
for inv in unmatched:
    inv_no = (inv['invoice_number'] or '').strip().lower()
    reg = reg_rows.get(inv_no, {})
    print(f"Invoice: {inv['invoice_number']}")
    print(f"  Extracted GSTIN : [{inv['vendor_gstin']}]  len={len(inv['vendor_gstin'] or '')}")
    print(f"  Registry GSTIN  : [{reg.get('vendor_gstin','')}]  len={len(reg.get('vendor_gstin','') or '')}")
    print()

conn.close()
