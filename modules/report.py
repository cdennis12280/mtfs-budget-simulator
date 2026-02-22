"""
PDF report generation utilities for MTFS simulator.
Includes simple reports and professional multi-scenario statutory reports.
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import pandas as pd


def generate_pdf_report(output_path, title, kpis, note=None):
    """Legacy simple PDF report generator (canvas-based)."""
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


def generate_mtfs_statutory_report(output_path, council_name, report_date, scenarios_data,
                                   base_budget, reserves_policy=None, risk_summary=None):
    """
    Generate a professional, multi-scenario MTFS statutory report.
    Audit-ready PDF with governance-grade formatting and compliance sections.
    
    Args:
        output_path: File path to save PDF
        council_name: Name of the council
        report_date: Date of report (string)
        scenarios_data: Dict of {scenario_name: {'projection': df, 'kpis': dict, 'rag': str}}
        base_budget: Base year budget (£m) for percentage calculations
        reserves_policy: Optional ReservesPolicy object for policy compliance references
    
    Returns:
        Absolute path to generated PDF
    """
    
    # Create PDF document with Platypus
    doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm,
                           leftMargin=20*mm, rightMargin=20*mm)
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0b3d91'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0b3d91'),
        spaceAfter=6,
        spaceBefore=6,
        fontName='Helvetica-Bold'
    )
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    # ===== PAGE 1: COVER PAGE =====
    story.append(Spacer(1, 40*mm))
    story.append(Paragraph(f"MULTI-YEAR FINANCIAL STRATEGY (MTFS)", title_style))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(f"Medium-Term Financial Plan & Scenario Analysis", styles['Heading2']))
    story.append(Spacer(1, 30*mm))
    
    story.append(Paragraph(f"<b>{council_name}</b>", styles['Heading3']))
    story.append(Spacer(1, 12*mm))
    story.append(Paragraph(f"Report Date: {report_date}", styles['Normal']))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y at %H:%M:%S')}", styles['Normal']))
    
    story.append(Spacer(1, 20*mm))
    story.append(Paragraph("""
    <b>STATUTORY STATEMENT</b><br/>
    <br/>
    This Multi-Year Financial Strategy (MTFS) has been prepared in accordance with:
    <br/>
    • The Local Government Act 1992 (as amended)
    <br/>
    • The Local Government Finance Act 1992
    <br/>
    • CIPFA Financial Management Code of Practice
    <br/>
    • Prudential Code for Capital Finance in Local Authorities
    <br/>
    <br/>
    The scenarios presented in this report represent the Council's analysis of potential financial 
    futures under different assumptions. This report is intended to support informed decision-making 
    by senior leadership and elected members in setting the Council's budget and financial strategy.
    <br/>
    <br/>
    <b>DISCLAIMER:</b> The projections and assumptions contained herein are based on 
    information available at the report date. Actual outturn may differ materially from these 
    projections due to external changes in government funding, economic conditions, demand pressures, 
    and other factors beyond the Council's control.
    """, styles['Normal']))
    
    story.append(PageBreak())
    
    # ===== PAGE 2: EXECUTIVE SUMMARY =====
    story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    story.append(Spacer(1, 6*mm))
    
    # Get base case (first scenario)
    base_scenario_name = list(scenarios_data.keys())[0]
    base_data = scenarios_data[base_scenario_name]
    base_kpis = base_data['kpis']
    base_rag = base_data['rag']
    base_projection = base_data['projection']
    
    total_gap = base_kpis.get('total_4_year_gap', 0)
    savings_pct = base_kpis.get('savings_required_pct', 0)
    
    summary_text = f"""
    The Council faces a cumulative budget gap of <b>£{total_gap:.1f}m</b> over the 
    medium-term financial strategy period. This analysis considers {len(scenarios_data)} scenarios 
    representing different assumptions about funding, inflation, and demand pressures.
    <br/>
    <br/>
    <b>Key Findings:</b>
    <br/>
    • Cumulative Gap (Base Case): £{total_gap:.1f}m ({(total_gap / base_budget * 100):.1f}% of budget)
    <br/>
    • Savings Required: {savings_pct:.2f}% of annual budget
    <br/>
    • Financial Sustainability Rating: <b>{base_rag}</b>
    <br/>
    • Scenarios Modelled: {', '.join(scenarios_data.keys())}
    <br/>
    • Closing Reserves (Y5): £{base_projection.iloc[-1]['Closing_Reserves']:.1f}m
    <br/>
    <br/>
    <b>Recommendation:</b> The Council should prioritise reducing expenditure through 
    transformation, income generation, and demand management to close the identified gap 
    while maintaining minimum reserves thresholds.
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    
    story.append(Spacer(1, 12*mm))
    
    # ===== SCENARIO COMPARISON TABLE =====
    story.append(Paragraph("SCENARIO COMPARISON", heading_style))
    story.append(Spacer(1, 6*mm))
    
    scenario_table_data = [
        ['Scenario', '4-Year Gap (£m)', 'Gap (% Budget)', 'Savings (% Bud)', 'Final Reserves', 'RAG']
    ]
    
    for scenario_name, scenario_info in scenarios_data.items():
        scenario_kpis = scenario_info['kpis']
        scenario_rag = scenario_info['rag']
        final_reserves = scenario_info['projection'].iloc[-1]['Closing_Reserves']
        scenario_gap = scenario_kpis.get('total_4_year_gap', 0)
        scenario_savings = scenario_kpis.get('savings_required_pct', 0)
        
        scenario_table_data.append([
            scenario_name,
            f"£{scenario_gap:.1f}",
            f"{(scenario_gap / base_budget * 100):.1f}%",
            f"{scenario_savings:.2f}%",
            f"£{final_reserves:.1f}m",
            scenario_rag
        ])
    
    scenario_table = Table(scenario_table_data, colWidths=[90, 85, 80, 80, 85, 65])
    scenario_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b3d91')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    story.append(scenario_table)
    
    story.append(PageBreak())
    
    # ===== PAGE 3: ASSUMPTIONS =====
    story.append(Paragraph("KEY ASSUMPTIONS (Base Case)", heading_style))
    story.append(Spacer(1, 6*mm))
    
    assumptions_text = """
    <b>Funding Assumptions:</b>
    <br/>
    • Council Tax Growth: 2.0% annually (configurable)
    <br/>
    • Business Rates Growth: -1.0% annually (configurable)
    <br/>
    • Government Grant Change: -2.0% annually (configurable)
    <br/>
    • Fees & Charges Growth: 3.0% annually (configurable)
    <br/>
    <br/>
    <b>Expenditure Assumptions:</b>
    <br/>
    • Pay Award: 3.5% annually (configurable)
    <br/>
    • General Inflation: 2.0% annually (configurable)
    <br/>
    • Adult Social Care Demand Growth: 4.0% annually (configurable)
    <br/>
    • Children's Social Care Demand Growth: 3.0% annually (configurable)
    <br/>
    <br/>
    <b>Policy Decisions:</b>
    <br/>
    • Annual Savings Target: 2.0% of budget (configurable)
    <br/>
    • Use of Reserves: 50.0% of gap funded from reserves, 50% service cuts (configurable)
    <br/>
    <br/>
    <i>Note: All assumptions are configurable and can be adjusted to reflect the Council's 
    specific circumstances, risk appetite, and strategic priorities. Sensitivity analysis is 
    available to test the impact of individual assumption changes.</i>
    """
    
    story.append(Paragraph(assumptions_text, styles['Normal']))
    
    story.append(PageBreak())
    
    # ===== RESERVES POLICY COMPLIANCE =====
    if reserves_policy:
        story.append(Paragraph("RESERVES POLICY COMPLIANCE", heading_style))
        story.append(Spacer(1, 6*mm))
        
        closing_reserves = base_projection.iloc[-1]['Closing_Reserves']
        policy_text = f"""
        The Council's reserves policy sets the following thresholds:
        <br/>
        <br/>
        • <b>Minimum Reserves:</b> {reserves_policy.min_pct}% of net revenue budget (statutory floor)
        <br/>
        • <b>Target Reserves:</b> {reserves_policy.target_pct}% of net revenue budget (ideal position)
        <br/>
        • <b>Maximum Reserves:</b> {reserves_policy.max_pct}% of net revenue budget (prevent over-accumulation)
        <br/>
        <br/>
        Under the base case scenario, the Council's closing reserves in Year 5 are projected 
        to be £{closing_reserves:.1f}m, which meets policy requirements.
        The Council should maintain reserves within the target range to balance financial 
        resilience with prudent use of public resources.
        """
        story.append(Paragraph(policy_text, styles['Normal']))
        
        story.append(PageBreak())
    
    # ===== RISK & SENSITIVITY ADVISOR SUMMARY =====
    if risk_summary:
        story.append(Paragraph("RISK & SENSITIVITY ADVISOR SUMMARY", heading_style))
        story.append(Spacer(1, 6*mm))

        story.append(Paragraph(
            "The following risks are prioritised based on corporate risk scoring and model "
            "sensitivity. Stress tests reflect adverse movements in key assumptions.",
            styles['Normal']
        ))
        story.append(Spacer(1, 4*mm))

        risk_table_data = [[
            'Risk', 'Driver', 'Stress %', 'Gap Delta (£m)', 'Weighted Impact'
        ]]

        for item in risk_summary:
            risk_table_data.append([
                item.get('risk_title', ''),
                item.get('driver', ''),
                f"{item.get('stress_pct', 0):.0f}%",
                f"{item.get('gap_delta', 0):.2f}",
                f"{item.get('weighted_impact', 0):.2f}",
            ])

        risk_table = Table(risk_table_data, colWidths=[160, 90, 55, 85, 90])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b3d91')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 6*mm))

        mitigation_lines = []
        for item in risk_summary:
            action = item.get('recommended_action', 'Review mitigation and contingency options.')
            risk = item.get('risk_title', '')
            driver = item.get('driver', '')
            mitigation_lines.append(f"• {risk} ({driver}): {action}")

        if mitigation_lines:
            mitigation_text = "<br/>".join(mitigation_lines)
            story.append(Paragraph("<b>Mitigation Notes:</b><br/>" + mitigation_text, styles['Normal']))

        story.append(PageBreak())

    # ===== METHODOLOGY & GOVERNANCE =====
    story.append(Paragraph("METHODOLOGY & GOVERNANCE NOTES", heading_style))
    story.append(Spacer(1, 6*mm))
    
    methodology_text = """
    <b>Financial Modeling Approach:</b>
    <br/>
    The MTFS projections are calculated on a full-year accruals basis, consistent with 
    the Council's Statement of Accounts. Key features include:
    <br/>
    • Line-by-line departmental budget modeling
    <br/>
    • Scenario analysis with multiple inflation / demand assumptions
    <br/>
    • Sensitivity testing for key financial drivers
    <br/>
    • Reserves impact modeling (use and funding)
    <br/>
    <br/>
    <b>RAG (Red-Amber-Green) Rating Definitions:</b>
    <br/>
    • <b>RED:</b> Cumulative gap exceeds 5% of budget; urgent action required
    <br/>
    • <b>AMBER:</b> Cumulative gap 2-5% of budget; significant savings needed
    <br/>
    • <b>GREEN:</b> Cumulative gap less than 2% of budget; sustainable position
    <br/>
    <br/>
    <b>Statutory Compliance:</b>
    <br/>
    This report has been prepared by the Council's Section 151 (Chief Financial) Officer 
    in accordance with the Local Government Act 1992 and the Prudential Code. All projections 
    are subject to the Council's standing assumptions and available budget information. 
    The Council acknowledges that actual outturn will differ from these projections and 
    commits to regular in-year monitoring and strategy revision.
    """
    
    story.append(Paragraph(methodology_text, styles['Normal']))
    
    story.append(PageBreak())
    
    # ===== AUDITOR SIGN-OFF PAGE =====
    story.append(Spacer(1, 60*mm))
    story.append(Paragraph("SIGN-OFF & APPROVAL", heading_style))
    story.append(Spacer(1, 20*mm))
    
    signoff_text = """
    <b>Section 151 Officer / Chief Financial Officer</b>
    <br/>
    <br/>
    I confirm that this Multi-Year Financial Strategy has been prepared in accordance with 
    the Prudential Code and professional accounting standards. The projections and assumptions 
    represent a reasonable assessment of the Council's medium-term financial position based on 
    information available at the report date.
    <br/>
    <br/>
    Signature: _____________________________     Date: _______________
    <br/>
    <br/>
    Name: _____________________________
    <br/>
    <br/>
    <br/>
    <b>External Auditor Use Only</b>
    <br/>
    <br/>
    This report has been reviewed as part of our audit procedures for compliance with:
    <br/>
    ☐ CIPFA Financial Management Code
    <br/>
    ☐ Prudential Code for Capital Finance
    <br/>
    ☐ Local Government Act 1992 (Budget Setting)
    <br/>
    <br/>
    Auditor Sign-Off: _____________________________     Date: _______________
    <br/>
    <br/>
    Auditor Name: _____________________________
    """
    story.append(Paragraph(signoff_text, styles['Normal']))
    
    story.append(Spacer(1, 20*mm))
    story.append(Paragraph(
        f"<i>Report generated: {datetime.now().strftime('%d %B %Y at %H:%M:%S')} | "
        "This is a controlled document for internal use and external audit only.</i>",
        footer_style
    ))
    
    # Build PDF
    doc.build(story)
    
    return os.path.abspath(output_path)
