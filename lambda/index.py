import os
import json
import urllib.request

API_URL = os.environ.get("API_URL")
print(">> Loaded API_URL =", API_URL)

def lambda_handler(event, context):
    print(">> lambda_handler invoked")
    try:
        body = json.loads(event["body"])
        print(">> Event body parsed:", body)

        message = body.get("message")
        print(">> Prompt message:", message)

        # 会話履歴があれば
        conversation_history = body.get("conversationHistory", [])
        print(">> Conversation history length:", len(conversation_history))

        payload = json.dumps({
            "prompt": message,
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9
        }).encode("utf-8")
        print(">> Payload to POST:", payload)

        req = urllib.request.Request(
            API_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as res:
            resp_bytes = res.read()
        print(">> Raw response bytes:", resp_bytes)

        result = json.loads(resp_bytes)
        print(">> Parsed JSON result:", result)

        assistant_response = result.get("generated_text")
        print(">> Assistant response:", assistant_response)

        messages = conversation_history.copy()
        messages.append({"role": "assistant", "content": assistant_response})

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }

    except Exception as error:
        print("!! Exception occurred:", str(error))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
