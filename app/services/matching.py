from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def match(resume, job_desc):
    texts = [resume, job_desc]
    
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform(texts)
    
    score = cosine_similarity(vectors[0], vectors[1])
    
    return float(score[0][0])