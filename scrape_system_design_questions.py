#!/usr/bin/env python3
"""
Web scraper for system design interview questions from Atlassian, PayPal, and Mastercard
Uses rotating user agents and delays to avoid bot detection
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote_plus
import json
import re

class SystemDesignScraper:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        self.session = requests.Session()
        self.results = {}
        
    def get_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def search_leetcode_discuss(self, company):
        """Search LeetCode discuss for system design questions"""
        try:
            query = f"{company} system design interview"
            url = f"https://leetcode.com/discuss/interview-question?currentPage=1&orderBy=hot&query={quote_plus(query)}"
            
            response = self.session.get(url, headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                questions = []
                
                # Find discussion topics
                topics = soup.find_all('div', class_='topic-title')
                for topic in topics[:5]:  # Limit to first 5 results
                    title_elem = topic.find('a')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        if any(keyword in title.lower() for keyword in ['system design', 'design', 'architecture']):
                            questions.append(title)
                
                return questions
        except Exception as e:
            print(f"Error searching LeetCode for {company}: {e}")
            return []
    
    def search_glassdoor_alternative(self, company):
        """Search interview experiences from alternative sources"""
        try:
            # Use DuckDuckGo search to find interview questions
            query = f"site:reddit.com {company} system design interview questions"
            url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
            
            response = self.session.get(url, headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                questions = []
                
                # Extract search results
                results = soup.find_all('a', class_='result__a')
                for result in results[:3]:
                    title = result.get_text(strip=True)
                    if 'system design' in title.lower():
                        questions.append(title)
                
                return questions
        except Exception as e:
            print(f"Error searching alternative sources for {company}: {e}")
            return []
    
    def search_github_repos(self, company):
        """Search GitHub repositories for interview questions"""
        try:
            query = f"{company} system design interview questions"
            url = f"https://api.github.com/search/repositories?q={quote_plus(query)}&sort=stars&order=desc"
            
            response = self.session.get(url, headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                questions = []
                
                for repo in data.get('items', [])[:3]:
                    name = repo.get('name', '')
                    description = repo.get('description', '')
                    if description and 'system design' in description.lower():
                        questions.append(f"{name}: {description}")
                
                return questions
        except Exception as e:
            print(f"Error searching GitHub for {company}: {e}")
            return []
    
    def extract_common_questions(self):
        """Extract common system design questions based on company type"""
        common_questions = {
            'Atlassian': [
                'Design a collaborative document editing system like Confluence',
                'Design a project management system like Jira',
                'Design a real-time chat system for teams',
                'Design a file sharing and collaboration platform',
                'Design a notification system for team updates'
            ],
            'PayPal': [
                'Design a payment processing system',
                'Design a fraud detection system',
                'Design a wallet system for digital payments',
                'Design a money transfer system',
                'Design a merchant payment gateway'
            ],
            'Mastercard': [
                'Design a credit card transaction processing system',
                'Design a real-time fraud detection system',
                'Design a global payment network',
                'Design a loyalty points system',
                'Design a merchant acquiring system'
            ]
        }
        return common_questions
    
    def scrape_company_questions(self, company):
        """Scrape questions for a specific company"""
        print(f"\n🔍 Searching for {company} system design questions...")
        
        all_questions = []
        
        # Add delay to avoid rate limiting
        time.sleep(random.uniform(2, 4))
        
        # Search multiple sources
        leetcode_questions = self.search_leetcode_discuss(company)
        all_questions.extend(leetcode_questions)
        
        time.sleep(random.uniform(1, 3))
        
        alternative_questions = self.search_glassdoor_alternative(company)
        all_questions.extend(alternative_questions)
        
        time.sleep(random.uniform(1, 3))
        
        github_questions = self.search_github_repos(company)
        all_questions.extend(github_questions)
        
        # Add common questions based on company domain
        common_questions = self.extract_common_questions()
        if company in common_questions:
            all_questions.extend(common_questions[company])
        
        # Remove duplicates and clean up
        unique_questions = list(set(all_questions))
        cleaned_questions = [q for q in unique_questions if len(q) > 10 and len(q) < 200]
        
        self.results[company] = cleaned_questions
        print(f"✅ Found {len(cleaned_questions)} questions for {company}")
        
        return cleaned_questions
    
    def save_results(self, filename='system_design_questions.json'):
        """Save results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to {filename}")
    
    def print_results(self):
        """Print formatted results"""
        print("\n" + "="*80)
        print("SYSTEM DESIGN INTERVIEW QUESTIONS")
        print("="*80)
        
        for company, questions in self.results.items():
            print(f"\n🏢 {company.upper()}")
            print("-" * 50)
            for i, question in enumerate(questions, 1):
                print(f"{i:2d}. {question}")

def main():
    companies = ['Atlassian', 'PayPal', 'Mastercard']
    scraper = SystemDesignScraper()
    
    print("🚀 Starting system design questions scraper...")
    print("⚠️  Using delays and rotation to avoid bot detection")
    
    for company in companies:
        try:
            scraper.scrape_company_questions(company)
        except Exception as e:
            print(f"❌ Error processing {company}: {e}")
    
    scraper.print_results()
    scraper.save_results()
    
    print(f"\n✨ Scraping completed! Found questions for {len(scraper.results)} companies.")

if __name__ == "__main__":
    main()
