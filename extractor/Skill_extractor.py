# extractor/skill_extractor.py
import fitz  # PyMuPDF
import json
import re
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text

def normalize_text(text):
    text = text.replace('|', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def normalize_skill(skill):
    return re.sub(r'\s+', ' ', skill).strip().lower()

def load_skills_from_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(data.get('skills', []))

def extract_skills_with_exact_match(pdf_path, json_path):
    text = extract_text_from_pdf(pdf_path)
    skill_set = load_skills_from_json(json_path)
    normalized_text = normalize_text(text)

    found_skills = set()
    for skill in skill_set:
        normalized_skill = normalize_skill(skill)
        if len(normalized_skill.split()) == 1:
            if re.search(r'\b' + re.escape(normalized_skill) + r'\b', normalized_text):
                found_skills.add(skill)
        else:
            if normalized_skill in normalized_text:
                found_skills.add(skill)

    return sorted(found_skills)