import streamlit as st
import bcrypt
import os
import psycopg2
from display import *
from streamlit_cookies_manager import EncryptedCookieManager

# st.set_page_config(layout="wide", page_title="Yelp Recommend", page_icon="logo.jpg")



def login():
    st.title("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        cursor.execute("SELECT password_hash FROM myusers WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        if result:
            stored_password_hash = result[0]
            if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome {username}!")
                cookies["logged_in"] = "True"
                cookies["username"] = username
                cookies.save()
                st.rerun()
            else:
                st.error("Incorrect username or password")
        else:
            st.error("Username does not exist")

def register():
    st.title("Register")
    
    new_username = st.text_input("Create Username")
    new_password = st.text_input("Create Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        if new_password != confirm_password:
            st.error("Passwords do not match!")
        else:

            cursor.execute("SELECT username FROM myusers WHERE username = %s", (new_username,))
            if cursor.fetchone():
                st.error("Username already exists!")
            else:

                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("INSERT INTO myusers (username, password_hash) VALUES (%s, %s)", (new_username, hashed_password))
                conn.commit()
                st.success("Registration successful! Please login.")
                st.rerun()

def preference_form():
    st.title("Set Your Preferences")
    

    cuisine = st.multiselect(
    "Select your favorite cuisine", 
    [
        "Chinese", 
        "Italian", 
        "Mexican", 
        "Japanese", 
        "Indian", 
        "French", 
        "Thai", 
        "Korean", 
        "Mediterranean", 
        "Greek", 
        "Vietnamese", 
        "Spanish", 
        "Turkish", 
        "Caribbean", 
        "American", 
        "Brazilian", 
        "Lebanese", 
        "African", 
        "Russian", 
        "German", 
        "British", 
        "Australian", 
        "Middle Eastern", 
        "Filipino", 
        "Indonesian", 
        "Malaysian", 
        "Pakistani", 
        "Persian", 
        "Other"
    ]
)

    cuisine_str = ', '.join(cuisine)  

    taste = st.multiselect("Select your taste preference", ["Sweet", "Spicy", "Salty", "Sour", "Umami"])
    taste_str = ', '.join(taste) 
    

    special_req = st.text_area("Any special preferences?")

    if st.button("Submit Preferences"):
        username = st.session_state.username
        cursor.execute("""
            UPDATE myusers 
            SET cuisine_preference = %s, taste_preference = %s, special_requirements = %s 
            WHERE username = %s
        """, (cuisine_str, taste_str, special_req, username))
        conn.commit()
        st.success("Preferences saved successfully!")
        st.rerun()


def check_user_preferences():
    username = st.session_state.get("username")
    cursor.execute("SELECT cuisine_preference, taste_preference FROM myusers WHERE username = %s", (username,))
    user_preferences = cursor.fetchone()

    if user_preferences is None or (not user_preferences[0] and not user_preferences[1]):
        return False
    return True

# def user_menu():
#     st.write("User: ", st.session_state.get("username", "Guest"))
#     if st.button("My Favorite Stores"):
#         st.write("Displaying favorite stores...")
#         # Add logic to display favorite stores
#     if st.button("My Look History"):
#         st.write("Displaying look history...")

def user_menu():
    st.markdown(
        """
        <style>
        .user-menu {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            position: absolute;
            top: -50px;
            right: 10px;
            z-index: 1000;
        }
        .user-icon {
            display: inline-block;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: #0073e6;
            color: #fff;
            text-align: center;
            line-height: 60px;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
        }
        .dropdown-menu {
            display: none;
            position: absolute;
            top: 70px;
            right: 10px;
            background: #fff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            border-radius: 5px;
            overflow: hidden;
            z-index: 1100;
            width: 200px;
        }
        .dropdown-menu a {
            display: block;
            padding: 15px;
            text-decoration: none;
            color: #333;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            text-align: left;
        }
        .dropdown-menu a:hover {
            background-color: #f0f0f0;
        }
        .user-menu:hover .dropdown-menu {
            display: block;
        }
        </style>

        <div class="user-menu">
            <div class="user-icon">U</div>
            <div class="dropdown-menu">
                <a href="#" onclick="window.location.href='/favorite-stores';">My Favorite Stores</a>
                <a href="#" onclick="window.location.href='/look-history';">My Look History</a>
                <a href="#" onclick="window.location.href='/logout';">Logout</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )



def main_page():

    if check_user_preferences():
        search_query = st.text_input("Search for a business")
        display_businesses(search_query)
    else:
        preference_form()

def initialize_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = cookies.get("logged_in", "False") == "True"
    if 'username' not in st.session_state:
        st.session_state.username = cookies.get("username", "")

# def page_router():
#     initialize_session() 
#     st.session_state.logged_in = cookies.get("logged_in", "False") == "True"
#     st.session_state.username = cookies.get("username", "")
#     if not st.session_state.logged_in:

#         # Toggle switch for Login/Register
#         toggle = st.toggle("Don't have an account? Register", key="toggle")

#         if toggle:
#             register()
#         else:
#             login()
#     else:
#         user_menu()
#         main_page()

def page_router():
    initialize_session()

    # Set login status from cookies
    st.session_state.logged_in = cookies.get("logged_in", "False") == "True"
    st.session_state.username = cookies.get("username", "")

    # Check if the user is logged in
    if not st.session_state.logged_in:
        # Toggle switch for Login/Register
        toggle = st.toggle("Don't have an account? Register", key="toggle")

        if toggle:
            register()
        else:
            login()
    else:
        # Check for query parameters to determine routing
        query_params = st.query_params
        print(query_params)
        if "business_id" in query_params and query_params["business_id"]:
            # Route to business details page
            business_id = query_params["business_id"]
            query = """
                SELECT business_id, name, stars, review_count, categories 
                FROM business
                WHERE business_id = %s
            """
            cursor.execute(query, (business_id,))
            businesses = cursor.fetchall()
            print(businesses)
            username = st.session_state.get("username", "")
            log_click_event(username, business_id)

            if businesses:
                
                display_store_details(businesses)
            else:
                st.error(f"No business found with the given ID {business_id}.")
        else:
            # Default to main page with user menu
            user_menu()
            main_page()
        
if __name__ == "__main__":  
    # Initialize the cookie manager
    cookies = EncryptedCookieManager(prefix="myapp_", password="your_secret_password")

    if not cookies.ready():
        st.stop()

    # DATABASE_URL = os.getenv('DATABASE_URL')

    # conn = psycopg2.connect(DATABASE_URL, sslmode='require')

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


    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    page_router()

    conn.close()
