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

# Create a session state variable to store chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the chat messages from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input fields for the user's prompt and context
user_question = st.chat_input("What's your question?")
user_context = st.text_area("Please provide the context for your question")

# Ensure both fields are filled in before proceeding
if user_question and user_context:
    # Add user's message to chat history
    st.session_state.messages.append({"role": "user", "content": user_question})

    # Display the user's message
    with st.chat_message("user"):
        st.markdown(user_question)

    # Prepare the payload (data) to send to the Lambda function
    payload = {
        "question": user_question,
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
            # Parse and display the result
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
elif user_question or user_context:
    st.error("Please fill in both the question and the context.")
