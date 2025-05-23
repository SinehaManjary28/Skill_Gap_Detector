import os
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile


def generate_pdf_report(pdf_path, extracted_skills, top_5, gap_info_list):
    """
    Generate a PDF report with skill analysis and visualizations.
    Uses matplotlib for reliable chart generation instead of Plotly.
    """
    # Create PDF object with default Latin-1 encoding (FPDF limitation)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "SkillFit Report", ln=True, align='C')

    # Extracted Skills
    pdf.set_font("Arial", 'B', 12)
    pdf.ln(5)
    pdf.cell(0, 10, "Extracted Skills:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, ", ".join(sorted([s.title() for s in extracted_skills])))
    pdf.ln(5)

    # Create chart with matplotlib (more reliable than Plotly for PDF embedding)
    roles = [f"{role} | {domain}" for role, domain, _ in top_5]
    scores = [int(score * 100) for _, _, score in top_5]
    
    # Create temporary file for the chart
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        chart_path = tmp.name
        
        try:
            plt.figure(figsize=(10, 6))
            # Horizontal bar chart
            plt.barh(roles[::-1], scores[::-1], color='teal')
            plt.xlabel('Match %')
            plt.title('Match Percentage for Top Predicted Roles')
            plt.xlim(0, 100)
            # Add percentage labels
            for i, v in enumerate(scores[::-1]):
                plt.text(v + 1, i, f"{v}%")
                
            plt.tight_layout()
            plt.savefig(chart_path, dpi=150)
            plt.close()
            
            # Add image to PDF
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Top Role Match Percentages:", ln=True)
            pdf.image(chart_path, x=10, w=pdf.w - 20)
            pdf.ln(10)
            
        except Exception as e:
            # Fallback if image creation fails
            pdf.cell(0, 10, f"Chart generation failed: {str(e)}", ln=True)
            print(f"Chart error: {str(e)}")
        finally:
            # Clean up temp file
            try:
                os.unlink(chart_path)
            except:
                pass

    # Skill Gap Analysis
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Skill Gap Analysis & Upskilling Suggestions:", ln=True)
    
    top_n = min(3, len(top_5))
    for i in range(top_n):
        role, domain, score = top_5[i]
        user, required, gap = gap_info_list[i]

        pdf.set_font("Arial", 'B', 12)
        # Using standard hyphen instead of em dash to avoid encoding issues
        pdf.cell(0, 10, f"Rank {i+1}: {role} | {domain} - Match: {int(score * 100)}%", ln=True)
        pdf.set_font("Arial", size=10)

        pdf.cell(0, 8, f"Your Skills ({len(user)}):", ln=True)
        pdf.multi_cell(0, 7, ", ".join(sorted([s.title() for s in user])) or "None")
        
        pdf.cell(0, 8, f"Required Skills ({len(required)}):", ln=True)
        pdf.multi_cell(0, 7, ", ".join(sorted([s.title() for s in required])) or "Not Specified")
        
        pdf.cell(0, 8, f"Gap Skills ({len(gap)}):", ln=True)
        if gap:
            for skill in sorted(gap):
                pdf.cell(0, 7, f"- {skill.title()}", ln=True)
        else:
            pdf.cell(0, 7, "You're well-matched for this role!", ln=True)
        pdf.ln(5)

    # Save PDF
    try:
        pdf.output(pdf_path)
        print(f"PDF saved successfully to {pdf_path}")
        return True
    except Exception as e:
        print(f"Error saving PDF: {str(e)}")
        return False