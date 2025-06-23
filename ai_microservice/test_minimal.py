#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.routes import extract_text_from_pdf
from ai.scorer import calculate_resume_score

def test_pdf_extraction():
    """Test PDF extraction directly"""
    
    resume_path = "../media/resumes/BAT_CV.pdf"
    
    if not os.path.exists(resume_path):
        print(f"❌ Test file not found: {resume_path}")
        return
    
    print(f"📄 Testing PDF extraction with: {resume_path}")
    
    try:
        # Read the file
        with open(resume_path, 'rb') as f:
            file_bytes = f.read()
        
        print(f"📄 File size: {len(file_bytes)} bytes")
        
        # Test extraction
        text = extract_text_from_pdf(file_bytes)
        print(f"📝 Extracted text length: {len(text)}")
        print(f"📝 First 200 chars: {text[:200]}...")
        
        # Test scoring
        job_desc = "Software engineer with Python experience"
        score = calculate_resume_score(text, job_desc)
        print(f"🎯 Score: {score * 100:.2f}%")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_extraction()
