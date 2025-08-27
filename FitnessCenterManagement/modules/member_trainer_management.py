# modules/member_trainer_management.py
import streamlit as st
from datetime import datetime, timedelta  # timedelta 추가
from supabase import create_client

def load_members(supabase):
    return supabase.table("members").select("*").execute().data or []

def load_trainers(supabase):
    return supabase.table("trainers").select("*").execute().data or []

def manage_members(supabase):
    st.header("회원 관리")
    members = load_members(supabase)

    if not members:
        st.write("등록된 회원이 없습니다.")
    else:
        for m in members:
            st.write(f"- {m['name']} / 전화: {m['phone']} / 이메일: {m.get('email', '없음')} / 등록일: {m['membership_registration']} / 만료일: {m['membership_expiration']}")

    membership_levels = ["실버", "골드", "플래티넘", "다이아몬드"]
    st.subheader("회원 등록")

    with st.form("member_form"):
        name = st.text_input("이름")
        phone = st.text_input("전화번호 (010xxxxxxxx)")
        email = st.text_input("이메일")
        reg_date = st.date_input("등록일", datetime.today())
        exp_date = st.date_input("만료일", datetime.today() + timedelta(days=30))
        membership_level = st.selectbox("멤버십 등급", membership_levels, index=0)
        submitted = st.form_submit_button("등록")

        if submitted:
            if exp_date < reg_date:
                st.error("만료일은 등록일 이후여야 합니다.")
            else:
                try:
                    # 회원 정보 삽입
                    supabase.table("members").insert({
                        "name": name,
                        "phone": phone,
                        "email": email,
                        "membership_registration": reg_date.isoformat(),
                        "membership_expiration": exp_date.isoformat(),
                        "membership_level": membership_level
                    }).execute()
                    st.success("회원 등록 완료")
                except Exception as e:
                    st.error(f"회원 등록 실패: {str(e)}")

def manage_trainers(supabase):
    st.header("트레이너 관리")
    trainers = load_trainers(supabase)

    if not trainers:
        st.write("등록된 트레이너가 없습니다.")
    else:
        for t in trainers:
            st.write(f"- {t['name']} / 전화: {t['phone']} / 계약: {t['contract_start']} ~ {t['contract_end']}")

    st.subheader("트레이너 등록")
    with st.form("trainer_form"):
        name = st.text_input("이름")
        phone = st.text_input("전화번호")
        contract_start = st.date_input("계약 시작일", datetime.today())
        contract_end = st.date_input("계약 종료일", datetime.today() + timedelta(days=365))
        submitted = st.form_submit_button("등록")

        if submitted:
            if contract_end < contract_start:
                st.error("계약 종료일은 시작일 이후여야 합니다.")
            else:
                try:
                    # 트레이너 정보 삽입
                    supabase.table("trainers").insert({
                        "name": name,
                        "phone": phone,
                        "contract_start": contract_start.isoformat(),
                        "contract_end": contract_end.isoformat()
                    }).execute()
                    st.success("트레이너 등록 완료")
                except Exception as e:
                    st.error(f"트레이너 등록 실패: {str(e)}")
