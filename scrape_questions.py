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

def search_questions(company):
    questions = []
    session = requests.Session()
    
    # Search DuckDuckGo for interview questions
    try:
        query = f"{company} system design interview questions site:reddit.com OR site:leetcode.com"
        url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
        
        response = session.get(url, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find_all('a', class_='result__a')
            
            for result in results[:5]:
                title = result.get_text(strip=True)
                if any(word in title.lower() for word in ['design', 'system', 'interview']):
                    questions.append(title)
        
        time.sleep(random.uniform(2, 4))
        
    except Exception as e:
        print(f"Error searching for {company}: {e}")
    
    # Add known questions based on company
    known_questions = {
        'Atlassian': [
            'Design a collaborative document editing system like Confluence',
            'Design a project management tool like Jira',
            'Design a real-time chat system for teams',
            'Design a file sharing platform',
            'Design a notification system'
        ],
        'PayPal': [
            'Design a payment processing system',
            'Design a fraud detection system',
            'Design a digital wallet',
            'Design a money transfer system',
            'Design a merchant payment gateway'
        ],
        'Mastercard': [
            'Design a credit card transaction system',
            'Design a real-time fraud detection system',
            'Design a global payment network',
            'Design a loyalty rewards system',
            'Design a merchant acquiring platform'
        ]
    }
    
    if company in known_questions:
        questions.extend(known_questions[company])
    
    return list(set(questions))

def main():
    companies = ['Atlassian', 'PayPal', 'Mastercard']
    all_content = []
    
    print("🔍 Scraping system design questions...")
    
    for company in companies:
        print(f"Searching {company}...")
        questions = search_questions(company)
        
        all_content.append(f"\n{'='*60}")
        all_content.append(f"{company.upper()} SYSTEM DESIGN QUESTIONS")
        all_content.append(f"{'='*60}")
        
        for i, question in enumerate(questions, 1):
            all_content.append(f"{i}. {question}")
        
        time.sleep(random.uniform(1, 3))
    
    # Save to text file
    with open('system_design_questions.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_content))
    
    print("✅ Questions saved to system_design_questions.txt")

if __name__ == "__main__":
    main()
