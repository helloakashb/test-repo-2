#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote_plus

def get_headers():
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive'
    }

def search_comprehensive(company):
    session = requests.Session()
    all_questions = set()
    
    search_queries = [
        f"{company} system design interview questions",
        f"{company} senior software engineer interview system design",
        f"{company} L5 L6 system design round",
        f"{company} staff engineer system design interview",
        f"{company} principal engineer interview experience",
        f"site:leetcode.com {company} system design",
        f"site:reddit.com {company} interview system design",
        f"site:glassdoor.com {company} system design questions",
        f"site:github.com {company} system design interview",
        f"{company} onsite interview system design round"
    ]
    
    for query in search_queries:
        try:
            url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
            response = session.get(url, headers=get_headers(), timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = soup.find_all('a', class_='result__a')
                
                for result in results[:3]:
                    title = result.get_text(strip=True)
                    if any(word in title.lower() for word in ['design', 'system', 'interview', 'experience']):
                        all_questions.add(title)
            
            time.sleep(random.uniform(2, 5))
            
        except Exception as e:
            print(f"Error with query '{query}': {e}")
            continue
    
    return list(all_questions)

def main():
    companies = ['Atlassian', 'PayPal', 'Mastercard']
    
    print("🔍 Enhanced scraping for comprehensive system design questions...")
    
    with open('additional_questions.txt', 'w', encoding='utf-8') as f:
        for company in companies:
            print(f"Searching {company} comprehensively...")
            questions = search_comprehensive(company)
            
            f.write(f"\n{'='*60}\n")
            f.write(f"{company.upper()} - ADDITIONAL QUESTIONS FOUND\n")
            f.write(f"{'='*60}\n")
            
            for i, question in enumerate(questions, 1):
                f.write(f"{i}. {question}\n")
            
            print(f"Found {len(questions)} additional questions for {company}")
    
    print("✅ Additional questions saved to additional_questions.txt")

if __name__ == "__main__":
    main()
