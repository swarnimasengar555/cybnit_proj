import os

import streamlit as st
from groq import Groq

PREFERRED_MODELS = [
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.1-8b-instant",
]
NON_CHAT_HINTS = ("whisper", "guard", "tts", "playai", "orpheus", "embed", "transcri")

SYSTEM_PROMPT = (
    "You are a senior technical architect working on the BitElevate platform "
    "at Cynbit Technologies. You design adaptive, rigorous learning roadmaps "
    "for students. Skip generic textbook curriculums and focus on modern "
    "stacks, AI agents and scalable system design. Every week must have a "
    "clear goal, topics, a hands-on project and a measurable outcome."
)


def build_prompt(skills, role, weeks, hours):
    return (
        f"Create a {weeks}-week personalized learning roadmap.\n"
        f"Current skills: {skills}\n"
        f"Target role: {role}\n"
        f"Time available: {hours} hours per week\n\n"
        "Format in markdown. For each week give: Goal, Topics, "
        "Hands-on Project, Outcome. Skip things the student already knows "
        "and end with a short list of portfolio projects."
    )


def get_client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        try:
            key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            key = None
    return Groq(api_key=key) if key else None


@st.cache_data(ttl=600, show_spinner=False)
def available_models(api_key):
    client = Groq(api_key=api_key)
    ids = [m.id for m in client.models.list().data]
    return [i for i in ids if not any(h in i.lower() for h in NON_CHAT_HINTS)]


def candidate_models(client):
    """Models to try, best first. GROQ_MODEL env var overrides everything."""
    override = os.getenv("GROQ_MODEL")
    if override:
        return [override]
    try:
        ids = available_models(client.api_key)
    except Exception:
        return PREFERRED_MODELS
    ordered = [m for m in PREFERRED_MODELS if m in ids]
    ordered += [m for m in ids if m not in ordered]
    return ordered or PREFERRED_MODELS


def generate(client, messages):
    last_error = None
    for model in candidate_models(client)[:4]:
        try:
            response = client.chat.completions.create(
                model=model, temperature=0.7, messages=messages
            )
            return response.choices[0].message.content, model
        except Exception as e:
            last_error = e
            if "model" not in str(e).lower():
                raise
    raise last_error


st.set_page_config(page_title="BitElevate Roadmap Generator", page_icon="🧭")
st.title("🧭 BitElevate Adaptive Roadmap Generator")
st.caption("Tell us where you are and where you want to go. We design the path.")

with st.sidebar:
    st.header("Preferences")
    weeks = st.slider("Duration (weeks)", 2, 12, 4)
    hours = st.slider("Hours per week", 5, 40, 10)
    st.markdown("---")
    st.caption("PoC for Cynbit Technologies · BitElevate")

skills = st.text_area(
    "What are your current skills?",
    placeholder="e.g. Basic Python, HTML, a little SQL",
)
role = st.text_input(
    "What is your target role?",
    placeholder="e.g. AI/ML Architect, Cloud Engineer, Full-Stack Developer",
)

if st.button("Generate my roadmap", type="primary"):
    if not skills.strip() or not role.strip():
        st.warning("Please fill in both your skills and your target role.")
        st.stop()

    client = get_client()
    if client is None:
        st.error("GROQ_API_KEY is not set. Add it as an environment variable.")
        st.stop()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_prompt(skills, role, weeks, hours)},
    ]
    with st.spinner("Designing your roadmap..."):
        try:
            roadmap, used_model = generate(client, messages)
        except Exception as e:
            st.error(f"Could not generate roadmap: {e}")
            st.stop()

    st.subheader(f"Your {weeks}-week path to {role}")
    st.markdown(roadmap)
    st.caption(f"Generated with {used_model} via Groq")
    st.download_button(
        "Download roadmap (.md)",
        roadmap,
        file_name="roadmap.md",
        mime="text/markdown",
    )
