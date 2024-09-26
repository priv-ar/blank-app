import streamlit as st
import json
import boto3

# Initialize Lambda client
try:
    lambda_client = boto3.client(
        'lambda',
        region_name='eu-west-1',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
    )
except Exception as e:
    st.error(f"Fail Lambda init: {e}")

# Chatbot Title
st.title("XYZ Store - 🤖 Virtual Assistant")
st.subheader("Your favorite store for XYZ products!")

# Polite introduction of the chatbot
st.write("""
Hello! Welcome to XYZ Store, the best place for all your XYZ needs. I’m your friendly virtual assistant, here to help you with any questions or issues related to our products and services.
I can assist you with common customer support topics such as password resets, tracking orders, return policies, and more.
Please provide your question and some context so I can help you more effectively.
""")

# Create a session state variable to store chat messages and conversation progress
if "messages" not in st.session_state:
    st.session_state.messages = []
if "step" not in st.session_state:
    st.session_state.step = "ask_name"  # New step starts with asking the user's name
if "ask_name" not in st.session_state:
    st.session_state.ask_name = "" # To store the user's name

# Display the chat messages from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Step 1: Ask for the user's name
if st.session_state.step == "ask_name":
    user_name = st.text_input("What is your name?")
    if user_name:
        # Store the user's name in session state
        st.session_state.user_name = user_name

        # Add to chat history
        st.session_state.messages.append({"role": "user", "content": f"My name is {user_name}."})
        
        # Move to the next step (ask email)
        st.session_state.step = "ask_email"
        st.rerun()

# Step 2: Ask for the user's email (but do not store it)
elif st.session_state.step == "ask_email":
    user_email = st.text_input(f"Hello {st.session_state.user_name}, thank you for your answer. What is your email?")
    if user_email:
        # Add to chat history but do not store the email
        st.session_state.messages.append({"role": "user", "content": f"My email is {user_email}."})
        
        # Move to the next step (ask question)
        st.session_state.step = "ask_question"
        st.rerun()

# Step 3: Ask for the user's question
elif st.session_state.step == "ask_question":
    user_question = st.chat_input("Thank you. What is your question?")
    if user_question:
        # Add user's question to chat history
        st.session_state.messages.append({"role": "user", "content": user_question})
        st.session_state.user_question = user_question  # Store the question
        st.session_state.step = "ask_context"  # Move to the next step
        st.rerun()  # Rerun to show the context input

# Step 4: Ask for the context after the question is provided
elif st.session_state.step == "ask_context":
    user_context = st.chat_input("Thanks for your request. Could you please provide the context for your question?")
    if user_context:
        # Add user's context to chat history
        st.session_state.messages.append({"role": "user", "content": user_context})

        # Prepare the payload (data) to send to the Lambda function
        payload = {
            "question": st.session_state.user_question,
            "context": user_context
        }

        arn_url = "arn:aws:lambda:eu-west-1:640167380126:function:CallSageMakerLLM"

        try:
            # Invoke Lambda function
            response = lambda_client.invoke(
                FunctionName=arn_url,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )

            # Read and parse response
            response_payload = json.loads(response['Payload'].read())
            
            # Check for errors in the response
            if 'FunctionError' in response:
                st.error(f"Lambda function error: {response['FunctionError']}")

            # Check if the request was successful
            if response_payload.get('statusCode') == 200:
                # Parse the result
                result = json.loads(response_payload['body'])

                assistant_response = result['Message']

                # Display assistant's response
                with st.chat_message("assistant"):
                    st.markdown(assistant_response)

                # Store the assistant's response in session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response
                })            
            else:
                st.error(f"Error: Could not get a valid response, status code: {response_payload.get('statusCode')}")
        except Exception as e:
            st.error(f"Error invoking Lambda: {e}")

        # Reset to ask a new question after completing the interaction
        st.session_state.step = "ask_question"
        st.rerun()

    # Only display an error if the context is missing
    elif not user_context:
        st.error("Please provide the context for your question.")
