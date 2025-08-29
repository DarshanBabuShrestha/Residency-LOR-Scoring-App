from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import io, re

# PDF and DOCX extraction
from PyPDF2 import PdfReader
from docx import Document

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs])

def score_patient_care(text: str) -> int:
    text = text.lower()
   
    if re.search(r"(exceptional care|remarkable bedside|trusted by patients|compassion|outstanding clinician|stellar performance|technical skills surpassed|medical judgment consistently sound|top [0-9]+%|strongest intern)", text):
        return 95
 
    elif re.search(r"(good care|solid clinical skills|performed well|reliable clinician|strong clinical ability)", text):
        return 75
  
    elif re.search(r"(adequate clinical|meets expectations|satisfactory performance|no major issues)", text):
        return 50
 
    else:
        return 30


def score_medical_knowledge(text: str) -> int:
    text = text.lower()
    if re.search(r"(extraordinary|exceptional|brilliant|outstanding|top \d+%|fund of knowledge)", text):
        return 100
    elif re.search(r"(strong|solid|very good|good knowledge)", text):
        return 75
    elif re.search(r"(adequate|meets expectations)", text):
        return 50
    else:
        return 30

def score_interpersonal(text: str) -> int:
    text = text.lower()
    if re.search(r"(exceptional communicator|natural leader|works extremely well with team|universally respected)", text):
        return 90
    elif re.search(r"(gets along|quiet but effective|team player)", text):
        return 60
    elif re.search(r"(neutral mention only|no mention teamwork)", text):
        return 35
    else:
        return 30

def score_professionalism(text: str) -> int:
    text = text.lower()
    # Exceptional professionalism / work ethic
    if re.search(r"(unfailingly dependable|tireless|resilient|always prepared|never compromising|highest praise|remarkable dedication|exceptional work ethic|adaptability|consistently reliable|outstanding professionalism)", text):
        return 95
    # Strong / good
    elif re.search(r"(hard worker|diligent|professional|meets expectations|dependable|punctual|well prepared|trustworthy)", text):
        return 75
    # Adequate / neutral
    elif re.search(r"(adequate|neutral mention|satisfactory)", text):
        return 50
    # Weak / omitted
    else:
        return 30

def score_scholarly(text: str) -> int:
    text = text.lower()
    # High-level scholarly achievement
    if re.search(r"(published|first[- ]author|peer[- ]reviewed journal|presented at national conference|hhmi fellowship|funded research|annals of surgery|manuscript accepted|led initiative|grant awarded)", text):
        return 100
    # Moderate scholarly involvement
    elif re.search(r"(poster presentation|local conference|active in lab|volunteered consistently|teaching assistant|case report|department presentation)", text):
        return 75
    # Basic involvement
    elif re.search(r"(involved in research|did volunteer work|interest group|small project|helped with study)", text):
        return 55
    # None mentioned
    else:
        return 30

def score_author_credibility(text: str) -> int:
    text = text.lower()
    if "program director" in text or "chair" in text:
        return 100
    elif "professor" in text or "associate professor" in text:
        return 90
    elif "assistant professor" in text:
        return 70
    elif "community physician" in text:
        return 50
    elif "international" in text or "outside the us" in text:
        return 30
    else:
        return 40

def detect_deductions(text: str) -> int:
    text = text.lower()
    tier1, tier2, tier3 = 0, 0, 0

    if re.search(r"(unsafe|cannot recommend|unethical|serious professionalism issue)", text):
        return -80

    if re.search(r"(needed constant supervision|unreliable|recommend with reservations|frequent absences)", text):
        tier2 += 1

    if re.search(r"(showed improvement|performed at expected level|quiet in discussions|minor issue)", text):
        tier3 += 1

    deduction = 0
    if tier2 >= 2:
        deduction = -60
    elif tier2 == 1:
        deduction = -40

    if tier3 >= 3:
        deduction = -50
    elif tier3 > 0:
        deduction += -20

    if tier2 > 0 and tier3 > 0 and deduction < -50:
        deduction = -50

    return deduction


def score_lor_text(text: str) -> dict:
    patient_care = score_patient_care(text)
    medical_knowledge = score_medical_knowledge(text)
    interpersonal = score_interpersonal(text)
    professionalism = score_professionalism(text)
    scholarly = score_scholarly(text)
    author_credibility = score_author_credibility(text)
    deductions = detect_deductions(text)

    final_score = int(round(
        (patient_care + medical_knowledge + interpersonal + professionalism + scholarly + author_credibility) / 6 + deductions
    ))

    return {
        "patient_care": patient_care,
        "medical_knowledge": medical_knowledge,
        "interpersonal": interpersonal,
        "professionalism": professionalism,
        "scholarly": scholarly,
        "author_credibility": author_credibility,
        "deductions": deductions,
        "final_score": final_score
    }


@app.post("/score-lor")
async def score_lor(
    lor_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    if file:
        contents = await file.read()
        if file.filename.lower().endswith(".pdf"):
            lor_text = extract_text_from_pdf(contents)
        elif file.filename.lower().endswith(".docx"):
            lor_text = extract_text_from_docx(contents)
        else:
            return JSONResponse({"error": "Unsupported file type."}, status_code=400)
    elif not lor_text:
        return JSONResponse({"error": "No input provided."}, status_code=400)

    result = score_lor_text(lor_text)
    return result
