import os
import streamlit as st
import requests
import json
import boto3

# Get AWS credentials from environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

lambda_client = boto3.client(
    'lambda',
    region_name='eu-west-1',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Set the title for the Streamlit app
st.title("Virtual Assistant for Customer Support")

# Input fields for question and context
question = st.text_input("Enter your question:")
context = st.text_area("Provide the context for your question:")

# Button to send the question and context
if st.button("Get Answer"):
    if question and context:
        # Prepare the payload (data) to send to the Lambda function
        payload = {
            "question": question,
            "context": context
        }

        arn_url = "arn:aws:lambda:eu-west-1:640167380126:function:CallSageMakerLLM"

        try:
             # Invoke Lambda function
            response = lambda_client.invoke(
                FunctionName=arn_url,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )

            # Read response
            response_payload = json.loads(response['Payload'].read())
            
            # Check if the request was successful
            if response_payload.get('statusCode') == 200:
                # Parse and display the result
                result = json.loads(response_payload['body'])
                st.write(f"Question: {result['Question']}")
                st.write(f"Answer: {result['Message']}")
            else:
                st.error("Error: Could not get a valid response from the model")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Please enter both a question and context.")
