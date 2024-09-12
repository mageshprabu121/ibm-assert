import os
from dotenv import load_dotenv
import sqlite3
import re
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()
api_key = os.getenv("WATSONX_APIKEY", None)
ibm_cloud_url = os.getenv("WATSONX_URL", None)
project_id = os.getenv("WATSONX_INSTANCE_ID", None)

if api_key is None or ibm_cloud_url is None or project_id is None:
    print("Ensure you copied the .env file that you created earlier into the same directory as this notebook")
else:
    creds = {
        "url": ibm_cloud_url,
        "apikey": api_key 
    }

params = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.MAX_NEW_TOKENS: 100,
}

llm_model = Model(
    model_id='meta-llama/llama-3-70b-instruct',
    params=params,
    credentials=creds,
    project_id=project_id
)


db_path = 'assessment.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT transcript FROM assessments")
transcripts = cursor.fetchall()


sample_txt_path = 'sample.txt'
with open(sample_txt_path, 'r') as file:
    sample_text = file.read()

questions_answers = {}
pattern = r"\* Question (\d+): (.*?)\nAnswer: (.*?)(?=\n\*|$)"
matches = re.findall(pattern, sample_text, re.DOTALL)

for match in matches:
    question_number = int(match[0])
    answer_text = match[2].strip()
    questions_answers[question_number] = answer_text


tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = AutoModel.from_pretrained("distilbert-base-uncased")

def compute_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.numpy()

def cosine_similarity(embedding1, embedding2):
    dot_product = np.dot(embedding1, embedding2.T)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    return (dot_product / (norm1 * norm2)).item()


def assess_humanization(transcript, answer):
    prompt = f"Assess how human-like this response is based on the context:\n\nContext: {answer}\nResponse: {transcript}\n\nScore the response on a scale out of 100. Give only score not any explanation."
    response = llm_model.generate_text(prompt)
    
    
    match = re.search(r'(\d+)', response)
    
    if match:
        humanization_score = float(match.group(1))
    else:
        raise ValueError("Could not extract a valid score from the LLM response.")
    
    return humanization_score

total_score = 0
for i, (transcript,) in enumerate(transcripts, start=1):
    answer = questions_answers.get(i, "")
    if answer:  
        humanization_score = assess_humanization(transcript, answer)
        transcript_embedding = compute_embedding(transcript)
        answer_embedding = compute_embedding(answer)
        cosine_score = cosine_similarity(transcript_embedding, answer_embedding) * 100
        weighted_score = (humanization_score * cosine_score) / 100
        total_score += weighted_score
        print(f"Question {i} -Humanization Score: {humanization_score}, Weighted Score: {weighted_score}")
    else:
        print(f"No expected answer found for Question {i}")

final_score = total_score / len(questions_answers)
print(f"Final Score: {final_score}/100")

if final_score >= 90:
    grade = "A"
elif final_score >= 80:
    grade = "B"
elif final_score >= 70:
    grade = "C"
elif final_score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"Grade: {grade}")


SMTP_SERVER = 'smtp.gmail.com'  
SMTP_PORT = 587  
SMTP_USERNAME = 'cseskct121mageshprabu.g@gmail.com'  
SMTP_PASSWORD = 'yvqcmaxwecmxokkf' 

# def send_email(to_email, candidate_name, final_score, grade):
#     subject = "Assessment Results"
#     body = f"""
#     Dear HR,

#     We are pleased to inform you that {candidate_name}'s assessment has been completed.

#     The assessment score is {final_score}/100, and grade is {grade}.


#     Best regards,
#     The Assessment Team
#     """

#     msg = MIMEMultipart()
#     msg['From'] = SMTP_USERNAME
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))

#     try:
#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#         server.starttls()
#         server.login(SMTP_USERNAME, SMTP_PASSWORD)
#         server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
#         server.quit()
#         print(f"Email sent successfully to {to_email}")
#     except Exception as e:
#         print(f"Failed to send email to {to_email}. Error: {str(e)}")

def send_email(to_email, candidate_name, final_score, grade):
    subject = "Assessment Results"
    final_score = round(final_score)
    
    if final_score >= 60:
        assessment_result = "cleared"
    else:
        assessment_result = "not cleared"

    body = f"""
    Dear HR,

    This is to inform you that {candidate_name} has {assessment_result} the assessment.

    The assessment score is {final_score}/100, and the grade is {grade}.

    Best regards,
    The Assessment Team

    """

    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {str(e)}")


cursor.execute("SELECT name, email FROM assessments WHERE id = 1")  
candidate_info = cursor.fetchone()

if candidate_info:
    candidate_name, candidate_email = candidate_info
    send_email(candidate_email, candidate_name, final_score, grade)

conn.close()
