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
    "AI Engineer": "Build and deploy artificial intelligence models and systems.",
    "Business Analyst": "Bridge the gap between business needs and data insights.",
    "Data Engineer": "Design and maintain scalable data pipelines and infrastructure.",
    "Research Scientist": "Conduct advanced research in machine learning and AI.",
    "NLP Engineer": "Develop natural language processing models and applications.",
    "Computer Vision Engineer": "Build systems that understand images and videos.",
    "Deep Learning Engineer": "Specialize in building deep neural networks.",
    "Big Data Engineer": "Work with massive datasets using tools like Spark and Hadoop.",
    "BI Developer": "Design and develop business intelligence dashboards and reports.",
    "Software Engineer - Data": "Build backend systems to support data-heavy applications.",
    "AI Product Manager": "Lead the development and strategy of AI-driven products.",
    "Robotics Engineer": "Develop intelligent systems for robots and automation.",
    "Statistical Analyst": "Apply statistical methods to extract insights from data.",
    "MLOps Engineer": "Ensure machine learning models are deployed and monitored reliably.",
    "Quantitative Analyst": "Use math and stats to guide financial or risk decisions.",
    "Data Architect": "Design the structure of complex data systems.",
    "Knowledge Engineer": "Model domain knowledge for AI systems and expert systems."

    # Add more roles here...
}

DOMAIN_DESCRIPTIONS = {
     "Healthcare": "Domain focusing on health and medical applications.",
    "Finance": "Domain focusing on financial services and products.",
    "E-commerce": "Domain related to online retail and commerce.",
    "Education": "Domain involving learning systems, content, and analytics.",
    "Manufacturing": "Domain focusing on industrial production and automation.",
    "Retail": "Domain centered on consumer goods sales, both online and offline.",
    "Telecommunications": "Domain focused on communication networks and services.",
    "Transportation": "Domain dealing with logistics, traffic, and mobility solutions.",
    "Energy": "Domain related to energy production, distribution, and sustainability.",
    "Entertainment": "Domain focusing on movies, music, games, and media.",
    "Agriculture": "Domain applying technology in farming and food production.",
    "Real Estate": "Domain related to property buying, selling, and investment.",
    "Cybersecurity": "Domain dedicated to securing systems, networks, and data.",
    "Legal": "Domain related to law, compliance, and legal analytics.",
    "Marketing": "Domain focusing on customer behavior, targeting, and advertising.",
    "Travel & Tourism": "Domain dealing with trip planning, hospitality, and experiences.",
    "Automotive": "Domain related to vehicle manufacturing, sales, and autonomous systems.",
    "Public Sector": "Domain focused on government, policy, and public services.",
    "Logistics": "Domain dealing with supply chain management and distribution systems.",
    "Human Resources": "Domain involving talent acquisition, retention, and workforce analytics.",
      # Tech / AI / Data domains
    "Artificial Intelligence": "Domain focusing on building intelligent systems that simulate human intelligence.",
    "Machine Learning": "Domain dedicated to algorithms that improve through data and experience.",
    "Computer Science": "Domain covering theory, design, and development of software and hardware.",
    "Data Science": "Domain involving extracting knowledge and insights from structured and unstructured data.",
    "Deep Learning": "Domain specializing in neural networks with multiple layers for complex pattern recognition.",
    "Natural Language Processing": "Domain focused on enabling computers to understand and generate human language.",
    "Robotics": "Domain dealing with design, construction, and operation of robots.",
    "Computer Vision": "Domain focused on enabling machines to interpret visual information from the world.",
    "Big Data": "Domain handling large volumes of data, analytics, and scalable processing systems.",
    "Cloud Computing": "Domain related to delivering computing services over the internet.",
    "Data Engineering": "Domain focused on designing and managing data pipelines and infrastructure.",
    "Software Engineering": "Domain covering systematic design, development, testing, and maintenance of software.",
    "Information Security": "Domain concentrating on protecting data and systems from cyber threats."
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
    skill_json_path = "skills.json"
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
        top_n = min(3, len(top_5))  

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

            with st.expander(f"Rank {i+1}: {role} | {domain}"):
                role_query = role.replace(" ", "+") + "+" + domain.replace(" ", "+")
                linkedin_jobs = f"https://www.linkedin.com/jobs/search/?keywords={role_query}"
                indeed_jobs = f"https://www.indeed.com/jobs?q={role_query}"
                glassdoor_jobs = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={role_query}"
                st.markdown(
                    f"<b>{role}</b> <span title='{role_desc}' style='cursor: help;'>ℹ</span> | "
                    f"<b>{domain}</b> <span title='{domain_desc}' style='cursor: help;'>ℹ</span>",
                    unsafe_allow_html=True,
                )
                match_percent = int(score * 100)
                st.markdown(f"*Match Percentage:* {match_percent}%")
                st.progress(match_percent)

                st.markdown(f"*Explore Latest Oppurtunities:* [LinkedIn]({linkedin_jobs}) &nbsp;|&nbsp; [Glassdoor]({glassdoor_jobs}) &nbsp;|&nbsp; [Indeed]({indeed_jobs})")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"*Your Skills ({len(user)}):*")
                    st.write(", ".join(sorted([s.title() for s in user])) if user else "None")

                with col2:
                    st.markdown(f"*Required Skills ({len(required)}):*")
                    st.write(", ".join(sorted([s.title() for s in required])) if required else "Not Specified")

                with col3:
                    st.markdown(f"*Gap Skills ({len(gap)}):*")
                    if gap:
                        for skill in sorted(gap):
                            skill_title = skill.title()
                            search_url = f"https://www.google.com/search?q=learn+{skill.replace(' ', '+')}+online"
                            st.markdown(f"- 🔺 {skill_title} → [Upskill Link]({search_url})")
                    else:
                        st.success("You're well-matched for this role!")

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