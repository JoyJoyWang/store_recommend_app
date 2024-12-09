# recommend_system_with_LLM
**In the real world, ratings in apps like yelp, uber and doordash, can differ from the real feelings of customers and the sentiment of the customer expressed in reviews. To bridge this gap, we propose a project that leverages large language models (LLMs) to analyze customer reviews and calculate sentiment scores. By doing so, we aim to dig more details in the experience in a store and provide more accurate store recommendations based on genuine customer feelings. This project is to LLM calculate the sentiment scores of review contents and use them to recommend stores.** 



## Functions

- **User Login**: Allows users to log in and input their preferences for personalized recommendations.
- **Store Recommendations**: Suggests stores based on user-selected categories (e.g., Restaurant, Cafe, Bar) and the sentiment scores derived from customer reviews.
- **Sentiment Analysis**: Employs a pre-trained language model to analyze reviews, generating sentiment scores that guide recommendations.
- **Description Generation**: Provides users with generated descriptions of stores, highlighting experiences and potential pitfalls based on personalized preferences.

## Framework

- **Data Storage**: All data will be stored in AWS RDS using PostgreSQL, ensuring reliable and scalable data management.
- **Front-end**: Built with Streamlit, providing an easy-to-use interface for interaction.
- **Back-end**: We will compare the performance of different open-source models before making a final decision on which model to use for sentiment analysis and description generation.
- **Data Source**: The project uses simulated Yelp store data, but we plan to integrate real-time data in the future.
- **Deployment**: The application can be hosted on platforms like AWS EC2, Heroku, or any cloud service that supports Python.



