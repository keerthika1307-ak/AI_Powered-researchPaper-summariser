import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import textstat
import plotly.graph_objects as go
import plotly.express as px

# ensure nltk data
try:
    nltk.data.find('tokenizers/punkt_tab')
except Exception:
    import nltk as _nltk
    _nltk.download('punkt_tab')
    _nltk.download('punkt')

def word_count(text: str) -> int:
    return len(nltk.word_tokenize(text))

def sentence_count(text: str) -> int:
    return len(nltk.sent_tokenize(text))

def top_keywords(text: str, n=10):
    vec = TfidfVectorizer(stop_words='english', max_features=2000)
    X = vec.fit_transform([text])
    scores = dict(zip(vec.get_feature_names_out(), X.toarray()[0]))
    top = sorted(scores.items(), key=lambda x: -x[1])[:n]
    return [k for k, _ in top]

def cosine_sim(a: str, b: str) -> float:
    vec = TfidfVectorizer(stop_words='english')
    X = vec.fit_transform([a, b])
    sim = cosine_similarity(X[0:1], X[1:2])[0][0]
    return float(sim)

def keyword_overlap(a: str, b: str) -> float:
    ka = set(top_keywords(a, n=20))
    kb = set(top_keywords(b, n=20))
    if not ka or not kb:
        return 0.0
    overlap = ka.intersection(kb)
    return len(overlap) / max(len(ka), 1)

def analyze_texts(input_text: str, summary_text: str) -> dict:
    in_wc = word_count(input_text)
    sum_wc = word_count(summary_text)
    in_sc = sentence_count(input_text)
    sum_sc = sentence_count(summary_text)
    tf_ratio = round(sum_wc / in_wc, 3) if in_wc else 0
    sim = round(cosine_sim(input_text, summary_text), 4)
    overlap = round(keyword_overlap(input_text, summary_text), 4)
    flesch_input = round(textstat.flesch_reading_ease(input_text), 2)
    flesch_summary = round(textstat.flesch_reading_ease(summary_text), 2)
    top_in = top_keywords(input_text, n=10)
    top_sum = top_keywords(summary_text, n=10)

    return {
        'input_word_count': in_wc,
        'summary_word_count': sum_wc,
        'input_sentence_count': in_sc,
        'summary_sentence_count': sum_sc,
        'compression_ratio': tf_ratio,
        'cosine_similarity': sim,
        'keyword_overlap': overlap,
        'flesch_input': flesch_input,
        'flesch_summary': flesch_summary,
        'top_keywords_input': top_in,
        'top_keywords_summary': top_sum
    }

def plot_comparison(analysis: dict):
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Word Count', x=['Input','Summary'], y=[analysis['input_word_count'], analysis['summary_word_count']]))
    fig.add_trace(go.Bar(name='Sentence Count', x=['Input','Summary'], y=[analysis['input_sentence_count'], analysis['summary_sentence_count']]))
    fig.update_layout(barmode='group', title='Input vs Summary: Counts')
    return fig

def plot_top_keywords(analysis: dict):
    top_in = analysis.get('top_keywords_input', [])[:10]
    top_sum = analysis.get('top_keywords_summary', [])[:10]
    df = {'keyword': top_in + top_sum, 'source': ['input']*len(top_in) + ['summary']*len(top_sum)}
    # simple bar chart comparing presence (we'll count 1 for presence)
    fig = px.histogram(df, x='keyword', color='source', barmode='group')
    fig.update_layout(title='Top Keywords: Input vs Summary', xaxis_tickangle=-45)
    return fig