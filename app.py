import os
import openai
from slack_bolt import App
from slack_sdk import WebClient

app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
)

client = WebClient(
    token=os.getenv("SLACK_BOT_TOKEN"),
)


@app.event("message")
def handler(client, event, logger):
    try:

        messages = []

        if event.get("thread_ts"):
            replies = client.conversations_replies(
                channel=event.get("channel"),
                ts=event.get("thread_ts"),
            )
            assert "ok" in replies
            for message in replies.get("messages"):
                if "bot_id" in message:
                    messages.append({"role": "assistant", "content": message.get("text")})
                else:
                    messages.append({"role": "user", "content": message.get("text")})
        else:
            messages.append({"role": "user", "content": event.get("text")})

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=messages,
        )

        response = client.chat_postMessage(
            channel=event.get("channel"),
            thread_ts=event.get("thread_ts", event.get("ts")),
            text=completion["choices"][0]["message"]["content"],
        )
        assert "ok" in response

    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    app.start(port=int(os.getenv("PORT", 3000)))
