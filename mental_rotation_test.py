import streamlit as st
import random
import time

# ---------------------------
# CONFIGURATION
# ---------------------------

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


# ---------------------------
# MAIN ENGINE
# ---------------------------

def run_mental_rotation_test():

    st.title("🧠 Mental Rotation Task")

    # ---------- SESSION INIT ----------

    if "mrt_initialized" not in st.session_state:
        st.session_state.mrt_initialized = True
        st.session_state.mrt_question = 0
        st.session_state.mrt_results = []
        st.session_state.mrt_randomized = random.sample(
            range(len(image_sets)), TOTAL_QUESTIONS
        )
        st.session_state.mrt_question_start = None
        st.session_state.mrt_options = None

    # ---------- COMPLETION ----------

    if st.session_state.mrt_question >= TOTAL_QUESTIONS:

        correct = sum(r["correct"] for r in st.session_state.mrt_results)
        accuracy = (correct / TOTAL_QUESTIONS) * 100
        avg_time = sum(r["time"] for r in st.session_state.mrt_results) / TOTAL_QUESTIONS
        timed_out = sum(r["timed_out"] for r in st.session_state.mrt_results)

        st.markdown("## 🧠 Task Completed")
        st.markdown("---")

        col1, col2, col3 = st.columns(3)
        col1.metric("Accuracy", f"{accuracy:.1f}%")
        col2.metric("Avg Reaction Time", f"{avg_time:.2f}s")
        col3.metric("Timed Out", f"{timed_out}/{TOTAL_QUESTIONS}")

        # Store score if needed for final stage
        st.session_state.mrt_score = accuracy

        if st.button("Continue", type="primary", use_container_width=True):

            # Clean MRT session keys
            for key in list(st.session_state.keys()):
                if key.startswith("mrt_"):
                    del st.session_state[key]

            st.session_state.current_stage = "final"
            st.rerun()

        return

    # ---------- QUESTION PHASE ----------

    if st.session_state.mrt_question_start is None:
        st.session_state.mrt_question_start = time.time()

    elapsed = time.time() - st.session_state.mrt_question_start
    remaining = max(0.0, QUESTION_TIME_LIMIT - elapsed)

    # Auto timeout
    if elapsed >= QUESTION_TIME_LIMIT:
        st.session_state.mrt_results.append({
            "correct": False,
            "time": QUESTION_TIME_LIMIT,
            "timed_out": True
        })
        st.session_state.mrt_question += 1
        st.session_state.mrt_question_start = None
        st.session_state.mrt_options = None
        st.rerun()

    # ---------- UI ----------

    st.markdown(
        f"**Question {st.session_state.mrt_question + 1} of {TOTAL_QUESTIONS}**"
    )

    progress_fraction = remaining / QUESTION_TIME_LIMIT
    timer_color = "🟢" if remaining > 3 else ("🟡" if remaining > 1.5 else "🔴")
    st.progress(progress_fraction, text=f"{timer_color} Time left: {remaining:.1f}s")

    trial_idx = st.session_state.mrt_randomized[
        st.session_state.mrt_question
    ]

    target_img, correct_img, wrong_img = image_sets[trial_idx]

    if st.session_state.mrt_options is None:
        options = [
            {"img": correct_img, "correct": True},
            {"img": wrong_img, "correct": False},
        ]
        random.shuffle(options)
        st.session_state.mrt_options = options
    else:
        options = st.session_state.mrt_options

    st.markdown("---")
    col_center = st.columns([1, 1, 1])
    with col_center[1]:
        st.image(target_img, width=175)

    st.markdown("---")
    st.markdown("### 👆 Click on the correct rotated version:")

    col1, col2 = st.columns(2)

    with col1:
        st.image(options[0]["img"], width=175)
        if st.button("Option A", key=f"mrt_a_{st.session_state.mrt_question}"):

            rt = time.time() - st.session_state.mrt_question_start

            st.session_state.mrt_results.append({
                "correct": options[0]["correct"],
                "time": rt,
                "timed_out": False
            })

            st.session_state.mrt_question += 1
            st.session_state.mrt_question_start = None
            st.session_state.mrt_options = None
            st.rerun()

    with col2:
        st.image(options[1]["img"], width=175)
        if st.button("Option B", key=f"mrt_b_{st.session_state.mrt_question}"):

            rt = time.time() - st.session_state.mrt_question_start

            st.session_state.mrt_results.append({
                "correct": options[1]["correct"],
                "time": rt,
                "timed_out": False
            })

            st.session_state.mrt_question += 1
            st.session_state.mrt_question_start = None
            st.session_state.mrt_options = None
            st.rerun()

    # Smooth refresh without blocking
    st.rerun()
