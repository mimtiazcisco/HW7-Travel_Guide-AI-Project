"""
Travel Guide Generator with Images
Author: Mr. Khan
"""

from __future__ import annotations

import os
import datetime
from typing import List, Optional, Tuple

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import requests

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image

# =========================
# Environment
# =========================

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY not found in .env")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# Streamlit Config
# =========================

st.set_page_config(
    page_title="🌍 Travel Guide Generator",
    page_icon="✈️",
    layout="wide"
)

# =========================
# Constants
# =========================

MODEL_FALLBACKS = ["gpt-4o", "gpt-4-turbo", "gpt-4"]
MAX_TOKENS = 3000

SPECIAL_INTERESTS_OPTIONS = [
    "Museums",
    "Food & Cuisine",
    "Historic Sites",
    "Nightlife",
    "Nature & Parks",
    "Shopping",
    "Adventure Activities",
    "Cultural Experiences",
    "Beaches",
    "Photography Spots",
]

SYSTEM_PROMPT = """
You are an expert travel planner with deep local knowledge.

Generate realistic, practical travel itineraries.
Respect all constraints.
Consider logistics: opening hours, distances, meals.

Output in Markdown with:

## Trip Overview
## Day-by-Day Itinerary
### Day 1, Day 2...
Morning / Afternoon / Evening
## Recommended Restaurants & Cafes
## Essential Travel Tips
## Estimated Budget Breakdown
## Packing Suggestions
"""

IMAGE_DIR = os.path.join(os.getcwd(), "downloads", "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

# =========================
# Session State
# =========================

def init_state():
    defaults = {
        "destination": "",
        "num_days": 3,
        "special_interests": [],
        "guardrails": "",
        "plan_md": None,
        "last_model": None,
        "city_image": None,
        "interest_images": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# =========================
# Helpers
# =========================

def build_user_prompt(dest, days, interests, guardrails):
    interests_text = ", ".join(interests) if interests else "None"
    return f"""
Destination: {dest}
Days: {days}
Interests: {interests_text}
Constraints: {guardrails or "None"}
"""

def call_openai(system_prompt, user_prompt):
    for model in MODEL_FALLBACKS:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=MAX_TOKENS,
                temperature=0.7
            )
            return resp.choices[0].message.content.strip(), model
        except Exception:
            continue
    raise RuntimeError("All models failed")

# -------- IMAGE GENERATION --------

def generate_image(prompt: str, filename: str) -> str:
    path = os.path.join(IMAGE_DIR, filename)

    if os.path.exists(path):
        return path

    try:
        img = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )

        image_url = img.data[0].url
        img_data = requests.get(image_url).content

        with open(path, "wb") as f:
            f.write(img_data)

        return path
    except Exception:
        return None

# -------- PDF --------

def generate_pdf(destination, days, markdown_text, city_image_path):
    filename = f"travel_guide_{destination.lower().replace(' ', '_')}_{days}days.pdf"
    output_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()
    story = []

    if city_image_path and os.path.exists(city_image_path):
        story.append(Image(city_image_path, width=5*inch, height=3*inch))
        story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph(f"Travel Guide: {destination}", styles["Title"]))
    story.append(Paragraph(f"{days} Day Itinerary", styles["Heading2"]))
    story.append(Spacer(1, 0.2*inch))

    for line in markdown_text.split("\n"):
        if line.startswith("## "):
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph(line[3:], styles["Heading1"]))
        elif line.startswith("### "):
            story.append(Paragraph(line[4:], styles["Heading2"]))
        else:
            story.append(Paragraph(line, styles["Normal"]))

    doc.build(story)
    return file_path

# =========================
# UI
# =========================

st.title("🌍 Travel Guide Generator (with Images)")
st.caption("AI-powered itinerary + visual inspiration")

with st.form("travel_form"):
    st.session_state.destination = st.text_input("Destination *")
    st.session_state.num_days = st.number_input("Days *", 1, 30, 3)
    st.session_state.special_interests = st.multiselect(
        "Special Interests",
        SPECIAL_INTERESTS_OPTIONS
    )
    st.session_state.guardrails = st.text_area("Constraints")
    submit = st.form_submit_button("Generate ✨")

# =========================
# Main Logic
# =========================

if submit:
    with st.spinner("Generating itinerary and images..."):
        plan, model = call_openai(
            SYSTEM_PROMPT,
            build_user_prompt(
                st.session_state.destination,
                st.session_state.num_days,
                st.session_state.special_interests,
                st.session_state.guardrails
            )
        )

        st.session_state.plan_md = plan
        st.session_state.last_model = model

        # City image
        st.session_state.city_image = generate_image(
            f"Beautiful high quality travel photo of {st.session_state.destination} city skyline",
            "city.png"
        )

        # Interest images
        images = {}
        for interest in st.session_state.special_interests:
            img_path = generate_image(
                f"{interest} in {st.session_state.destination}, professional travel photography",
                f"{interest.lower().replace(' ','_')}.png"
            )
            images[interest] = img_path

        st.session_state.interest_images = images

# =========================
# Display
# =========================

if st.session_state.city_image:
    st.image(st.session_state.city_image, caption=st.session_state.destination)

if st.session_state.interest_images:
    st.subheader("Your Interests")
    cols = st.columns(len(st.session_state.interest_images))
    for col, (k, v) in zip(cols, st.session_state.interest_images.items()):
        if v:
            col.image(v, caption=k)

if st.session_state.plan_md:
    st.markdown(st.session_state.plan_md)

    pdf_path = generate_pdf(
        st.session_state.destination,
        st.session_state.num_days,
        st.session_state.plan_md,
        st.session_state.city_image
    )

    with open(pdf_path, "rb") as f:
        st.download_button("Download PDF", f, file_name=os.path.basename(pdf_path))

