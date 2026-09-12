import streamlit as st
import spacy
import spacy.cli
import google.generativeai as genai

# 1. Configure the AI Model securely
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3.6-flash')

# 2. Force download via spaCy's native CLI if missing
@st.cache_resource
def load_spacy():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        spacy.cli.download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

nlp = load_spacy()

# 3. Define metrics function
def calculate_metrics(text):
    doc = nlp(text)
    tokens = [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
    word_count = len(tokens)
    sentence_count = len(list(doc.sents))
    unique_words = set(tokens)
    lexical_diversity = len(unique_words) / word_count if word_count > 0 else 0
    return word_count, sentence_count, lexical_diversity

# 4. Define AI feedback function
def get_ai_feedback(text):
    prompt = f"""
    You are an expert English language assessor. Review the following student text.
    1. Estimate the CEFR level (A1 to C2) and approximate IELTS band score.
    2. Identify 2-3 specific grammar or structural errors.
    3. Provide constructive feedback on how to improve the text's coherence and vocabulary.
    
    Student Text:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

# 5. Build the user interface
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
