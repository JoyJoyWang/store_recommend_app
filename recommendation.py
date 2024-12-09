from typing import List
import random
import math
import streamlit as st
import bcrypt
import os
import psycopg2
import random
import datetime
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("PG_HOST"),
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    sslmode=os.getenv("PG_SSLMODE", "require")  # Default to 'require'
)
cursor = conn.cursor()
def fetch_businesses_with_keywords(keywords: List[str], limit: int = 30) -> List[tuple]:
    """
    Fetch relevant businesses by searching for user-provided keywords in name, categories, and reviews.
    Calculate keyword matches and rank businesses by the number of matches.
    """
    if not keywords:
        return []

    # Construct SQL query for matching keywords
    keyword_conditions = " OR ".join([
        "b.name ILIKE %s", "b.categories ILIKE %s", "r.text ILIKE %s"
    ] * len(keywords))  # Repeat for each keyword

    query = f"""
        SELECT b.business_id, b.name, b.stars, b.review_count, b.categories,
               COUNT(*) AS keyword_matches
        FROM business b
        LEFT JOIN review r ON b.business_id = r.business_id
        WHERE {keyword_conditions}
        GROUP BY b.business_id, b.name, b.stars, b.review_count, b.categories
        ORDER BY keyword_matches DESC, b.stars DESC, b.review_count DESC
        LIMIT %s
    """

    # Build query parameters
    params = []
    for keyword in keywords:
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
    params.append(limit)

    # Execute query
    cursor.execute(query, params)
    return cursor.fetchall()

def recommendation_with_keywords(search_query: str, username: str, limit: int = 30) -> List[tuple]:
    """
    Use user-provided keywords and preferences to fetch recommended businesses.
    """
    # Fetch user preferences
    cursor.execute("""
        SELECT cuisine_preference, taste_preference, special_requirements 
        FROM myusers WHERE username = %s
    """, (username,))
    user_prefs = cursor.fetchone()
    preferences = {
        "cuisine_preference": user_prefs[0] if user_prefs else "",
        "taste_preference": user_prefs[1] if user_prefs else "",
        "special_requirements": user_prefs[2] if user_prefs else ""
    }

    # Combine user preferences with search query into a keyword list
    keywords = []
    if search_query:
        keywords.extend(search_query.split())  # Split query into words
    if preferences["cuisine_preference"]:
        keywords.extend(preferences["cuisine_preference"].split(", "))
    if preferences["taste_preference"]:
        keywords.extend(preferences["taste_preference"].split(", "))
    if preferences["special_requirements"]:
        keywords.extend(preferences["special_requirements"].split())

    # Remove duplicates and fetch businesses
    keywords = list(set(keywords))  # Ensure unique keywords
    businesses = fetch_businesses_with_keywords(keywords, limit=limit)
    return businesses
