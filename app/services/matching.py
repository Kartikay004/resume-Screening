from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def match(resume, job_desc):
    tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1,2))
    vectors = tfidf.fit_transform([resume, job_desc])
    score = cosine_similarity(vectors[0], vectors[1])
    return float(score[0][0])
