import streamlit as st
import random
import time
import pandas as pd
from streamlit_autorefresh import st_autorefresh

TOTAL_QUESTIONS = 42
TIME_LIMIT = 5

COLORS = {
    "RED": "red",
    "GREEN": "green",
    "BLUE": "blue",
    "YELLOW": "yellow"
}

NEUTRAL_WORDS = ["DOG", "CAR", "TREE", "HOUSE"]


# ================= QUESTION ENGINE =================

def generate_question():
    q_type = random.choice(["congruent", "incongruent", "neutral"])

    if q_type == "neutral":
        word = random.choice(NEUTRAL_WORDS)
        color = random.choice(list(COLORS.values()))
        return word, color, "Neutral"

    word = random.choice(list(COLORS.keys()))

    if q_type == "congruent":
        color = COLORS[word]
        condition = "Congruent"
    else:
        color = random.choice([c for c in COLORS.values() if c != COLORS[word]])
        condition = "Incongruent"

    return word, color, condition


def record_response(results, q_no, word, color, condition, answer, correct, rt):
    results.append({
        "Question": q_no,
        "Word": word,
        "Font Color": color,
        "Condition": condition,
        "Response": answer if answer else "No Response",
        "Correct": correct,
        "Reaction Time (s)": rt
    })


def next_question():
    st.session_state.q_index += 1
    st.session_state.start_time = time.time()
    st.session_state.answered = False

    (
        st.session_state.word,
        st.session_state.color,
        st.session_state.condition
    ) = generate_question()


# ================= MAIN ENGINE =================

def run_stroop_test():

    st.title("🧠 Stroop Color–Word Test")

    # -------- SESSION INIT --------

    if "stroop_started" not in st.session_state:
        st.session_state.stroop_started = False

    if "q_index" not in st.session_state:
        st.session_state.q_index = 1

    if "results" not in st.session_state:
        st.session_state.results = []

    if "answered" not in st.session_state:
        st.session_state.answered = False

    # -------- START --------

    if not st.session_state.stroop_started:

        st.subheader("📋 Instructions")
        st.write("""
- Select the COLOR of the text, not the word.
- Some words may not represent colors.
- Each question has 5 seconds.
- Total questions: 42
""")

        if st.button("▶️ Start Test"):

            st.session_state.stroop_started = True
            st.session_state.q_index = 1
            st.session_state.results = []
            st.session_state.start_time = time.time()

            (
                st.session_state.word,
                st.session_state.color,
                st.session_state.condition
            ) = generate_question()

            st.session_state.answered = False
            st.rerun()

        return

    # -------- FINISH --------

    if st.session_state.q_index > TOTAL_QUESTIONS:

        st.success("✅ Test Completed")

        df = pd.DataFrame(st.session_state.results)

        total_trials = len(df)
        total_errors = total_trials - df["Correct"].sum()
        error_rate = (total_errors / total_trials) * 100 if total_trials > 0 else 0

        df_correct = df[df["Correct"] == True]

        mean_rt = df_correct["Reaction Time (s)"].dropna().mean()

        cong_rt = df_correct[df_correct["Condition"] == "Congruent"]["Reaction Time (s)"].mean()
        incong_rt = df_correct[df_correct["Condition"] == "Incongruent"]["Reaction Time (s)"].mean()

        stroop_effect = None
        if pd.notna(cong_rt) and pd.notna(incong_rt):
            stroop_effect = incong_rt - cong_rt

        st.subheader("📊 Performance Metrics")

        col1, col2, col3 = st.columns(3)

        col1.metric("Error Rate (%)", f"{error_rate:.2f}")
        col2.metric("Mean RT (Correct Only) (s)", f"{mean_rt:.2f}" if pd.notna(mean_rt) else "N/A")
        col3.metric("Stroop Interference (s)", f"{stroop_effect:.2f}" if stroop_effect is not None else "N/A")

        st.subheader("📋 Detailed Responses")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "⬇️ Download CSV",
            df.to_csv(index=False),
            "stroop_results.csv",
            "text/csv"
        )

        if st.button("Continue to Mental Rotation Test"):

            for key in [
                "stroop_started",
                "q_index",
                "results",
                "answered",
                "word",
                "color",
                "condition",
                "start_time"
            ]:
                st.session_state.pop(key, None)

            st.session_state.current_stage = "mental"
            st.rerun()

        return

    # -------- TIMER (STABLE) --------

    st_autorefresh(interval=1000, key="stroop_timer")

    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, int(TIME_LIMIT - elapsed))

    st.write(f"### Question {st.session_state.q_index} / {TOTAL_QUESTIONS}")
    st.warning(f"⏱ Time left: {remaining} seconds")

    # -------- DISPLAY --------

    st.markdown(
        f"<h1 style='color:{st.session_state.color}; text-align:center;'>"
        f"{st.session_state.word}</h1>",
        unsafe_allow_html=True
    )

    # -------- ANSWERS --------

    cols = st.columns(4)

    for color_name, col in zip(COLORS.keys(), cols):
        with col:
            if st.button(color_name, key=f"{st.session_state.q_index}_{color_name}") and not st.session_state.answered:

                rt = round(elapsed, 2)
                correct = color_name.lower() == st.session_state.color

                record_response(
                    st.session_state.results,
                    st.session_state.q_index,
                    st.session_state.word,
                    st.session_state.color,
                    st.session_state.condition,
                    color_name,
                    correct,
                    rt
                )

                st.session_state.answered = True
                next_question()
                st.rerun()

    # -------- TIMEOUT --------

    if remaining == 0 and not st.session_state.answered:

        record_response(
            st.session_state.results,
            st.session_state.q_index,
            st.session_state.word,
            st.session_state.color,
            st.session_state.condition,
            None,
            False,
            None
        )

        next_question()
        st.rerun()
