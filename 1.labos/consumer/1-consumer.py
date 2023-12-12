import asyncio
import os
import json
from datetime import datetime
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    DataLakeDirectoryClient,
    FileSystemClient,
)
from azure.identity import DefaultAzureCredential
from azure.eventhub.aio import EventHubConsumerClient


EVENT_HUB_CONNECTION_STR = "Endpoint=sb://vjezbavjestina.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=VQDxmFIqJyd3cyYcKzWx2U3kavp8Xg8fi+AEhKdyYuc="
EVENT_HUB_NAME = "hubvjestina"
SAS_TOKEN = "ndtF8WKlwJ3nSsGWwThRAtqY+CsXmUJeV2gRDhdX6Ss1KAiEdaPZpNzVVN1qeaGCk1Mm09OdIcIy+AStpWBlLw=="
CONTAINER_NAME = "datalakecontainer"


async def on_event(partition_context, event):
    json_body = event.body_as_json(encoding="UTF-8")

    account_url = f"https://storageoblak.dfs.core.windows.net"
    service_client = DataLakeServiceClient(account_url, credential=SAS_TOKEN)
    file_system_client = service_client.get_file_system_client(
        file_system=CONTAINER_NAME
    )

    for objava in json_body:
        dt = datetime.utcfromtimestamp(objava["data"]["created_utc"])
        dir = dt.strftime("%Y/%m/%d/%H/%M")

        dir_client = file_system_client.create_directory(dir)
        file_client = dir_client.get_file_client(f"{objava['data']['name']}.json")

        file_client.upload_data(str(objava["data"]), overwrite=True)

        print(f"Uploaded {objava['data']['title']} to {dir}")
    # Update the checkpoint so that the program doesn't read the events
    # that it has already read when you run it next time.
    await partition_context.update_checkpoint(event)


async def main():
    # Create a consumer client for the event hub.
    client = EventHubConsumerClient.from_connection_string(
        EVENT_HUB_CONNECTION_STR,
        consumer_group="$Default",
        eventhub_name=EVENT_HUB_NAME,
    )
    async with client:
        # Call the receive method. Read from the beginning of the
        # partition (starting_position: "-1")
        await client.receive(on_event=on_event, starting_position="-1")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    print("Loop!!")
    # Run the main method.
    loop.run_until_complete(main())
    print("Run done!!")
