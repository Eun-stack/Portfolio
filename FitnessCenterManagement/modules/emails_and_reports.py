# modules/email_and_reports.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def send_email(recipient, subject, body, email_sender, email_password):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_sender, email_password)

        msg = MIMEMultipart()
        msg["From"] = email_sender
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server.sendmail(email_sender, recipient, msg.as_string())
        server.quit()
        
        st.success("이메일 발송 완료!")
    except Exception as e:
        st.error(f"이메일 발송 실패: {str(e)}")

def generate_report(supabase):
    # 통계 또는 보고서 생성 예시
    st.write("통계 보고서 예시")
    data = supabase.table("pt_reservations").select("*").execute().data
    for item in data:
        st.write(item)
