import logging
logging.getLogger("prawcore").setLevel(logging.ERROR)
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import os
from pymongo import MongoClient
from Generate_response.retrieve import DataRetriever
import time
import asyncio
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from inject.inject import MainInjector

class ResponseGenerator:
    def __init__(self, model_path="D:\\Intern\\Survey_sparrow\\Conversniper\\Generate_response\\final_model"):
        self.model_path = model_path
        self.model, self.tokenizer, self.device = self._load_model()
        self.retriever = DataRetriever()
        
        self.mongo_client = MongoClient("mongodb://localhost:27017/")
        self.db = self.mongo_client["conversniper"]
        self.responses_collection = self.db["responses"]
        self.social_collection = self.db["social_data"]

        
        self.slack_bot_token = "xoxb-8510209012085-8513500318914-hbuSXq8KRCqdwEoRq1zX76b5" 
        self.slack_channel = "#response-approvals" 
        self.approver_id = "C08F3EATSH0"  
        self.slack_client = WebClient(token=self.slack_bot_token)  
        self.injector = MainInjector()

    def _load_model(self):
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model path '{self.model_path}' does not exist.")
            
            tokenizer = GPT2Tokenizer.from_pretrained(self.model_path)
            model = GPT2LMHeadModel.from_pretrained(self.model_path)
            
            tokenizer.pad_token = tokenizer.eos_token
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model.to(device)
            model.eval()
            
            print("Model loaded successfully")
            return model, tokenizer, device
        except Exception as e:
            print(f"Error loading model: {e}")
            return None, None, None

    def generate_response(self, post, sentiment, max_length=150, temperature=0.6, top_k=36):
        try:
            input_text = f"<|post|>{post}<|sentiment|>{sentiment}<|response|>"
            inputs = self.tokenizer(
                input_text,
                return_tensors='pt',
                truncation=True,
                max_length=max_length,
                padding=True  
            )
            input_ids = inputs['input_ids'].to(self.device)
            attention_mask = inputs['attention_mask'].to(self.device)

            with torch.no_grad():
                output = self.model.generate(
                    input_ids,
                    attention_mask=attention_mask,
                    max_length=max_length,
                    temperature=temperature,
                    top_k=top_k,
                    do_sample=True,
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            full_output = self.tokenizer.decode(output[0], skip_special_tokens=False)
            response = full_output.split("<|response|>")[1].strip() if "<|response|>" in full_output else full_output.strip()
            response = response.replace('<|endoftext|>', '').strip()

            return response
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Error—generation failed!"

    def store_response(self, post, sentiment, response, post_id, platform):
        """Store a response in MongoDB and notify the injector (bypassing Slack approval)."""
        response_data = {
            "post_id": post_id,
            "post_content": post,
            "sentiment": sentiment,
            "response": response,
            "platform": platform,
            "generated_at": time.time()
        }
        self.responses_collection.insert_one(response_data)
        print(f"Stored response for post_id: {post_id} in MongoDB")
        
        
        # if self.send_slack_approval(post, sentiment, response, post_id, platform):
        #     if self.check_slack_approval(post_id):
        #         asyncio.run(self.injector.inject_response(response, post_id, platform))
        #     else:
        #         print(f"Response for post_id {post_id} not approved—skipping injection.")
        # else:
        #     print(f"Failed to send Slack approval for post_id {post_id}—skipping injection.")
        
        # Directly trigger injection without approval (bypassing Slack)
        asyncio.run(self.injector.inject_response(response,platform))

    def send_slack_approval(self, post, sentiment, response, post_id, platform):
        """Send a Slack message for approval with interactive buttons (preserved for future use, but not called)."""
        try:
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*New Response for {platform} Post {post_id}*\n\n"
                                f"**Post Content:** {post}\n"
                                f"**Sentiment:** {sentiment}\n"
                                f"**Response:** {response}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Approve"},
                            "style": "primary",
                            "value": f"approve_{post_id}"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Reject"},
                            "style": "danger",
                            "value": f"reject_{post_id}"
                        }
                    ]
                }
            ]
            self.slack_client.chat_postMessage(channel=self.slack_channel, blocks=blocks)
            print(f"Sent Slack approval request for post_id: {post_id}")
            return True
        except SlackApiError as e:
            print(f"Failed to send Slack approval: {e}")
            return False

    def check_slack_approval(self, post_id, timeout=None):
        """Check Slack for approval/rejection via button clicks (preserved for future use, but not called)."""
        while True:
            try:
                result = self.slack_client.conversations_history(channel=self.slack_channel, limit=100)
                for message in result["messages"]:
                    if "blocks" in message and any(block["elements"][0]["value"].startswith(f"approve_{post_id}") for block in message["blocks"]):
                        self.slack_client.chat_delete(channel=self.slack_channel, ts=message["ts"])
                        return True
                    elif "blocks" in message and any(block["elements"][1]["value"].startswith(f"reject_{post_id}") for block in message["blocks"]):
                        self.slack_client.chat_delete(channel=self.slack_channel, ts=message["ts"])
                        print(f"Response for post_id {post_id} rejected by approver.")
                        return False
                time.sleep(10)
            except SlackApiError as e:
                if "channel_not_found" in str(e):
                    print(f"Slack API error—channel not found: {e}. Ensure '{self.slack_channel}' exists and the bot is invited.")
                    return False
                elif "missing_scope" in str(e):
                    print(f"Slack API error—missing scope: {e}. Ensure 'channels:history', 'groups:history', 'mpim:history', 'im:history' scopes are added.")
                    return False
                print(f"Error checking Slack approval: {e}")
                return False

    def get_responses(self, post_id=None, limit=10, since=None):
        query = {}
        if post_id:
            query["post_id"] = post_id
        if since:
            query["generated_at"] = {"$gte": since}
        
        responses = self.responses_collection.find(query).sort("generated_at", -1).limit(limit)
        return list(responses)

    def run(self, poll_interval=5):
        if self.model is None or self.tokenizer is None:
            print("Stopping due to model loading failure.")
            return

        print("\nStarting real-time response generation from MongoDB...\n")
        try:
            for content, sentiment, post_id, platform in self.retriever.stream_data(poll_interval):
                response = self.generate_response(content, sentiment)
                if response != "Error—generation failed!":
                    self.store_response(content, sentiment, response, post_id, platform)
        except KeyboardInterrupt:
            print("Stopping response generation...")

if __name__ == "__main__":
    generator = ResponseGenerator()
    generator.run(poll_interval=5)