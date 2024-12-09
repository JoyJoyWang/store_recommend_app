# Recommendation Web App

## Overview

This project provides a web-based application to compare and test different recommendation algorithms conveniently. The platform enables users to evaluate key metrics such as click-through rate (CTR) and conversion rate. It is designed for ease of use, allowing users to simply update the `recommendation.py` file with new algorithms for evaluation.

The web app features:

- A visually appealing and user-friendly interface.
- Integration with a robust backend.
- Deployment of a database on Heroku and an image library on GitHub Pages.
- Capability to test and measure the effectiveness of recommendation algorithms directly within the app.

The application is deployed at: [Web App Link](https://spec-project-store-recommend-app.streamlit.app/)

This project demonstrates the potential of recommendation systems in a practical setting, offering a streamlined platform for testing, optimizing, and understanding algorithm performance. It is ideal for both developers and researchers looking to innovate in the recommendation space.

The photo data used in this application is hosted on GitHub Pages, providing an easily accessible and scalable solution for serving images. The photos are stored in the repository [JoyJoyWang/yelp_photo](https://github.com/JoyJoyWang/yelp_photo) and can be accessed directly via the GitHub Pages URL. This setup ensures that the application can efficiently fetch and display images without requiring additional image hosting services.

## Demo Video

Watch the usage demo of the web app:

[![Usage Demo](https://img.youtube.com/vi/fDHqhnYrVak/0.jpg)](https://www.youtube.com/watch?v=fDHqhnYrVak)

## Features

1. **Login and Registration**:
   - Secure user authentication using hashed passwords.
   - User preferences can be stored and managed.
2. **Personalized Recommendations**:
   - Cold-start recommendations based on user preferences.
   - Keyword-based search recommendations tailored to user input.
3. **Interactive Business Listing**:
   - View businesses in a paginated layout.
   - Detailed business information and user reviews.
   - Add businesses to a personal collection.
4. **User Behavior Analysis**:
   - Log user interactions, such as clicks and time spent on businesses.
   - Track collected businesses for further analysis.
5. **Deployment and Scalability**:
   - Database hosted on Heroku.
   - Frontend served via Streamlit with efficient backend operations.

## Installation Guide

### Prerequisites

- Python 3.9 or higher
- PostgreSQL database
- Environment variables set for database credentials (via `.env` file)

### Steps

1. Clone the repository:

   ```
   git clone https://github.com/JoyJoyWang/store_recommend_app.git
   cd store_recommend_app
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Run the application:

   ```
   streamlit run login.py
   ```

## Python Files and Functions

### 1. `display.py`

Functions for displaying and interacting with the frontend:

- `log_click_event(username, business_id, action)`: Logs user clicks and collections.
- `execute_query(query, params)`: Executes a SQL query and handles exceptions.
- `cold_start_recommendation(username, query_offset, limit)`: Provides recommendations for new users.
- `search_recommendation(search_query, username, query_offset, limit)`: Fetches recommendations based on search queries.
- `display_businesses(search_query, page)`: Displays businesses in a paginated grid layout.
- `display_store_details(businesses)`: Shows detailed information about a specific business.

### 2. `login.py`

Handles user authentication and session management:

- `login()`: Authenticates users using their username and password.
- `register()`: Registers new users and stores their credentials securely.
- `preference_form()`: Allows users to set preferences for better recommendations.
- `check_user_preferences()`: Verifies if a user has set preferences.
- `page_router()`: Manages routing between login, registration, and main pages.

### 3. `recommendation.py`

Implements recommendation algorithms:

- `fetch_businesses_with_keywords(keywords, limit)`: Retrieves businesses matching the provided keywords.
- `recommendation_with_keywords(search_query, username, limit)`: Combines user preferences and search queries to generate recommendations.

## Database Schema

The backend database supports multiple functionalities, storing user preferences, interactions, and business data to generate and track recommendations effectively. Below are the details of the database tables:

### 1. **`collect`**

Stores user collections of businesses.

- `id` (Primary Key): Auto-incrementing ID.
- `username`: User's name.
- `business_id`: ID of the business collected.
- `collected_at`: Timestamp of when the business was collected.

### 2. **`click_history`**

Tracks user interactions and behaviors.

- `id` (Primary Key): Unique record ID.
- `username`: User's name.
- `recommendmodel`: Recommendation model used.
- `click_store`: Clicked store ID.
- `stay_time`: Duration of user's stay.
- `collect`: Boolean indicating if the store was collected.
- `created_at`: Timestamp of the interaction.

### 3. **`business`**

Contains details of businesses.

- `business_id` (Primary Key): Unique ID of the business.
- `name`: Business name.
- `latitude`: Geographical latitude.
- `longitude`: Geographical longitude.
- `stars`: Average star rating.
- `review_count`: Total number of reviews.
- `categories`: Business categories.

### 4. **`review`**

Stores reviews for businesses.

- `review_id` (Primary Key): Unique ID of the review.
- `user_id`: ID of the user who left the review.
- `business_id`: Associated business ID.
- `stars`: Review rating.
- `text`: Review text.

### 5. **`users`**

Holds user details and activity statistics.

- `user_id` (Primary Key): Unique user ID.
- `name`: User's name.
- `review_count`: Number of reviews written.
- `useful`: Count of "useful" votes received.
- `fans`: Number of fans.

### 6. **`checkin`**

Tracks business check-ins.

- `business_id`: ID of the business.
- `date`: Check-in dates.

### 7. **`tip`**

Stores user tips for businesses.

- `user_id`: ID of the user who left the tip.
- `business_id`: Associated business ID.
- `text`: Tip content.
- `date`: Date the tip was given.
- `compliment_count`: Number of compliments received.

### 8. **`myusers`**

Manages registered users and their preferences.

- `id` (Primary Key): Unique ID for each user.
- `username`: User's unique username.
- `password_hash`: Encrypted password.
- `cuisine_preference`: Preferred cuisines.
- `taste_preference`: Preferred tastes.
- `special_requirements`: Special user requirements.

### 9. **`photos`**

Stores metadata for business photos.

- `photo_id` (Primary Key): Unique photo ID.
- `business_id`: Associated business ID.
- `caption`: Caption for the photo.
- `label`: Descriptive label for the photo (e.g., food, drink, interior).

## How to Use

1. Update the `recommendation.py` file with your recommendation algorithm.
2. Deploy the app to test and compare the algorithm’s performance.
3. Track metrics like click-through rate and conversion rate for evaluation.

## Contribution

This app offers a well-designed frontend and backend framework, making it easy to integrate new recommendation algorithms and deploy the web app seamlessly. It provides a convenient platform for users to interact with the app, enabling developers and researchers to gather first-hand experimental data or conduct A/B testing efficiently. Contributions to enhance its features and usability are highly encouraged.
