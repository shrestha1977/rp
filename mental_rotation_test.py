import streamlit as st
import random
import time

image_sets = [
    ("images/target1.png", "images/correct1.png", "images/wrong1.png"),
    ("images/target2.png", "images/correct2.png", "images/wrong2.png"),
    ("images/target3.png", "images/correct3.png", "images/wrong3.png"),
    ("images/target4.png", "images/correct4.png", "images/wrong4.png"),
    ("images/target5.png", "images/correct5.png", "images/wrong5.png"),
    ("images/target6.png", "images/correct6.png", "images/wrong6.png"),
    ("images/target7.png", "images/correct7.png", "images/wrong7.png"),
    ("images/target8.png", "images/correct8.png", "images/wrong8.png"),
    ("images/target9.png", "images/correct9.png", "images/wrong9.png"),
    ("images/target10.png", "images/correct10.png", "images/wrong10.png"),
    ("images/target11.png", "images/correct11.png", "images/wrong11.png"),
    ("images/target12.png", "images/correct12.png", "images/wrong12.png"),
    ("images/target13.png", "images/correct13.png", "images/wrong13.png"),
    ("images/target14.png", "images/correct14.png", "images/wrong14.png"),
    ("images/target15.png", "images/correct15.png", "images/wrong15.png"),
]

TOTAL_QUESTIONS = 15
QUESTION_TIME_LIMIT = 10


# ================= TIMER MODEL =================

def safe_elapsed(start_time):
    if start_time is None:
        return 0
    return max(0, time.time() - start_time)


# ================= MAIN TEST ENGINE =================

def run_mental_rotation_test():

    st.title("🧠 Mental Rotation Task")

    # ---------- Session Initialization ----------

    if "mrt_initialized" not in st.session_state:
        st.session_state.mrt_initialized = True
        st.session_state.mrt_question = 0
        st.session_state.mrt_results = []
        st.session_state.mrt_question_start = None
        st.session_state.mrt_randomized = random.sample(
            range(len(image_sets)), TOTAL_QUESTIONS
        )
        st.session_state.mrt_options = None

    def record_answer(is_correct, timed_out=False):

        if st.session_state.mrt_question_start is None:
            return

        question_time = safe_elapsed(st.session_state.mrt_question_start)

        st.session_state.mrt_results.append({
            "correct": is_correct,
            "time": question_time,
            "timed_out": timed_out
        })

        st.session_state.mrt_question += 1
        st.session_state.mrt_question_start = None
        st.session_state.mrt_options = None

    # ---------- Completion Phase ----------

    if st.session_state.mrt_question >= TOTAL_QUESTIONS:

        correct_count = sum(
            1 for r in st.session_state.mrt_results if r["correct"]
        )

        accuracy = (correct_count / TOTAL_QUESTIONS) * 100

        avg_time = sum(
            r["time"] for r in st.session_state.mrt_results
        ) / TOTAL_QUESTIONS if len(st.session_state.mrt_results) > 0 else 0

        timed_out = sum(
            1 for r in st.session_state.mrt_results if r["timed_out"]
        )

        st.markdown("## 🧠 Mental Rotation Results")

        col1, col2, col3 = st.columns(3)

        col1.metric("Accuracy", f"{accuracy:.1f}%")
        col2.metric("Avg Reaction Time", f"{avg_time:.2f}s")
        col3.metric("Timed Out", f"{timed_out}/{TOTAL_QUESTIONS}")

        st.session_state.mrt_score = accuracy

        if st.button("Finish Assessment"):

            for key in [
                "mrt_initialized",
                "mrt_question",
                "mrt_results",
                "mrt_question_start",
                "mrt_randomized",
                "mrt_options",
            ]:
                st.session_state.pop(key, None)

            st.session_state.current_stage = "final"
            st.rerun()

        return

    # ---------- Question Phase ----------

    if st.session_state.mrt_question_start is None:
        st.session_state.mrt_question_start = time.time()

    elapsed = safe_elapsed(st.session_state.mrt_question_start)

    remaining = max(0, QUESTION_TIME_LIMIT - elapsed)

    st.markdown(
        f"### Question {st.session_state.mrt_question + 1} / {TOTAL_QUESTIONS}"
    )

    st.progress(remaining / QUESTION_TIME_LIMIT)

    # Timeout handling
    if elapsed >= QUESTION_TIME_LIMIT:
        record_answer(False, timed_out=True)
        st.rerun()
        return

    trial_idx = st.session_state.mrt_randomized[
        st.session_state.mrt_question
    ]

    target_img, correct_img, wrong_img = image_sets[trial_idx]

    if st.session_state.mrt_options is None:
        options = [
            {"img": correct_img, "correct": True},
            {"img": wrong_img, "correct": False}
        ]
        random.shuffle(options)
        st.session_state.mrt_options = options
    else:
        options = st.session_state.mrt_options

    st.image(target_img, width=200)

    col1, col2 = st.columns(2)

    with col1:
        st.image(options[0]["img"], width=200)
        if st.button("Option A"):
            record_answer(options[0]["correct"])
            st.rerun()

    with col2:
        st.image(options[1]["img"], width=200)
        if st.button("Option B"):
            record_answer(options[1]["correct"])
            st.rerun()
