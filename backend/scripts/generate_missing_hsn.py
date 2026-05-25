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
        textColor=colors.HexColor("#4b2c20")
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
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#fdfcfb")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#fdfcfb")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    return table

def build_items_table(items):
    # Intentional empty HSN/SAC column
    data = [["Sl.", "Description", "HSN/SAC", "Qty", "Unit", "Price", "Taxable Value"]]
    for i, item in enumerate(items, start=1):
        data.append([str(i), item["description"], "", str(item["qty"]), item["unit"], f'{item["unit_price"]:,}', f'{item["taxable_value"]:,}'])
    table = Table(data, colWidths=[30, 200, 62, 42, 42, 70, 90])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#9ca3af")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#78350f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
    ]))
    return table

def build_tax_table(invoice):
    data = [
        ["Tax Type", "Rate", "Amount"],
        ["CGST", "9%", "1,080"],
        ["SGST", "9%", "1,080"],
        ["Total Tax", "", "2,160"],
        ["Grand Total", "", "14,160"]
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
    elements.append(Paragraph("TAX INVOICE (MISSING HSN)", styles["InvoiceTitle"]))
    elements.append(Spacer(1, 12))
    elements.append(build_header_table(invoice))
    elements.append(Spacer(1, 14))
    elements.append(build_items_table(items))
    elements.append(Spacer(1, 12))
    elements.append(build_tax_table(invoice))
    elements.append(Spacer(1, 14))
    elements.append(Paragraph("Scenario: This invoice is missing the HSN code for its items.", styles["InvoiceSmall"]))
    doc.build(elements)

if __name__ == "__main__":
    output_dir = Path("storage/12")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    inv_missing_hsn = {
        "invoice_no": "MISSING-HSN-111",
        "invoice_date": "2026-04-07",
        "supplier_name": "Generic Hardware Ltd",
        "supplier_city": "Chennai",
        "supplier_gstin": "33AAAAA0000A1Z1",
        "buyer_name": "Acme Corp",
        "buyer_gstin": "27ACMEX1234P1Z1",
        "billing_city": "Pune",
        "shipping_city": "Pune",
        "place_of_supply": "Tamil Nadu",
        "scenario_desc": "Missing HSN code on items."
    }
    items = [{"description": "Stainless Steel Bolts (M10)", "hsn": "", "qty": 100, "unit": "Nos", "unit_price": 120, "taxable_value": 12000}]
    create_invoice_pdf(inv_missing_hsn, items, output_dir / "invoice_missing_hsn.pdf")
    print("Success: Generated missing HSN scenario in storage/12/invoice_missing_hsn.pdf")
