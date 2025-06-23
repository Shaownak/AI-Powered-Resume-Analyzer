from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_resume_score(resume_text: str, job_description: str) -> float:
    """Calculate similarity score between resume and job description using TF-IDF."""
    try:
        # Clean and preprocess text
        resume_text = resume_text.strip().lower()
        job_description = job_description.strip().lower()

        if not resume_text or not job_description:
            return 0.0

        documents = [resume_text, job_description]
        tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        matrix = tfidf.fit_transform(documents)
        score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return float(score)
    except Exception:
        return 0.0
