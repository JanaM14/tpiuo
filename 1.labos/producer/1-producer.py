import asyncio
import requests
import requests.auth
import json
from time import sleep

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub.exceptions import EventHubError
from azure.eventhub import EventData


CONNECTION_STR = "Endpoint=sb://newhubs.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=ZJmsHJbFBRJAn8dmF6IBgjStBHMT2PLi++AEhDZqBv8="
EVENTHUB_NAME = "newhubs"


async def run():
    client_auth = requests.auth.HTTPBasicAuth(
        "6dh64eDiNOG4dG06LEYfLQ", "i56BzqkJOQiReIW4wezh20HcrXTB7w"
    )
    post_data = {
        "grant_type": "password",
        "username": "jmm123478",
        "password": "severina123",
    }
    headers = {"User-Agent": "ChangeMeClient/0.1 by YourUsername"}
    response = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=client_auth,
        data=post_data,
        headers=headers,
    )
    var = response.json()
    headers = {
        "Authorization": f'bearer {var["access_token"]}',
        "User-Agent": "ChangeMeClient/0.1 by YourUsername",
    }
    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    after = ""
    for i in range(5):
        url = f"https://oauth.reddit.com/r/dataengineering/top/?t=all&limit=10&after={after}"
        response = requests.get(url, headers=headers)
        res = response.json()
        after = res["data"]["after"]
        producer = EventHubProducerClient.from_connection_string(
            conn_str=CONNECTION_STR, eventhub_name=EVENTHUB_NAME
        )

        async with producer:
            event_data_batch = await producer.create_batch()
            for post in res["data"]["children"]:
                event_data_batch.add(EventData(json.dumps(post)))
                print(f"Poslala: {post['data']['title']}")
            await producer.send_batch(event_data_batch)
        sleep(10)

    while True:
        sleep(3600)
        continue


print("prije!")
asyncio.run(run())
print("poslije!")
