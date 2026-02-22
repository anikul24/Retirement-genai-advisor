import boto3
import json

prompt_data = """You are a expert poet and your task is to compose a poem on hope and inspiration in the hardships of life."""


bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')


payload = {
    "anthropic_version": "bedrock-2023-05-31",
    "messages": [
        {
            "role": "user",
            "content": prompt_data
        }
    ],
    "max_tokens": 1024,
    "temperature": 0.7

   }

print(type(payload))


body = json.dumps(payload)

#print("Request Body: ", body)

model_id = "us.anthropic.claude-opus-4-5-20251101-v1:0"


response = bedrock_client.invoke_model(
    modelId=model_id,
    body=body,
    accept='application/json',
    contentType='application/json'
)



response_body = response.get('body').read()

print(f'response_body:{response_body}')


response_output = json.loads(response_body.decode('utf-8'))

print("Generated Poem: ", response_output['content'][0]['text'])