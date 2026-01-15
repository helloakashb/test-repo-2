# System Design Interview Questions Scraper

A Python web scraper that collects system design interview questions for Atlassian, PayPal, and Mastercard from various sources while avoiding bot detection.

## Features

- **Anti-bot detection**: Rotating user agents, random delays, proper headers
- **Multiple sources**: LeetCode Discuss, Reddit (via DuckDuckGo), GitHub repositories
- **Company-specific questions**: Tailored questions based on company domain
- **Clean output**: JSON export and formatted console display

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python scrape_system_design_questions.py
```

## Output

- Console display with formatted questions
- `system_design_questions.json` file with all results

## Bot Detection Avoidance

- Random delays between requests (1-4 seconds)
- Rotating user agents from real browsers
- Proper HTTP headers
- Rate limiting to avoid overwhelming servers
- Uses public APIs and search engines when possible
