import streamlit as st
import tempfile
import os
import fitz  # PyMuPDF
import plotly.graph_objects as go
from export_pdf import generate_pdf_report
from extractor.Skill_extractor import extract_skills_with_exact_match
from domainn_predictor import predict_top_roles_domains, get_gap_skills
import plotly.io as pio
pio.kaleido.scope.default_format = "png"

# -------------- Dummy Role/Domain descriptions --------------
# Replace with your actual descriptions
ROLE_DESCRIPTIONS = {
    "Data Scientist": "Analyze data to gain insights and build predictive models.",
    "Machine Learning Engineer": "Develop ML models and integrate them into products.",
    "Data Analyst": "Interpret data to help make business decisions.",
    # Add more roles here...
}

DOMAIN_DESCRIPTIONS = {
    "Healthcare": "Domain focusing on health and medical applications.",
    "Finance": "Domain focusing on financial services and products.",
    "E-commerce": "Domain related to online retail and commerce.",
    # Add more domains here...
}

# ------------------ Streamlit Config ------------------ #
st.set_page_config(page_title="SkillFit: Role Matcher & Upskill Analyzer", layout="wide")

st.markdown(
    """<h1 style='text-align: center; color: #1A5276;'> SkillFit: Smart Skill Analyzer & Role Matcher</h1>
    <h3 style='text-align: center; color: #2874A6; font-weight: normal;'>
        Analyze &nbsp; | &nbsp; Match &nbsp; | &nbsp; Upskill
    </h3>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# ------------------ Sidebar Upload + Preview ------------------ #
st.sidebar.header(" Upload Resume/linkedin Profile")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=["pdf"])

def display_pdf_preview_in_sidebar(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))  # Small preview
    image_path = os.path.join(tempfile.gettempdir(), "preview.png")
    pix.save(image_path)

    with st.sidebar.expander(" Preview Uploaded Resume"):
        st.image(image_path, caption="Page 1 Preview", use_container_width=True)

# ------------------ Main Section ------------------ #
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(uploaded_file.read())
        tmp_pdf_path = tmp_pdf.name

    # Show Preview
    display_pdf_preview_in_sidebar(tmp_pdf_path)

    # Extract Skills
    skill_json_path = r"C:\Users\Asus\Documents\MDS\Internship (Kanini software solutions )\Project\skills.json"
    extracted_skills = extract_skills_with_exact_match(tmp_pdf_path, skill_json_path)
    os.remove(tmp_pdf_path)

    if extracted_skills:
        with st.expander(" View Extracted Skills", expanded=True):
            st.write(", ".join(sorted([s.title() for s in extracted_skills])))

        # Predict roles/domains
        top_5 = predict_top_roles_domains(extracted_skills)
        roles = [f"{role} | {domain}" for role, domain, _ in top_5]
        scores = [int(score * 100) for _, _, score in top_5]

        # ------------------ Enhanced Match Percentage Bar Chart ------------------ #
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=roles[::-1],
            x=scores[::-1],
            orientation='h',
            marker=dict(
                color=scores[::-1],
                colorscale='Viridis',
                line=dict(color='white', width=1.5)
            ),
            text=[f"{s}%" for s in scores[::-1]],
            textposition='outside',
            hovertemplate='%{y}<br>Match: %{x}%<extra></extra>',
        ))

        fig.update_layout(
            title=' Match Percentage for Top Predicted Roles',
            xaxis=dict(title='Match %', range=[0, 100]),
            yaxis=dict(title='Role | Domain'),
            height=420,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(250,250,250,1)',
        )

        st.plotly_chart(fig, use_container_width=True)

        # ------------ Skill Gap Insights ---------------- #
        top_n = min(3, len(top_5))  # Ensure we don’t exceed available roles

        # Prepare gap info list for report and display
        gap_info_list = []
        for i in range(top_n):
            role, domain, score = top_5[i]
            user, required, gap = get_gap_skills(extracted_skills, role, domain)
            gap_info_list.append((user, required, gap))

        st.markdown("### Skill Gap Analysis & Upskilling Suggestions")
        st.write("Explore personalized improvement areas for your top role matches:")

        for i in range(top_n):
            role, domain, score = top_5[i]
            user, required, gap = gap_info_list[i]

            role_desc = ROLE_DESCRIPTIONS.get(role, "No description available for this role.")
            domain_desc = DOMAIN_DESCRIPTIONS.get(domain, "No description available for this domain.")

            with st.expander(f" Rank {i+1}: {role} | {domain}"):
                st.markdown(
                    f"<b>{role}</b> <span title='{role_desc}' style='cursor: help;'>ℹ️</span> | "
                    f"<b>{domain}</b> <span title='{domain_desc}' style='cursor: help;'>ℹ️</span>",
                    unsafe_allow_html=True,
                )

                match_percent = int(score * 100)
                st.markdown(f" Match Percentage:** {match_percent}%")
                st.progress(match_percent)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f" *Your Skills ({len(user)}):*")
                    st.write(", ".join(sorted([s.title() for s in user])) if user else "None")

                with col2:
                    st.markdown(f" *Required Skills ({len(required)}):*")
                    st.write(", ".join(sorted([s.title() for s in required])) if required else "Not Specified")

                with col3:
                    st.markdown(f"⚠ *Gap Skills ({len(gap)}):*")
                    if gap:
                        for skill in sorted(gap):
                            skill_title = skill.title()
                            search_url = f"https://www.google.com/search?q=learn+{skill.replace(' ', '+')}+online"
                            st.markdown(f"- 🔺 {skill_title} → [Upskill Link]({search_url})")
                    else:
                        st.success(" You're well-matched for this role!")

        # --------- Downloadable Reports (implement your functions) --------- #
        # Add a Generate PDF button in the sidebar
        with st.sidebar:
            generate_pdf_btn = st.button(" Generate & Download PDF Report")

        # Generate & show download button only if user clicks
        if generate_pdf_btn:
            with st.spinner("Generating PDF report..."):
                pdf_report_path = os.path.join(tempfile.gettempdir(), "skillfit_report.pdf")
                generate_pdf_report(pdf_report_path, extracted_skills, top_5, gap_info_list)

            if os.path.exists(pdf_report_path) and os.path.getsize(pdf_report_path) > 0:
                with open(pdf_report_path, "rb") as file:
                    st.sidebar.download_button(
                        label="⬇ Download PDF Report",
                        data=file,
                        file_name="skillfit_report.pdf",
                        mime="application/pdf",
                    )
            else:
                st.sidebar.error("⚠ PDF report generation failed.")

        # col_dl1, col_dl2 = st.columns(2)
        # with col_dl1:
        #     with open(txt_report_path, "rb") as file:
        #         st.download_button(
        #             label="📥 Download TXT Report",
        #             data=file,
        #             file_name="skillfit_report.txt",
        #             mime="text/plain",
        #         )
        # with col_dl2:
        #     with open(pdf_report_path, "rb") as file:
        #         st.download_button(
        #             label="📥 Download PDF Report",
        #             data=file,
        #             file_name="skillfit_report.pdf",
        #             mime="application/pdf",
        #         )

    else:
        st.warning(" No skills could be extracted from your resume. Try uploading a different format.")
else:
    st.info(" Please upload a resume from the sidebar to begin.")