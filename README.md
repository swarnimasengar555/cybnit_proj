# BitElevate Adaptive Roadmap Generator (PoC)

A small proof of concept for **AI-Driven Adaptive Learning & Roadmap Generation** for Cynbit's BitElevate platform.

BitElevate promises adaptive learning instead of rigid curriculums. Writing a personal technical roadmap for every student by hand does not scale, so this PoC generates one automatically from the student's current skills and target role.

## How it works

1. The student enters current skills, target role, duration and weekly hours.
2. A system prompt sets the persona (technical architect on BitElevate) and a structure for each week.
3. An LLM served by Groq (model auto-selected from those available on the account) returns a week-by-week roadmap with goals, topics, a hands-on project and an outcome.
4. The student can download the roadmap as Markdown.

## Run locally

```bash
pip install -r requirements.txt
export GROQ_API_KEY=your_key_here     # Windows: set GROQ_API_KEY=your_key_here
streamlit run app.py
```

A free API key is available at https://console.groq.com.

## Technical approach

**Model choice.** A large language model fits this task because personalised educational content needs semantic understanding and structured long-form generation, which a classical predictive model cannot provide. Groq-hosted open models (Llama or GPT-OSS family) give fast, low-cost inference suitable for a live demo. The app lists the models available on the account and picks the best one, so it does not break when models are rotated; set `GROQ_MODEL` to force a specific one.

**Prompt design.** A fixed system prompt keeps outputs rigorous, modern and consistently structured. User inputs are injected into a template, so behaviour stays predictable.

**Data pipeline (production vision).** Instead of self-reported skills, the system would pull signals from the student's GitHub and LeetCode profiles, assess real skill level, and pass that as context to the model through a retrieval-augmented generation (RAG) pipeline.

## Future work

- **Phase 2:** build a vector database (ChromaDB or Pinecone) of Cynbit's internal material and newsletters so roadmaps are grounded in Cynbit's own teaching methods.
- **Phase 3:** progress tracking, where completed projects update the roadmap weekly (a real adaptive loop).
- **Phase 4:** mentor dashboard so mentors review and tweak AI roadmaps rather than writing them from scratch.

## Limitations

- Roadmaps are only as good as the self-reported skills in this PoC.
- No resource link verification yet; this is planned with the RAG layer.
