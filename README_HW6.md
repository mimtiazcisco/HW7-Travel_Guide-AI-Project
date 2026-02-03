
## Project title and name of author
# 🌍 AI-Powered Travel Guide Generator  
**Author: Muhammad Imtiaz**

---

## Purpose

This project is an AI-powered Travel Guide Generator built as part of **HW6** to demonstrate practical usage of modern Large Language Models (LLMs) within a real Python application.

### Problem It Solves
Planning travel itineraries is time-consuming and often requires researching:
- Daily schedules
- Attractions
- Restaurants
- Budget estimates
- Packing lists

This project automates that process by using AI to generate **personalized, structured, and realistic travel guides** based on user input.

### Relation to AI / AI-Assisted Workflows
The application showcases how AI can:
- Replace manual research with intelligent content generation
- Enforce structured outputs using prompt engineering
- Assist decision-making with constraints and preferences
- Combine text generation with image generation for richer user experiences

It demonstrates a **real-world AI-assisted workflow**, not just a standalone model call.

---

## What the Code Does

At a high level, the application:

- Collects user input via a Streamlit web interface:
  - Travel destination
  - Number of days
  - Personal interests
  - Constraints or guardrails

- Uses **OpenAI’s Chat Completion API** to:
  - Generate a structured, multi-day travel itinerary
  - Respect user constraints and logistical realism
  - Output clean, formatted Markdown sections

- Uses **OpenAI’s Image Generation API** to:
  - Create a high-quality city image
  - Generate images related to selected interests (e.g., food, museums, nature)

- Converts the generated content into a **professionally formatted PDF** using ReportLab.

- Stores results in session state so content persists across UI interactions.

The focus of the code is on:
- Prompt engineering
- Model fallback logic
- Safe AI usage
- Production-style error handling
- AI-driven content generation

---

##  How to Run or Use

### Prerequisites
- Python 3.9+
- An OpenAI API key (kept private)

### Basic Steps
1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
