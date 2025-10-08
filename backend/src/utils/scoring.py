import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

# Simple heuristic scoring based on job title and industry
def score_lead_simple(lead):
    score = 0.5  # base score
    if 'ceo' in lead.job_title.lower() or 'founder' in lead.job_title.lower():
        score += 0.3
    if 'tech' in lead.industry.lower() if lead.industry else False:
        score += 0.2
    return min(score, 1.0)

# More advanced: train a simple model (mock, since no training data)
# For demo, use TF-IDF on job title
vectorizer = TfidfVectorizer()
model = LogisticRegression()

# Mock training data
titles = ["CEO", "CTO", "Sales Manager", "Intern"]
labels = [1, 1, 0, 0]  # 1 for high potential
vectorizer.fit(titles)
model.fit(vectorizer.transform(titles), labels)

def score_lead_ai(lead):
    vec = vectorizer.transform([lead.job_title])
    prob = model.predict_proba(vec)[0][1]
    return prob

def score_leads(leads):
    for lead in leads:
        lead.score = score_lead_ai(lead)
    return leads