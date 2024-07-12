import openai
import re
import csv
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
key = "your_api_key"
# Dictionary to store order statuses
order_statuses = {
    "1234": "Processing",
    "5678": "Shipped",
    "9101": "On Hold",
    "1121": "Delivered",
    "3141": "Awaiting Payment"
}

def log_conversation(user_input, bot_response):
    """
    Log the conversation between the user and the bot.

    Args:
    user_input (str): The user's message
    bot_response (str): The bot's response

    Returns:
    None
    """
    with open('conversation_log.txt', 'a') as file:
        file.write(f"User: {user_input}\nBot: {bot_response}\n\n")

def save_to_csv(contact_details):
    """
    Save contact details to a CSV file.

    Args:
    contact_details (list): A list containing full name, email, and phone number

    Returns:
    None
    """
    file_path = 'contact_details.csv'
    try:
        with open(file_path, 'x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Full Name', 'Email', 'Phone Number'])
    except FileExistsError:
        pass

    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(contact_details)

def request_feedback():
    """
    Request feedback from the user on a scale of 1 to 5.

    Returns:
    str: The user's feedback
    """
    print(
        "Could I ask you to rate our service today on a scale from 1 to 5? Your feedback is invaluable to us and helps us improve.")
    feedback = input("Your feedback: ")
    log_conversation("Feedback request", "Could I ask you to rate our service today on a scale from 1 to 5?")
    log_conversation("User feedback", feedback)
    return feedback

def check_order_status(order_id):
    """
    Check the status of an order given its ID.

    Args:
    order_id (str): The 4-digit order ID

    Returns:
    str: The status of the order or an error message if the order doesn't exist
    """
    if order_id in order_statuses:
        return f"Order ID {order_id} is currently {order_statuses[order_id]}."
    else:
        return "The order ID does not exist. Please check the ID and try again."

def save_contact_details(full_name=None, email=None, phone=None):
    """
    Save contact details and return a response message.

    Args:
    full_name (str, optional): The customer's full name
    email (str, optional): The customer's email address
    phone (str, optional): The customer's phone number

    Returns:
    str: A response message indicating success or requesting missing information
    """
    details = [full_name, email, phone]
    if all(details):
        save_to_csv(details)
        return "Thank you for providing your contact details. A human representative will contact you shortly."
    else:
        missing = []
        if not full_name:
            missing.append("full name")
        if not email:
            missing.append("email")
        if not phone:
            missing.append("phone number")
        return f"Please provide your {', '.join(missing)}."

def jaccard_similarity(str1, str2):
    """
    Calculate the Jaccard similarity between two strings.

    Args:
    str1 (str): The first string
    str2 (str): The second string

    Returns:
    float: The Jaccard similarity score
    """
    set1 = set(str1.split())
    set2 = set(str2.split())
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def score_interaction_tfidf(user_input, bot_response):
    """
    Score the interaction using TF-IDF and cosine similarity.

    Args:
    user_input (str): The user's message
    bot_response (str): The bot's response

    Returns:
    float: The similarity score scaled to a range of 0-10
    """
    documents = [user_input, bot_response]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0] * 10  # Scale the similarity to a score out of 10

def chat_with_openai():
    """
    Main function to run the chatbot using OpenAI's API.
    """
    client = openai.OpenAI(api_key=key)

    print(
        "Hello! I'm your assistant. How can I help you today? If you wish to end this conversation at any point, simply type 'exit'.")

    conversation_history = []
    waiting_for_order_id = False
    collecting_contact_details = False
    contact_details = {"full_name": None, "email": None, "phone": None}

    while True:
        user_message = input("You: ")
        if user_message.lower() == 'exit':
            request_feedback()
            print("Thank you for your feedback. Goodbye!")
            log_conversation(user_message, "Thank you for your feedback. Goodbye!")
            break

        conversation_history.append({"role": "user", "content": user_message})

        if waiting_for_order_id and re.match(r'^\d{4}$', user_message):
            status = check_order_status(user_message)
            print("Bot:", status)
            log_conversation(user_message, status)
            waiting_for_order_id = False
            conversation_history = []
            continue

        if collecting_contact_details:
            if not contact_details["full_name"]:
                contact_details["full_name"] = user_message
            elif not contact_details["email"]:
                if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', user_message):
                    contact_details["email"] = user_message
                else:
                    print("Bot: Please provide a valid email address.")
                    continue
            elif not contact_details["phone"]:
                if re.match(r'^\d+$', user_message):
                    contact_details["phone"] = user_message
                else:
                    print("Bot: Please provide a valid phone number (digits only).")
                    continue

            response = save_contact_details(**contact_details)
            print("Bot:", response)
            log_conversation(user_message, response)
            if all(contact_details.values()):
                collecting_contact_details = False
                contact_details = {"full_name": None, "email": None, "phone": None}
            continue

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a customer service assistant. Follow these instructions:
1. Order Status Inquiry: When a user asks about order status, ask for the 4-digit order ID if not provided.
2. Human Representative: If requested, use the save_contact_details function to collect full name, email, and phone number.
3. Return Policies: Knowledge of the store's return policies is crucial for handling inquiries regarding returns.
   The agent should be equipped to explain that most items can be returned within 30 days of purchase for a full refund or exchange, provided they are in their original condition with all tags and packaging intact.
   Receipt or proof of purchase is required.
   For queries about exceptions, the agent should clarify that items like clearance merchandise, perishable goods, and personal care products are generally not returnable, advising users to review product descriptions or consult with store personnel for specifics.
   Regarding refunds, the agent should explain that the method of refund matches the original payment method, detailing the process for both card and cash/check transactions.
   This ensures that users have a clear understanding of how they can expect to receive their refund.
4. Unclear Queries: Request clarification if needed.
5. Stay within scope of order status, human representative requests, and return policies."""
                },
                *conversation_history
            ],
            functions=[
                {
                    "name": "check_order_status",
                    "description": "Check the status of an order",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The 4-digit order ID"
                            }
                        },
                        "required": ["order_id"]
                    }
                },
                {
                    "name": "save_contact_details",
                    "description": "Save customer contact details for human representative",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "full_name": {
                                "type": "string",
                                "description": "Customer's full name"
                            },
                            "email": {
                                "type": "string",
                                "description": "Customer's email address"
                            },
                            "phone": {
                                "type": "string",
                                "description": "Customer's phone number"
                            }
                        },
                        "required": ["full_name", "email", "phone"]
                    }
                }
            ],
            function_call="auto"
        )

        response_message = response.choices[0].message

        if response_message.function_call:
            function_name = response_message.function_call.name
            function_args = json.loads(response_message.function_call.arguments)

            if function_name == "check_order_status":
                order_id = function_args.get("order_id")
                if order_id and re.match(r'^\d{4}$', order_id):
                    status = check_order_status(order_id)
                    bot_response = status
                    waiting_for_order_id = False
                else:
                    bot_response = "Could you please provide me with the 4-digit order ID so I can check the status for you?"
                    waiting_for_order_id = True
            elif function_name == "save_contact_details":
                collecting_contact_details = True
                contact_details = {k: v for k, v in function_args.items() if v}
                bot_response = save_contact_details(**contact_details)
            else:
                bot_response = "I'm sorry, I couldn't process that request."
        else:
            bot_response = response_message.content

        score_tfidf = score_interaction_tfidf(user_message, bot_response)
        score_jaccard = jaccard_similarity(user_message, bot_response)

        print("Bot:", bot_response)
        log_conversation(user_message, bot_response)
        conversation_history.append({"role": "assistant", "content": bot_response})
        log_conversation(user_message, f"score jaccard: {score_jaccard}")
        log_conversation(user_message, f"score tfidf: {score_tfidf}")

if __name__ == "__main__":
    chat_with_openai()