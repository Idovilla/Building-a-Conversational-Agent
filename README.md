
# Customer Service Chatbot

This Python script powers a customer service chatbot using OpenAI's GPT-4 model. It assists with inquiries such as order status, collecting contact details for human representative interaction, and providing feedback mechanisms. It features logging of conversations and handles user inputs through a terminal interface.

## Features

- **Order Status Inquiry**: Checks the status of an order based on a provided 4-digit ID.
- **Contact Detail Collection**: Saves customer contact details (name, email, phone) to a CSV file for further communication.
- **Conversation Logging**: Logs all user and bot interactions in a text file to review the dialogue history.
- **Feedback Request**: Collects user feedback on the service provided.

## Installation

Ensure you have Python 3.6 or higher installed on your system. Install the required dependencies by running:

```bash
pip install openai sklearn
```

## Usage

To run the chatbot, execute the script in the terminal:

```bash
python customer_service_chatbot.py
```

Interact with the chatbot by typing your inquiries. When you are done, you can exit the chat by typing 'exit'.

## Functions

- `log_conversation(user_input, bot_response)`: Logs the interaction between the user and the bot to `conversation_log.txt`.
- `save_to_csv(contact_details)`: Appends contact details to `contact_details.csv`.
- `request_feedback()`: Requests and logs user feedback.
- `check_order_status(order_id)`: Checks and returns the order status for a given ID.
- `save_contact_details(full_name, email, phone)`: Validates and saves provided contact details and returns appropriate responses.
- `jaccard_similarity(str1, str2)`: Computes the Jaccard similarity between two strings.
- `score_interaction_tfidf(user_input, bot_response)`: Scores the interaction using TF-IDF and cosine similarity.
- `chat_with_openai()`: The main function to run the chat interface.

## API Key Configuration

Before running the script, make sure to set your OpenAI API key in the script:

```python
key = "enter_key_here"
```

Replace `enter_key_here` with your actual OpenAI API key.

## Contributing

Contributions to this project are welcome. Please ensure that your code adheres to the existing style and has been tested adequately before submitting a pull request.

## License

Specify your license or state that the project is unlicensed.

