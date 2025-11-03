import requests
import xml.etree.ElementTree as ET

ARXIV_BASE = 'http://export.arxiv.org/api/query?search_query=all:'

def fetch_arxiv(query: str, max_results: int = 5):
    q = requests.utils.requote_uri(query)
    url = f"{ARXIV_BASE}{q}&start=0&max_results={max_results}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
    except Exception:
        return []
    try:
        root = ET.fromstring(r.text)
    except Exception:
        return []
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    papers = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text if entry.find('atom:title', ns) is not None else ''
        summary = entry.find('atom:summary', ns).text if entry.find('atom:summary', ns) is not None else ''
        link = entry.find('atom:id', ns).text if entry.find('atom:id', ns) is not None else ''
        authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
        papers.append({'title': title.strip(), 'summary': summary.strip(), 'link': link, 'authors': authors})
    return papers