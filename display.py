import math
import streamlit as st
import bcrypt
import os
import psycopg2
import random
import datetime
from recommendation import recommendation_with_keywords
from typing import List 

# DATABASE_URL = os.getenv('DATABASE_URL')

# conn = psycopg2.connect(DATABASE_URL, sslmode='require')

from dotenv import load_dotenv
import os
import psycopg2

# Load environment variables from .env file
load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("PG_HOST"),
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    sslmode=os.getenv("PG_SSLMODE", "require")  # Default to 'require'
)

cursor = conn.cursor()
# query = """
# SELECT *
# FROM information_schema.tables
# WHERE table_schema = 'public'
# """
# cursor.execute(query)
# columns = cursor.fetchall()

# print("user_prefs",columns)


def log_click_event(username, business_id, action="click"):
    try:
        timestamp = datetime.datetime.now()
        query = """
            INSERT INTO click_history (username, click_store, created_at)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (username, business_id, timestamp))
        conn.commit()

        # For tracking the user's behavior
        if action == "collect":
            collect_query = """
                INSERT INTO collect (username, business_id, collected_at)
                VALUES (%s, %s, %s)
            """
            cursor.execute(collect_query, (username, business_id, timestamp))
            conn.commit()
    except Exception as e:
        conn.rollback()  # Roll back the transaction to clear the error state
        st.error(f"Failed to log click event: {e}")   

def execute_query(query, params=None):
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.fetchall() if cursor.description else None
    except Exception as e:
        conn.rollback()
        st.error(f"Database error: {e}")
        return None

def cold_start_recommendation(username: str, query_offset: int = 0, limit: int = 30) -> List[tuple]:
    """
    Recommend businesses for users without a specific search query.
    Recommendations are based on user preferences and optionally extracted keywords.
    """
    # Fetch user preferences from the database
    cursor.execute("""
        SELECT cuisine_preference, taste_preference, special_requirements
        FROM myusers WHERE username = %s
    """, (username,))
    user_prefs = cursor.fetchone()

    if not user_prefs:
        # Default recommendation for users with no preferences set
        query = """
            SELECT business_id, name, stars, review_count, categories 
            FROM business
            ORDER BY stars DESC, review_count DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (limit, query_offset))
        return cursor.fetchall()

    # Extract preferences and process them
    cuisine_preference = user_prefs[0] if user_prefs[0] else ""
    taste_preference = user_prefs[1] if user_prefs[1] else ""
    special_requirements = user_prefs[2] if user_prefs[2] else ""

    # Combine preferences into a list of keywords
    keywords = []
    if cuisine_preference:
        keywords.extend(cuisine_preference.split(", "))
    if taste_preference:
        keywords.extend(taste_preference.split(", "))
    if special_requirements:
        keywords.extend(special_requirements.split(", "))

    # Remove duplicates
    keywords = list(set(keywords))

    if not keywords:
        # Default recommendation if no valid keywords are derived
        query = """
            SELECT business_id, name, stars, review_count, categories 
            FROM business
            ORDER BY stars DESC, review_count DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (limit, query_offset))
        return cursor.fetchall()

    # Build SQL query to fetch businesses based on keywords
    keyword_conditions = " OR ".join(["categories ILIKE %s"] * len(keywords))
    query = f"""
        SELECT business_id, name, stars, review_count, categories 
        FROM business
        WHERE {keyword_conditions}
        ORDER BY stars DESC, review_count DESC
        LIMIT %s OFFSET %s
    """
    params = [f"%{keyword}%" for keyword in keywords] + [limit, query_offset]
    cursor.execute(query, params)
    return cursor.fetchall()


# Search recommendation
def search_recommendation(search_query, username, query_offset=0, limit=30):
    if not search_query:
        return cold_start_recommendation(username, query_offset, limit)

    # Use keyword-based recommendation
    st.write("Searching for businesses using your query and preferences...")
    businesses = recommendation_with_keywords(search_query, username, limit=limit)
    return businesses


def show_details(business_id,name, stars, review_count, categories):
    # with st.modal("Product Details"):
    #     st.write(f"**Name:** {name}")
    #     st.write(f"**Rating:** {stars} stars")
    #     st.write(f"**Reviews:** {review_count}")
    #     st.write(f"**Categories:** {categories}")
        if st.button(f"View Details: {name}", key=f"details_{business_id}"):
            st.query_params(business_id=business_id)
            st.rerun()

def display_businesses(search_query="", page=1):

    query_params = st.query_params
    page_param = query_params.get("page", [1])
    if isinstance(page_param, list):
        page = int(page_param[0])
    else:
        page = int(page_param)
    query_offset = (page - 1) * 30
    # Add CSS for responsive three-column layout
    st.markdown(
        """
        <style>
        .flex {
            display: flex;
            flex-wrap: wrap;
            margin: -12px;
            justify-content: space-between;
        }
        .card {
            flex: 1 1 calc(33.333% - 24px); /* Three columns */
            margin: 12px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .card img {
            width: 100%;
            height: 150px;
            object-fit: cover;
        }
        .card-content {
            padding: 16px;
            flex: 1;
        }
        .card-content h3 {
            margin: 0;
            font-size: 1.2em;
            color: #333;
        }
        .card-content p {
            margin: 8px 0;
            font-size: 0.9em;
            color: #555;
        }
        .card-footer {
            text-align: center;
            padding: 12px;
            border-top: 1px solid #ddd;
        }
        .card-footer button {
            background: #007bff;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .card-footer button:hover {
            background: #0056b3;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Fetch user preferences and data
    username = st.session_state.get("username", "")
    query_offset = (page - 1) * 30

    # # Query based on user preferences or search query
    # if not search_query:
    #     cursor.execute("""
    #         SELECT cuisine_preference, taste_preference FROM myusers WHERE username = %s
    #     """, (username,))
    #     user_prefs = cursor.fetchone()

    #     if user_prefs:
    #         cuisine_preference, taste_preference = user_prefs[:2]  # Safely extract the first two elements
    #     else:
    #         cuisine_preference, taste_preference = None, None  # Defaults if no preferences found
        
    #     if user_prefs:
    #         query = """
    #             SELECT business_id, name, stars, review_count, categories 
    #             FROM business
    #             WHERE categories ILIKE %s OR categories ILIKE %s
    #             ORDER BY stars DESC, review_count DESC
    #             LIMIT 30 OFFSET %s
    #         """
    #         cursor.execute(query, (f'%{cuisine_preference}%', f'%{taste_preference}%', query_offset))
    #     else:
    #         query = """
    #             SELECT business_id, name, stars, review_count, categories 
    #             FROM business
    #             ORDER BY stars DESC, review_count DESC
    #             LIMIT 30 OFFSET %s
    #         """
    #         cursor.execute(query, (query_offset,))
    # else:
    #     query = """
    #         SELECT business_id, name, stars, review_count, categories 
    #         FROM business
    #         WHERE name ILIKE %s
    #         ORDER BY stars DESC, review_count DESC
    #         LIMIT 30 OFFSET %s
    #     """
    #     cursor.execute(query, (f'%{search_query}%', query_offset))

    # businesses = cursor.fetchall()
    username = st.session_state.get("username")
    businesses = search_recommendation(search_query, username)


    # Render cards
    cardcol1,cardcol2,cardcol3 = st.columns(3)
    if businesses:
        st.markdown('<div class="flex-col p-3">', unsafe_allow_html=True)
        for idx,business in enumerate(businesses):
            # print(business)
            business_id, name, stars, review_count, categories, *_ = business

            # Query for a photo of this business
            query = "SELECT photo_id, caption, label FROM photos WHERE business_id = %s LIMIT 1"
            cursor.execute(query, (business_id,))
            photo = cursor.fetchone()
            print("photo",photo)

            if photo:
                photo_id, caption, label = photo
                # photo_url = f"https://your_image_server/{photo_id}.jpg"  # Adjust based on your image storage
                photo_url = f"https://joyjoywang.github.io/yelp_photo/photos_cleaned/{photo_id}.jpg"
            else:
                photo_url = f"https://via.placeholder.com/300?text={name}"  # Fallback placeholder
                caption = "No photo available"
                label = ""

            # Display details
            # st.image(photo_url, caption=f"{caption} ({label})", use_container_width=True)

            if idx%3==0:
                col = cardcol1
            elif idx%3==1:
                col = cardcol2
            else:
                col = cardcol3
            with col:
                st.markdown(
                    f"""
                    <a href="?business_id={business_id}" style="text-decoration: none; color: inherit;">
                        <div class="card" style="cursor: pointer; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 16px;">
                            <img src="{photo_url}" alt="{name}" style="width: 100%; height: 150px; object-fit: cover;">
                            <div class="card-content" style="padding: 16px;">
                                <h3 style="margin: 0; font-size: 1.2em;">{name}</h3>
                                <p><b>Rating:</b> {stars} stars</p>
                                <p><b>Reviews:</b> {review_count}</p>
                                <p><b>Categories:</b> {categories}</p>
                            </div>
                        </div>
                    </a>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("No businesses found!")

    # Pagination
    cursor.execute("SELECT COUNT(*) FROM business")
    total_businesses = cursor.fetchone()[0]
    total_pages = math.ceil(total_businesses / 30)

    col1, col2 = st.columns([1, 1])
    if page > 1:
        if col1.button("Previous"):
            # st.experimental_set_query_params(page=page - 1)
            st.query_params = {"page": page - 1}
            st.rerun()
    if page < total_pages:
        if col2.button("Next"):
            # st.experimental_set_query_params(page=page + 1)
            st.query_params = {"page": page + 1}
            st.rerun()

def record_stay_time(username, business_id, start_time):
    end_time = datetime.datetime.now()
    stay_duration = end_time - start_time

    query = """
        UPDATE click_history
        SET stay_time = %s
        WHERE username = %s AND click_store = %s
        ORDER BY created_at DESC LIMIT 1
    """
    cursor.execute(query, (stay_duration, username, business_id))
    conn.commit()


def display_store_details(businesses):
    start_time = datetime.datetime.now()
    if not businesses or len(businesses) == 0:
        st.error("Store not found.")
        return

    # Extract details (assuming businesses is a list of tuples)
    business = businesses[0]  # Fetch the first entry
    business_id, name, stars, review_count, categories = business
    # Query for a photo of this business
    query = "SELECT photo_id, caption, label FROM photos WHERE business_id = %s LIMIT 1"
    cursor.execute(query, (business_id,))
    photo = cursor.fetchone()

    if photo:
        photo_id, caption, label = photo
        photo_url = f"https://joyjoywang.github.io/yelp_photo/photos_cleaned/{photo_id}.jpg"  # Adjust based on your image storage
    else:
        photo_url = f"https://via.placeholder.com/300?text={name}"  # Fallback placeholder
        caption = "No photo available"
        label = ""

    # Display details
    st.image(photo_url, caption=f"{caption} ({label})", use_container_width=True)
    st.title(name)
    if st.button("Add to Collection"):
        username = st.session_state.get("username", "")
        log_click_event(username, business_id, action="collect")
        st.success("Added to collection!")

    # st.write(f"**Rating:** {stars} stars")
    # st.write(f"**Review Count:** {review_count}")
    # st.write(f"**Categories:** {categories}")
    # st.write("**Description:** Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
        # Display reviews
    st.markdown("### Business Details")
    st.divider()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"**🌟 Rating:** {stars} stars")
        st.markdown(f"**📝 Reviews:** {review_count}")
    with col2:
        st.markdown(f"**📂 Categories:** {categories}")

    # st.markdown("**📖 Description:** Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
    st.divider()

    # Fetch reviews from the database

    query = """
        SELECT user_id, text, stars
        FROM review
        WHERE business_id = %s
    """
    cursor.execute(query, (business_id,))
    reviews = cursor.fetchall()

    st.markdown("### User Reviews")
    if reviews:
        for review in reviews:
            user_name, text, rating = review
            st.markdown(
                f"""
                <div style="margin-bottom: 16px; padding: 8px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;">
                    <strong>{user_name}</strong>  
                    <span style="color: #FFD700;">{'⭐' * int(float(rating))}</span>  
                    <p style="margin: 0; font-size: 0.9em; color: #333;">{text}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No reviews available for this store.")


# def page_router():
#     query_params = st.query_params
#     st.write(f"Query Params: {query_params}")  # Debugging

#     print("sisnbf")
#     if "business_id" in query_params:
#         business_id = query_params.get("business_id", [None])[0]
#         query = """
#             SELECT business_id, name, stars, review_count, categories 
#             FROM business
#             WHERE business_id = %s
#         """
#         cursor.execute(query, (business_id,))  # Pass as a tuple
#         businesses = cursor.fetchall()
#         print("businesses")
#         display_store_details(businesses)
#     else:
#         display_businesses()
