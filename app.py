import streamlit as st
from openai import OpenAI
import re

# 1. Configure the OpenRouter client securely
api_key = st.secrets.get("OPENROUTER_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# 2. Pure Python Metrics Calculator
def calculate_metrics(text):
    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)
    
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    sentence_count = len(sentences) if sentences else 1
    
    unique_words = set(words)
    lexical_diversity = len(unique_words) / word_count if word_count > 0 else 0
    
    return word_count, sentence_count, lexical_diversity

# 3. Define AI feedback function via OpenRouter
def get_ai_feedback(text):
    prompt = f"""
    You are an expert English language assessor. Review the following student text.
    1. Estimate the CEFR level (A1 to C2) and approximate IELTS band score.
    2. Identify 2-3 specific grammar or structural errors.
    3. Provide constructive feedback on how to improve the text's coherence and vocabulary.
    
    Student Text:
    {text}
    """
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",  # You can change this to any model available on OpenRouter
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 4. Build the user interface
st.set_page_config(page_title="AI Writing Assessor", layout="wide")
st.title("📝 AI Writing Assessor")
st.markdown("Analyze student writing for linguistic metrics and get AI-powered feedback.")

student_text = st.text_area("Paste the text here:", height=200)

if st.button("Evaluate Writing"):
    if student_text.strip():
        with st.spinner("Analyzing text..."):
            words, sentences, ttr = calculate_metrics(student_text)
            
            st.subheader("📊 Linguistic Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Word Count", words)
            col2.metric("Sentence Count", sentences)
            col3.metric("Lexical Diversity (TTR)", f"{ttr:.2f}")
            
            st.subheader("🤖 Qualitative AI Feedback")
            try:
                ai_feedback = get_ai_feedback(student_text)
                st.write(ai_feedback)
            except Exception as e:
                st.error(f"Error connecting to AI API: {e}")
    else:
        st.warning("Please enter some text to evaluate.")

# Instead of just a text area, add a file uploader option:
uploaded_file = st.file_uploader("Upload a text (.txt) file or paste below:", type=["txt"])

if uploaded_file is not None:
    # If a file is uploaded, read its text automatically
    student_text = uploaded_file.read().decode("utf-8")
    st.text_area("Loaded Text from File:", value=student_text, height=200)
else:
    # Otherwise, show the normal typing box
    student_text = st.text_area("Or paste the text here:", height=200)
