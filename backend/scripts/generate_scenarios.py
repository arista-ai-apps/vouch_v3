from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="InvoiceTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1e3a8a")
    ))
    styles.add(ParagraphStyle(
        name="InvoiceSub",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#374151")
    ))
    styles.add(ParagraphStyle(
        name="InvoiceSmall",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4b5563")
    ))
    return styles

def build_header_table(invoice):
    data = [
        ["Supplier", invoice["supplier_name"], "Invoice No.", invoice["invoice_no"]],
        ["Supplier City", invoice["supplier_city"], "Invoice Date", invoice["invoice_date"]],
        ["Supplier GSTIN", invoice["supplier_gstin"], "Place of Supply", invoice["place_of_supply"]],
        ["Buyer", invoice["buyer_name"], "Buyer GSTIN", invoice["buyer_gstin"]],
        ["Billing City", invoice["billing_city"], "Shipping City", invoice["shipping_city"]]
    ]
    table = Table(data, colWidths=[90, 190, 90, 165])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#9ca3af")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f7ff")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f0f7ff")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    return table

def build_items_table(items):
    data = [["Sl.", "Description", "HSN/SAC", "Qty", "Unit", "Price", "Taxable Value"]]
    for i, item in enumerate(items, start=1):
        data.append([str(i), item["description"], item["hsn"], str(item["qty"]), item["unit"], f'{item["unit_price"]:,}', f'{item["taxable_value"]:,}'])
    table = Table(data, colWidths=[30, 200, 62, 42, 42, 70, 90])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#9ca3af")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
    ]))
    return table

def build_tax_table(invoice):
    data = [["Tax Type", "Rate", "Amount"]]
    if invoice.get("cgst_amount"):
        data.append(["CGST", invoice.get("cgst_rate", "9%"), f'{invoice["cgst_amount"]:,}'])
        data.append(["SGST", invoice.get("sgst_rate", "9%"), f'{invoice["sgst_amount"]:,}'])
    if invoice.get("igst_amount"):
        data.append(["IGST", invoice.get("igst_rate", "18%"), f'{invoice["igst_amount"]:,}'])
    data.append(["Total Tax", "", f'{invoice["total_tax"]:,}'])
    data.append(["Grand Total", "", f'{invoice["grand_total"]:,}'])

    table = Table(data, colWidths=[90, 70, 100], hAlign="RIGHT")
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#9ca3af")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (2, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    return table

def create_invoice_pdf(invoice, items, output_path):
    styles = get_styles()
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    elements = []
    elements.append(Paragraph("TAX INVOICE", styles["InvoiceTitle"]))
    elements.append(Spacer(1, 12))
    elements.append(build_header_table(invoice))
    elements.append(Spacer(1, 14))
    elements.append(build_items_table(items))
    elements.append(Spacer(1, 12))
    elements.append(build_tax_table(invoice))
    elements.append(Spacer(1, 14))
    elements.append(Paragraph("Scenario: " + invoice["scenario_desc"], styles["InvoiceSmall"]))
    doc.build(elements)

if __name__ == "__main__":
    output_dir = Path("storage/1")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ── CASE 1: Correct Intra-state ──
    inv_correct = {
        "invoice_no": "CORRECT-TAX-001",
        "invoice_date": "2026-04-04",
        "supplier_name": "Mumbai Logistics Services",
        "supplier_city": "Mumbai",
        "supplier_gstin": "27SUPPL1234F1Z1",
        "buyer_name": "Acme Corp",
        "buyer_gstin": "27ACMEX1234P1Z1",
        "billing_city": "Pune",
        "shipping_city": "Pune",
        "place_of_supply": "Maharashtra",
        "total_tax": 1800,
        "grand_total": 11800,
        "cgst_rate": "9%", "cgst_amount": 900,
        "sgst_rate": "9%", "sgst_amount": 900,
        "scenario_desc": "Same state (27 -> 27) with correct CGST/SGST."
    }
    items = [{"description": "Office Chairs", "hsn": "9403", "qty": 2, "unit": "Nos", "unit_price": 5000, "taxable_value": 10000}]
    create_invoice_pdf(inv_correct, items, output_dir / "tax_intra_correct.pdf")

    # ── CASE 2: Wrong Intra-state (Mismatch) ──
    inv_wrong = {
        "invoice_no": "WRONG-TAX-002",
        "invoice_date": "2026-04-05",
        "supplier_name": "Pune Industrial Supplies",
        "supplier_city": "Pune",
        "supplier_gstin": "27WROGE1234F1Z1",
        "buyer_name": "Acme Corp",
        "buyer_gstin": "27ACMEX1234P1Z1",
        "billing_city": "Mumbai",
        "shipping_city": "Mumbai",
        "place_of_supply": "Maharashtra",
        "total_tax": 3600,
        "grand_total": 23600,
        "igst_rate": "18%", "igst_amount": 3600,
        "scenario_desc": "Intra-state (27 -> 27) but IGST charged instead of CGST/SGST."
    }
    items2 = [{"description": "Electric Motors", "hsn": "8501", "qty": 1, "unit": "Nos", "unit_price": 20000, "taxable_value": 20000}]
    create_invoice_pdf(inv_wrong, items2, output_dir / "tax_intra_mismatch.pdf")

    print("Success: Generated scenarios in storage/1/")
