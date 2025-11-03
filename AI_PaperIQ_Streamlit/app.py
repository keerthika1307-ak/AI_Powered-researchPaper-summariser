import streamlit as st
from utils import gemini_api, paper_fetcher, pdf_extractor, text_analysis
import os

st.set_page_config(page_title='AI PaperIQ', layout='wide')

st.title('📚 AI PaperIQ — Streamlit Summariser')

# Sidebar inputs
with st.sidebar:
    st.header('Input Options')
    mode = st.radio('Choose input type', ['Paste text', 'Upload PDF', 'Search topic'])
    if mode == 'Search topic':
        topic = st.text_input('Enter topic (e.g., Machine Learning)')
    else:
        topic = ''
    st.write('Model preference (quality vs speed)')
    pref = st.selectbox('Preferred model', ['auto (pro preferred)', 'pro (quality)', 'flash (fast)'])

if 'conversation' not in st.session_state:
    st.session_state.conversation = []

col1, col2 = st.columns([2,1])

with col1:
    st.subheader('Chat-like Summariser')
    user_input = ''
    if mode == 'Paste text':
        user_input = st.text_area('Paste text or abstract here', height=200)
    elif mode == 'Upload PDF':
        uploaded = st.file_uploader('Upload PDF', type=['pdf'])
        if uploaded is not None:
            with st.spinner('Extracting text from PDF...'):
                try:
                    user_input = pdf_extractor.extract_text_from_pdf(uploaded)
                    st.success('Text extracted. Scroll below to see it.')
                except Exception as e:
                    st.error('PDF extraction failed: ' + str(e))
    elif mode == 'Search topic':
        user_input = st.text_area('Optional: Paste text or leave blank to fetch top ArXiv result for topic', height=120)

    submitted = st.button('Summarize')

    if submitted:
        content = ''
        if mode == 'Search topic' and not st.session_state.get('use_manual_text', False):
            if not topic:
                st.error('Please enter a topic to search.')
            else:
                with st.spinner('Fetching top paper from ArXiv...'):
                    papers = paper_fetcher.fetch_arxiv(topic, max_results=1)
                if not papers:
                    st.error('No papers found for topic. Paste text or try another topic.')
                else:
                    paper = papers[0]
                    content = paper.get('summary','') + "\n\nReference: " + paper.get('link','')
                    st.markdown('**Using top ArXiv paper:**')
                    st.write(paper.get('title'))
                    st.write(', '.join(paper.get('authors',[])))
                    st.markdown(f"[Open paper]({paper.get('link')})")
        else:
            content = user_input

        if not content or not content.strip():
            st.error('No text to summarize. Paste text, upload PDF, or search a topic.')
        else:
            st.session_state.conversation.append({'role':'user','text': content[:1000] + ('...' if len(content)>1000 else '')})
            with st.spinner('Generating high-quality summary using Gemini...'):
                model_choice = None
                if pref == 'pro (quality)':
                    model_choice = 'pro'
                elif pref == 'flash (fast)':
                    model_choice = 'flash'
                else:
                    model_choice = 'auto'
                summary = gemini_api.summarize_text(content, preferred=model_choice)
            st.session_state.conversation.append({'role':'ai','text': summary})

    # show conversation
    for msg in st.session_state.conversation[::-1]:
        if msg['role']=='ai':
            st.chat_message('assistant').write(msg['text'])
        else:
            st.chat_message('user').write(msg['text'])

with col2:
    st.subheader('Analysis & Visualizations')
    if st.session_state.conversation:
        last_user = next((m for m in reversed(st.session_state.conversation) if m['role']=='user'), None)
        last_ai = next((m for m in reversed(st.session_state.conversation) if m['role']=='ai'), None)
        if last_user and last_ai:
            input_text = last_user['text']
            summary_text = last_ai['text']
            analysis = text_analysis.analyze_texts(input_text, summary_text)
            
            # Display metrics with visual elements
            st.subheader("📊 Text Analysis Summary")
            
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric("Input Word Count", analysis["input_word_count"])
            metric_col2.metric("Summary Word Count", analysis["summary_word_count"])
            metric_col3.metric("Similarity", f"{analysis['cosine_similarity']*100:.2f}%")
            
            # Display additional info
            # Get common keywords (intersection of top keywords)
            common_keywords = list(set(analysis['top_keywords_input']) & set(analysis['top_keywords_summary']))
            if common_keywords:
                st.write("**🧠 Common Keywords:**", ", ".join(common_keywords[:5]))
            else:
                st.write("**🧠 Common Keywords:**", "No common keywords found")
            
            st.write("**📈 Readability Score (Summary):**", f"{analysis['flesch_summary']:.2f}")
            st.write("**📉 Compression Ratio:**", f"{analysis['compression_ratio']:.2%}")
            
            # Add visualizations
            st.plotly_chart(text_analysis.plot_comparison(analysis), use_container_width=True)
            st.plotly_chart(text_analysis.plot_top_keywords(analysis), use_container_width=True)
            
            # Additional metrics in two columns
            metrics_col1, metrics_col2 = st.columns(2)
            metrics_col1.metric('Cosine Similarity', value=f"{analysis['cosine_similarity']:.2%}")
            metrics_col2.metric('Keyword Overlap', value=f"{analysis['keyword_overlap']:.2%}")