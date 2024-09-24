import streamlit as st
import json
import boto3

# Initialize Lambda client
lambda_client = boto3.client(
    'lambda',
    region_name='eu-west-1'# ,
    # aws_access_key_id=AWS_ACCESS_KEY_ID,
    # aws_secret_access_key=AWS_SECRET_ACCESS_KEY
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
            print(response)

            # Read and parse response
            response_payload = json.loads(response['Payload'].read())
            
            # Check for errors in the response
            if 'FunctionError' in response:
                st.error(f"Lambda function error: {response['FunctionError']}")

            # Check if the request was successful
            if response_payload.get('statusCode') == 200:
                # Parse and display the result
                result = json.loads(response_payload['body'])
                st.write(f"Question: {result['Question']}")
                st.write(f"Answer: {result['Message']}")
            else:
                st.error(f"Error: Could not get a valid response, status code: {response_payload.get('statusCode')}")
        except Exception as e:
            st.error(f"Error invoking Lambda: {e}")
    else:
        st.error("Please enter both a question and context.")
