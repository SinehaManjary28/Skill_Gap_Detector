# SkillFit: Smart Skill Analyzer & Role Matcher

SkillFit is a smart web-based tool that analyzes a user's resume or LinkedIn profile (PDF format), extracts their skills, and predicts the top 5 job roles they’re most suited for – along with the match percentage and upskilling guidance.

It’s designed to help users understand their current strengths, discover suitable career paths, identify skill gaps, and receive personalized learning resources – all in one place.

Live App: [https://skill-fit.streamlit.app/](https://skill-fit.streamlit.app/)

---

## Features

- Upload LinkedIn PDF or Resume
- Skill Extraction using NLP
- Predicts Top 5 Job Roles based on your skills
- Visualizes Role Match Percentage using graphs
- Shows missing skills for top 3 matched roles
- Provides upskilling links (courses/resources)
- Shares job openings from LinkedIn, Indeed, and Glassdoor
- Downloadable skill analysis report

---

## How It Works

1. Upload a resume or LinkedIn profile PDF
2. Extract skills using text processing and NLP
3. Match with a curated job role-skill dataset (synthetic)
4. Predict top 5 job roles using a trained Random Forest classifier (97% accuracy)
5. Display results including visual graph, match scores, missing skills, learning links, and job links
6. Download report with all findings

---

## Tech Stack

- Python  
- Machine Learning (Random Forest, SVM, Logistic Regression)  
- Natural Language Processing (NLP)  
- Streamlit  
- Pandas, Scikit-learn, Matplotlib  
- PDF Parsing with PyMuPDF

---

## Dataset

We used a synthetic dataset that includes job roles, domains, and associated skillsets curated from various online job portals and job descriptions. This dataset was used to train and test the machine learning models.

---

## Try It Out

You can try the live app here:  
[https://skill-fit.streamlit.app/](https://skill-fit.streamlit.app/)

---

## Screenshots
![Screenshot 2025-05-23 150418](https://github.com/user-attachments/assets/477c0525-62f0-4205-a006-6cb70fa0f522)
![Screenshot 2025-05-23 150453](https://github.com/user-attachments/assets/a58790fe-72e3-4637-9b6c-2de09ccefc73)
![Screenshot 2025-05-23 150511](https://github.com/user-attachments/assets/426c45b7-ee8f-4a75-a0ef-7ac7f47e4876)
![Screenshot 2025-05-23 151334](https://github.com/user-attachments/assets/cc90ece2-9f0c-4cc8-b66c-3cec4a211bbe)


## Contact

If you have any questions, suggestions, or would like to collaborate, feel free to reach out.

- *Name*: Sineha Manjary R.
- *Email*: [sinehamanjary@gmail.com]
- *LinkedIn*: [https://www.linkedin.com/in/sineha-manjary/](https://www.linkedin.com/in/sineha-manjary/))
- *Project Demo*: [https://skill-fit.streamlit.app](https://skill-fit.streamlit.app)
