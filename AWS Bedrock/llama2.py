import boto3
import json

prompt_data = """You are a expert poet and your task is to compose a poem on hope and inspiration in the hardships of life."""


bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

payload = {
    # "modelId": "llama-2-7b-chat",
    "prompt": "[INST]" + prompt_data + "[/INST]",
    "temperature": 0.7,
    # "topP": 0.9,
    # "topK": 0,
    "max_gen_len": 512,

   }

body = json.dumps(payload)

model_id = "meta.llama3-8b-instruct-v1:0"

response = bedrock_client.invoke_model(
    modelId=model_id,
    body=body
)

response_body = response['body'].read().decode('utf-8')
print("Response Body: ", response_body)

response_json = json.loads(response_body)
print("Generated Poem: ", response_json['generation'])