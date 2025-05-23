# ---------------------- IMPORTS ----------------------
import pandas as pd
import numpy as np
import ast
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.utils.multiclass import unique_labels

# ---------------------- SKILL NORMALIZATION ----------------------
skill_mapping = {
    "ml": "machine learning", "dl": "deep learning", "ai": "artificial intelligence",
    "rest api": "rest api", "rest apis": "rest api", "restful api": "rest api",
    "restful": "rest api", "rest": "rest api", "springboot": "spring boot",
    "spring-boot": "spring boot", "apis": "api", "large language models": "llms",
    "large language model": "llms", "llm": "llms", "natural language understanding": "natural language processing",
    "natural language generation": "natural language processing", "nlp": "natural language processing",
    "Natural language processing": "natural language processing", "viz": "visualization",
    "data viz": "data visualization", "tensorflow 2.0": "tensorflow", "py": "python",
    "react": "react", "react js": "react", "react.js": "react", "js": "javascript",
    "c plus plus": "c++", "cpp": "c++", "csharp": "c#", "rdbms": "relational database",
    "sql server": "sql", "postgressql": "postgresql", "nosql db": "nosql",
    "xgboost": "gradient boosting", "gboost": "gradient boosting", "pytorch": "deep learning",
    "prompting": "prompt engineering", "prompt": "prompt engineering", "AI prompt": "prompt engineering",
    "AI prompting": "prompt engineering", "convolutional neural network": "cnn",
    "convolutional neural networks": "cnn", "convolutional neural net": "cnn",
    "convolutional neural nets": "cnn", "recurrent neural network": "rnn",
    "recurrent neural networks": "rnn", "recurrent neural net": "rnn",
    "recurrent neural nets": "rnn", "long short term memory": "lstm",
    "long short term memory networks": "lstm", "long short term memory net": "lstm",
    "Genarative adversarial networks": "gans", "Generative adversarial network": "gans",
    "ML pipeline": "ml pipelines", "MLpipeline": "ml pipelines", "MLOps": "ml ops",
    "stats": "statistics", "stat": "statistics", "maths": "mathematics", "math": "mathematics",
    "algorithm": "algorithms", "Data structures": "data structures", "Data structure": "data structures",
    "DSA": "dsa", "System designing": "system design", "System design": "system design",
    "Oops": "oop", "Object oriented programming": "oop", "Object oriented programming language": "oop"
}

def normalize_skills_list(skill_list):
    normalized = []
    for skill in skill_list:
        skill = skill.lower().strip().replace('_', ' ')
        normalized_skill = skill_mapping.get(skill, skill)
        normalized.append(normalized_skill)
    return normalized

# ---------------------- LOAD DATA ----------------------
dataset_path = "final.csv"
df = pd.read_csv(dataset_path)

# Remove duplicates
df.drop_duplicates(inplace=True)

# Convert stringified list to actual list and normalize each skill
df['Skills'] = df['Skills'].apply(ast.literal_eval)
df['Skills'] = df['Skills'].apply(normalize_skills_list)

# Join normalized list back to space-separated string for vectorizer
df['Skills_str'] = df['Skills'].apply(lambda x: ' '.join(x))

# ---------------------- LABEL ENCODING ----------------------
df['Combined_Label'] = df['Role'].str.strip() + " || " + df['Domain'].str.strip()
le_combined = LabelEncoder()
df['Combined_encoded'] = le_combined.fit_transform(df['Combined_Label'])

# ---------------------- VECTORIZATION ----------------------
vectorizer = TfidfVectorizer(ngram_range=(1, 3))
X = vectorizer.fit_transform(df['Skills_str'])
y_combined = df['Combined_encoded']

# ---------------------- TRAIN-TEST SPLIT ----------------------
X_train, X_test, y_train, y_test = train_test_split(X, y_combined, test_size=0.2, random_state=42)

# ---------------------- MODEL TRAINING ----------------------
model = RandomForestClassifier(n_estimators=150, random_state=42)
model.fit(X_train, y_train)

# ---------------------- EVALUATION ----------------------
y_pred = model.predict(X_test)
labels_in_test = unique_labels(y_test, y_pred)
target_names = le_combined.inverse_transform(labels_in_test)
print(classification_report(y_test, y_pred, labels=labels_in_test, target_names=target_names))

# ---------------------- INFERENCE & GAP SKILL ANALYSIS ----------------------

def predict_top_roles_domains(user_skills, top_n=5):
    # Normalize and join for prediction
    normalized_skills = normalize_skills_list(user_skills)
    input_str = ' '.join(normalized_skills)
    input_vector = vectorizer.transform([input_str])

    # Predict probabilities
    probs = model.predict_proba(input_vector)[0]
    top_indices = np.argsort(probs)[-top_n:][::-1]

    predictions = []
    for idx in top_indices:
        combined_label = le_combined.inverse_transform([idx])[0]
        role, domain = combined_label.split(" || ")
        predictions.append((role, domain, probs[idx]))
    return predictions

def get_gap_skills(user_skills, role, domain):
    user_set = set(normalize_skills_list(user_skills))

    # Filter matching role+domain rows
    filtered = df[(df['Role'].str.lower() == role.lower()) & (df['Domain'].str.lower() == domain.lower())]
    if filtered.empty:
        return user_set, set(), set()

    required = set()
    for skills in filtered['Skills']:
        required.update(skills)

    gap = required - user_set
    return user_set, required, gap

def analyze_gap_for_top_n(user_skills, predictions, top_n=3):
    for i, (role, domain, score) in enumerate(predictions[:top_n], start=1):
        user, required, gap = get_gap_skills(user_skills, role, domain)
        print(f"Rank {i}: Role = {role} | Domain = {domain} | Confidence = {score:.3f}")
        print(f"Your Skills ({len(user)}): {sorted(user)}")
        print(f"Required Skills ({len(required)}): {sorted(required)}")
        print(f"Gap Skills ({len(gap)}): {sorted(gap)}")
        print("-" * 50)

# ---------------------- TEST EXAMPLE ----------------------
# user_skills = ['Python', 'Deep Learning', 'Feature Engineering', 'HRIS', 'CRM']

# top_5 = predict_top_roles_domains(user_skills, top_n=5)

# print("Top 5 predicted Role + Domain with confidence scores:")
# for i, (role, domain, score) in enumerate(top_5, start=1):
#     print(f"{i}. {role} || {domain} --> Score: {score:.3f}")

# print("\nGap Skill Analysis for top 3 predictions:\n")
# analyze_gap_for_top_n(user_skills, top_5, top_n=3)
