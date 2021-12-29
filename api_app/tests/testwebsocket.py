import asyncio
import websockets

def test_url(url):
    async def inner():
        async with websockets.connect(url) as websocket:
            result = await websocket.recv()
            print(result)
            await websocket.send('[{ "type":"entrance", "data":"hello!", "room_name":"room1", "user":"can" }]')
            response = await websocket.recv()
            print(response)
    return asyncio.get_event_loop().run_until_complete(inner())

test_url("ws://127.0.0.1:8080/api/chat/room1/can")