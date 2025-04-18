import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

# Get top 5 Google results for the keyword
def get_top_google_results(query, num_results=5):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    search_query = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={search_query}&hl=en"

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    result_urls = []
    for result in soup.select("div.tF2Cxc"):
        link_tag = result.select_one("a")
        if link_tag and link_tag['href'].startswith("http"):
            result_urls.append(link_tag['href'])
        if len(result_urls) == num_results:
            break

    return result_urls

# Extract SEO features from a URL
def extract_seo_features(url, keyword):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        text = soup.get_text(separator=' ')
        words = text.split()
        word_count = len(words)

        keyword_count = text.lower().count(keyword.lower())
        keyword_density = (keyword_count / word_count) * 100 if word_count else 0

        headings = {
            'h1': len(soup.find_all('h1')),
            'h2': len(soup.find_all('h2')),
            'h3': len(soup.find_all('h3')),
            'h4': len(soup.find_all('h4')),
        }

        domain = re.findall(r'https?://([^/]+)', url)
        domain = domain[0] if domain else ""
        links = soup.find_all('a', href=True)
        internal_links = [link for link in links if domain in link['href']]
        external_links = [link for link in links if domain not in link['href'] and link['href'].startswith('http')]

        images = soup.find_all('img')
        images_with_alt = [img for img in images if img.get('alt')]
        alt_text_coverage = (len(images_with_alt) / len(images)) * 100 if images else 0

        return {
            "url": url,
            "word_count": word_count,
            "keyword_count": keyword_count,
            "keyword_density": round(keyword_density, 2),
            "headings": headings,
            "internal_links": len(internal_links),
            "external_links": len(external_links),
            "images": len(images),
            "images_with_alt": len(images_with_alt),
            "alt_text_coverage_percent": round(alt_text_coverage, 2)
        }

    except Exception as e:
        return {"url": url, "error": str(e)}

# Scoring system
def score_seo_content(your_data, competitors_data):
    avg_word_count = sum(d["word_count"] for d in competitors_data) / len(competitors_data)
    avg_internal_links = sum(d["internal_links"] for d in competitors_data) / len(competitors_data)

    score = 0
    report = []

    # Word Count
    if your_data["word_count"] >= avg_word_count:
        score += 20
    else:
        diff = avg_word_count - your_data["word_count"]
        score += max(0, 20 - int((diff / avg_word_count) * 20))
        report.append(f"📌 Word count is below average ({your_data['word_count']} vs {int(avg_word_count)}).")

    # Keyword Density
    kd = your_data["keyword_density"]
    if 0.5 <= kd <= 2.5:
        score += 15
    else:
        penalty = min(15, abs(kd - 1.5) * 10)
        score += max(0, 15 - penalty)
        report.append(f"📌 Keyword density is {kd}%. Ideal range is 0.5%–2.5%.")

    # Headings
    if your_data["headings"]["h1"] == 1 and your_data["headings"]["h2"] >= 3:
        score += 15
    else:
        score += 7
        report.append("📌 Use one H1 and at least 3 H2s for better structure.")

    # Internal Links
    if your_data["internal_links"] >= avg_internal_links:
        score += 10
    else:
        score += 5
        report.append(f"📌 Fewer internal links ({your_data['internal_links']} vs avg {int(avg_internal_links)}).")

    # External Links
    if your_data["external_links"] >= 2:
        score += 5
    else:
        score += 2
        report.append("📌 Add 1–2 external links to authority sources.")

    # Image Alt Text
    if your_data["alt_text_coverage_percent"] >= 80:
        score += 10
    else:
        score += 5
        report.append("📌 Add alt text to all images (currently {:.0f}%).".format(your_data["alt_text_coverage_percent"]))

    return int(score), report
