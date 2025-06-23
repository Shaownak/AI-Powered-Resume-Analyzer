from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        return text
    except Exception as e:
        print(f"PDF extraction failed: {e}")
        return ""


def calculate_resume_score(resume_path, job_description):
    """Calculate similarity score between resume and job description."""
    resume_text = extract_text_from_pdf(resume_path)
    if not resume_text:
        return 0.0

    documents = [resume_text, job_description]
    tfidf = TfidfVectorizer(stop_words='english')
    matrix = tfidf.fit_transform(documents)
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return round(score * 100, 2)  # Return percentage
