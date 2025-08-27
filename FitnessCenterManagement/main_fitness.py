# main_fitness.py
import streamlit as st
from supabase import create_client, Client
from modules.member_trainer_management import manage_members, manage_trainers
from modules.reservation_management import add_pt_reservation, get_trainer_schedule, manage_gym_logs
from modules.emails_and_reports import send_email, generate_report
import uuid
# 환경변수
import os
from dotenv import load_dotenv

#---------- 로컬에서 streamlit 실행 ----------
# cd 97-develop/FitnessCenterManagement
# streamlit run main_fitness.py

#---------- .env 파일 로드 ----------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

email_sender = os.getenv("GMAIL_EMAIL")
email_password = os.getenv("GMAIL_APP_PASSWORD")
smtp_server = os.getenv("SMTP_SERVER")


# 사이드바 메뉴
menu = st.sidebar.selectbox("메뉴 선택", ["회원 및 트레이너 관리", "예약 및 출입 관리", "이메일 발송 및 통계"])

# 메뉴에 맞는 기능 호출
if menu == "회원 및 트레이너 관리":
    st.header("회원 및 트레이너 관리")
    manage_members(supabase)
    manage_trainers(supabase)
    
elif menu == "예약 및 출입 관리":
    st.header("예약 및 출입 관리")
    add_pt_reservation(supabase)
    get_trainer_schedule(supabase)
    manage_gym_logs(supabase)
    
elif menu == "이메일 발송 및 통계":
    st.header("이메일 발송 및 통계")
    send_email("recipient@example.com", "Test Subject", "Test Body", "your_email", "your_password")
    generate_report(supabase)
