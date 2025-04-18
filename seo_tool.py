import streamlit as st
from seo_scraper import get_top_google_results, extract_seo_features, score_seo_content

st.set_page_config(page_title="SEO Analyzer", layout="centered")
st.title("🔍 SEO Analyzer Tool")
st.caption("Compare your content with top-ranking competitors and get actionable insights.")

keyword = st.text_input("Enter Target Keyword")
your_url = st.text_input("Enter Your Content URL")

if st.button("Analyze SEO"):
    if not keyword or not your_url:
        st.warning("Please enter both a keyword and your content URL.")
    else:
        with st.spinner("Fetching top competitors and analyzing SEO..."):
            try:
                top_urls = get_top_google_results(keyword)
                comp_data = [extract_seo_features(url, keyword) for url in top_urls]
                your_data = extract_seo_features(your_url, keyword)
                score, suggestions = score_seo_content(your_data, comp_data)

                st.subheader("📈 Your SEO Score")
                st.metric("Score", f"{score} / 100")

                st.subheader("🛠️ Suggestions to Improve")
                for s in suggestions:
                    st.write("•", s)

                st.subheader("🔗 Competitor URLs")
                for i, c in enumerate(comp_data, 1):
                    st.markdown(f"{i}. [{c['url']}]({c['url']})")

            except Exception as e:
                st.error(f"Something went wrong: {e}")
