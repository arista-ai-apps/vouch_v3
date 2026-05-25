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
        textColor=colors.HexColor("#111827")
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
        ["Billing City", invoice["billing_city"], "Shipping City", invoice["shipping_city"]],
        ["e-Way Bill No.", invoice.get("eway_bill_no", ""), "Vehicle No.", invoice.get("vehicle_no", "")],
        ["Payment Terms", invoice.get("payment_terms", ""), "Notes", invoice.get("notes", "")]
    ]

    table = Table(data, colWidths=[90, 190, 90, 165])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#9ca3af")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eff6ff")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#eff6ff")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table


def build_items_table(items):
    data = [[
        "Sl. No.", "Description", "HSN/SAC", "Qty",
        "Unit", "Unit Price", "Discount", "Taxable Value"
    ]]

    for i, item in enumerate(items, start=1):
        data.append([
            str(i),
            item["description"],
            item["hsn"],
            str(item["qty"]),
            item["unit"],
            f'{item["unit_price"]:,}',
            f'{item.get("discount", 0):,}',
            f'{item["taxable_value"]:,}'
        ])

    table = Table(data, colWidths=[38, 192, 62, 42, 42, 68, 55, 80])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#9ca3af")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
    ]))
    return table


def build_tax_table(invoice):
    data = [
        ["Tax Type", "Rate", "Amount"],
        ["CGST", invoice.get("cgst_rate", "0%"), f'{invoice.get("cgst_amount", 0):,}'],
        ["SGST", invoice.get("sgst_rate", "0%"), f'{invoice.get("sgst_amount", 0):,}'],
        ["IGST", invoice.get("igst_rate", "0%"), f'{invoice.get("igst_amount", 0):,}'],
        ["Grand Total", "", f'{invoice["grand_total"]:,}']
    ]

    table = Table(data, colWidths=[90, 70, 100], hAlign="RIGHT")
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#9ca3af")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 4), (2, 4), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    return table


def build_footer_table(invoice):
    data = [
        ["Declaration", invoice.get(
            "declaration",
            "We declare that this invoice contains all mandatory GST details and the particulars stated above are true and correct."
        )],
        ["Authorised Signatory", invoice.get("signatory", "Authorised Signatory")]
    ]

    table = Table(data, colWidths=[120, 365])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#9ca3af")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f9fafb")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    return table


def create_invoice_pdf(invoice, items, output_file):
    styles = get_styles()

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        leftMargin=32,
        rightMargin=32,
        topMargin=28,
        bottomMargin=28
    )

    elements = []

    elements.append(Paragraph("TAX INVOICE", styles["InvoiceTitle"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(invoice.get("subtitle", "Compliance Failure Test Case"), styles["InvoiceSub"]))
    elements.append(Spacer(1, 12))

    elements.append(build_header_table(invoice))
    elements.append(Spacer(1, 14))

    elements.append(build_items_table(items))
    elements.append(Spacer(1, 12))

    elements.append(build_tax_table(invoice))
    elements.append(Spacer(1, 14))

    elements.append(build_footer_table(invoice))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("This is a computer-generated invoice.", styles["InvoiceSmall"]))

    doc.build(elements)


if __name__ == "__main__":
    output_dir = Path(r"D:\Arista\accontantAI\vouching\UAT\uat_invoice_pdf_bundle_rb_systems")
    output_dir.mkdir(exist_ok=True)

    invoice = {
        "invoice_no": "EWAY-MISS-001",
        "invoice_date": "2026-04-04",
        "supplier_name": "TechCore Manufacturing",
        "supplier_city": "Bangalore",
        "supplier_gstin": "29AAACT1234F1Z1",
        "buyer_name": "RB systems",
        "buyer_gstin": "27RBSYS1234P1Z1",
        "billing_city": "Pune",
        "shipping_city": "Pune",
        "place_of_supply": "Maharashtra",
        "eway_bill_no": "",  # MISSING INTENTIONALLY
        "vehicle_no": "",
        "payment_terms": "Immediate",
        "notes": "Testing missing e-way bill detection (Value > 50k, Goods).",
        "cgst_rate": "9%",
        "sgst_rate": "9%",
        "igst_rate": "0%",
        "cgst_amount": 9450,
        "sgst_amount": 9450,
        "igst_amount": 0,
        "grand_total": 123900,
        "subtitle": "High-Value Goods (Non-Service) - Missing Eway Bill"
    }

    items = [
        {
            "description": "Enterprise Server Node v2.0",
            "hsn": "8471",  # Goods (Computers)
            "qty": 5,
            "unit": "Pcs",
            "unit_price": 21000,
            "discount": 0,
            "taxable_value": 105000
        }
    ]

    filename = "test_case_missing_eway_bill.pdf"
    create_invoice_pdf(invoice, items, output_dir / filename)
    print(f"PDF created successfully at: {output_dir / filename}")
