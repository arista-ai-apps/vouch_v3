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
        textColor=colors.red
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
    # Intentional missing data for buyer GSTIN and Supplier GSTIN
    data = [
        ["Supplier", invoice["supplier_name"], "Invoice No.", invoice["invoice_no"]],
        ["Supplier City", invoice["supplier_city"], "Invoice Date", invoice["invoice_date"]],
        ["Supplier GSTIN", invoice.get("supplier_gstin", ""), "Place of Supply", invoice["place_of_supply"]],
        ["Buyer", invoice["buyer_name"], "Buyer GSTIN", invoice.get("buyer_gstin", "")],
        ["Billing City", invoice["billing_city"], "Shipping City", invoice["shipping_city"]]
    ]
    table = Table(data, colWidths=[90, 190, 90, 165])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#9ca3af")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#fff7ed")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#fff7ed")),
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
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#991b1b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
    ]))
    return table

def build_tax_table(invoice):
    data = [
        ["Tax Type", "Rate", "Amount"],
        ["CGST", "9%", "900"],
        ["SGST", "9%", "900"],
        ["Total Tax", "", "1,800"],
        ["Grand Total", "", "11,800"]
    ]
    table = Table(data, colWidths=[90, 70, 100], hAlign="RIGHT")
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#9ca3af")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    return table

def create_invoice_pdf(invoice, items, output_path):
    styles = get_styles()
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    elements = []
    elements.append(Paragraph("TAX INVOICE (MISSING INFO)", styles["InvoiceTitle"]))
    elements.append(Spacer(1, 12))
    elements.append(build_header_table(invoice))
    elements.append(Spacer(1, 14))
    elements.append(build_items_table(items))
    elements.append(Spacer(1, 12))
    elements.append(build_tax_table(invoice))
    elements.append(Spacer(1, 14))
    elements.append(Paragraph("Scenario: This invoice is missing the Supplier and Buyer GSTINs.", styles["InvoiceSmall"]))
    doc.build(elements)

if __name__ == "__main__":
    output_dir = Path("storage/12")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    inv_missing = {
        "invoice_no": "MISSING-DATA-999",
        "invoice_date": "2026-04-06",
        "supplier_name": "Incomplete Vendor Pvt Ltd",
        "supplier_city": "Mumbai",
        # supplier_gstin is missing
        "buyer_name": "Acme Corp",
        # buyer_gstin is missing
        "billing_city": "Pune",
        "shipping_city": "Pune",
        "place_of_supply": "NA",
        "scenario_desc": "Missing GSTINs and Place of Supply."
    }
    items = [{"description": "Missing Data Test Item", "hsn": "0000", "qty": 1, "unit": "Nos", "unit_price": 10000, "taxable_value": 10000}]
    create_invoice_pdf(inv_missing, items, output_dir / "tax_missing_data.pdf")
    print("Success: Generated missing data scenario in storage/12/tax_missing_data.pdf")
