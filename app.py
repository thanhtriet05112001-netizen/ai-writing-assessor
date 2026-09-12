API_KEY = st.secrets["AQ.Ab8RN6KtXviRPSwnqKVSy2Rw5-isNT60dZOyO4uz8Vvs5V-WHw"]
genai.configure(api_key=API_KEY)
import subprocess

@st.cache_resource
def load_spacy():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
        return spacy.load("en_core_web_sm")
