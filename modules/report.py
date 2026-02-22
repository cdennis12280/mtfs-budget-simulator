"""
Simple PDF report generation utilities for MTFS simulator.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


def generate_pdf_report(output_path, title, kpis, note=None):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    x_margin = 20 * mm
    y = height - 30 * mm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_margin, y, title)
    y -= 10 * mm

    c.setFont("Helvetica", 10)
    if note:
        c.drawString(x_margin, y, note)
        y -= 8 * mm

    # KPIs
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, y, "Headline KPIs")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    for k, v in kpis.items():
        text = f"{k}: {v}"
        c.drawString(x_margin, y, text)
        y -= 6 * mm
        if y < 30 * mm:
            c.showPage()
            y = height - 30 * mm

    c.showPage()
    c.save()
    return os.path.abspath(output_path)
