import streamlit as st
import time

from math_test import run_math_test
from stroop_test import run_stroop_test
from mental_rotation_test import run_mental_rotation_test

st.set_page_config(page_title="Cognitive Assessment Tool", layout="centered")


# =====================================================
# CLOUD SAFE SESSION INITIALIZATION
# =====================================================

if "current_stage" not in st.session_state:
    st.session_state.current_stage = "consent"

if "stage_lock" not in st.session_state:
    st.session_state.stage_lock = True

if "heartbeat" not in st.session_state:
    st.session_state.heartbeat = time.time()


# =====================================================
# CONSENT + DEMOGRAPHICS PAGE
# =====================================================

if st.session_state.current_stage == "consent":

    st.title("Cognitive Assessment Study")

    st.markdown("""
    ### Digital Consent

    - I confirm that I have passed 12th standard.
    - I confirm that I am computer literate.
    - I understand that the data collected will be used **only for academic purposes**.
    - My participation is voluntary and I may withdraw at any time.
    """)

    consent = st.checkbox("I agree to participate")

    st.markdown("---")
    st.markdown("### Baseline & Demographic Information")

    name = st.text_input("Name")
    age = st.selectbox("Age Category", ["18-25", "26-35", "36-45", "46-55", "56+"])
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    hometown = st.text_input("Home Town")
    current_city = st.text_input("Current City")

    mother_language = st.selectbox(
        "Mother Language",
        ["Hindi", "English", "Bengali", "Tamil", "Telugu",
         "Marathi", "Gujarati", "Kannada", "Malayalam", "Other"]
    )

    academic = st.selectbox(
        "Academic Qualification",
        ["Pursuing UG", "Pursuing PG", "Completed UG", "Completed PG"]
    )

    service = st.selectbox(
        "Service Status",
        ["Employed", "Not Employed", "Retired"]
    )

    handedness = st.selectbox(
        "Handedness",
        ["Right", "Left", "Ambidextrous"]
    )

    device = st.selectbox(
        "Device Used",
        ["Laptop", "Desktop", "Mobile", "Tablet"]
    )

    vision = st.selectbox(
        "Vision Status",
        ["Normal", "Corrected to Normal"]
    )

    prior_exposure = st.selectbox(
        "Prior exposure to any cognitive test recently?",
        ["Yes", "No"]
    )

    if st.button("Start Test"):

        if not consent:
            st.warning("You must provide consent to proceed.")
            st.stop()

        if name.strip() == "":
            st.warning("Please enter your name.")
            st.stop()

        st.session_state.demographics = {
            "name": name,
            "age": age,
            "gender": gender,
            "hometown": hometown,
            "current_city": current_city,
            "mother_language": mother_language,
            "academic": academic,
            "service": service,
            "handedness": handedness,
            "device": device,
            "vision": vision,
            "prior_exposure": prior_exposure
        }

        st.session_state.stage_lock = False
        st.session_state.current_stage = "instructions"

        st.rerun()


# =====================================================
# INSTRUCTION SCREEN
# =====================================================

elif st.session_state.current_stage == "instructions":

    st.title("Instructions")

    st.markdown("""
    You will complete **three cognitive tasks**:

    1. Math Speed Test  
    2. Stroop Test  
    3. Mental Rotation Task  

    Respond quickly and accurately.

    Click the button below to begin the assessment.
    """)

    if st.button("Continue to Test"):

        st.session_state.stage_lock = False
        st.session_state.current_stage = "math"

        st.rerun()


# =====================================================
# TEST ENGINE ROUTER
# =====================================================

elif st.session_state.current_stage == "math":
    run_math_test()

elif st.session_state.current_stage == "stroop":
    run_stroop_test()

elif st.session_state.current_stage == "mental":
    run_mental_rotation_test()


# =====================================================
# FINAL SCREEN
# =====================================================

elif st.session_state.current_stage == "final":

    st.title("Thank You for Participating!")

    st.markdown("""
    Your participation is greatly appreciated.

    The results from each test were displayed after completion.

    This data will be used strictly for academic purposes.
    """)

    st.success("You may now close this window.")


