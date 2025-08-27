# modules/reservation_management.py
import streamlit as st
from datetime import datetime, timedelta
from supabase import create_client

def load_members(supabase):
    return supabase.table("members").select("*").execute().data or []

def load_trainers(supabase):
    return supabase.table("trainers").select("*").execute().data or []

def add_pt_reservation(supabase, trainer_id, member_id, start_dt, end_dt):
    supabase.table("pt_reservations").insert({
        "trainer_id": trainer_id,
        "member_id": member_id,
        "reservation_start": start_dt.isoformat(),
        "reservation_end": end_dt.isoformat()
    }).execute()
    st.success("PT 예약 등록 완료")

def get_trainer_schedule(supabase, trainer_id, start_date, end_date):
    schedule = supabase.table("pt_reservations")\
        .select("reservation_start, reservation_end")\
        .eq("trainer_id", trainer_id)\
        .gte("reservation_start", start_date.isoformat())\
        .lte("reservation_end", end_date.isoformat())\
        .execute().data

    return schedule

def manage_gym_logs(supabase):
    st.header("헬스장 출입 기록 등록")
    members = load_members(supabase)
    member_map = {m['name']: m['member_id'] for m in members}

    selected_member_reg = st.selectbox("회원 선택 (등록용)", list(member_map.keys()))
    check_in_date = st.date_input("입장 날짜", datetime.today())
    check_in_time = st.time_input("입장 시간", time(9, 0))
    check_out_date = st.date_input("퇴장 날짜", datetime.today())
    check_out_time = st.time_input("퇴장 시간", time(10, 0))

    check_in = datetime.combine(check_in_date, check_in_time)
    check_out = datetime.combine(check_out_date, check_out_time)

    if st.button("저장"):
        if check_out < check_in:
            st.error("퇴장 시간은 입장 시간 이후여야 합니다.")
        else:
            supabase.table("gym_logs").insert({
                "member_id": member_map[selected_member_reg],
                "check_in_time": check_in.isoformat(),
                "check_out_time": check_out.isoformat()
            }).execute()
            st.success("출입 기록 저장 완료")
