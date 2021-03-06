import asyncio
from fastapi import FastAPI, Request
from starlette.websockets import WebSocket, WebSocketDisconnect
from .notifier import Notifier
from .log import logger as log


notifier = Notifier()
app = FastAPI()


@app.get("/ping")
async def ping(request: Request):
    """ Проверка работы сервиса """
    host, port = request.client.host, request.client.port
    log.info(f'=> {host}:{port} <= pong')
    return "pong"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """ Стрим данных в WebSocket """
    await notifier.add(websocket)
    try:
        while True:
            await websocket.receive_text()
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        try:
            notifier.connections.index(websocket)
            notifier.remove(websocket)
        except ValueError as err:
            log.error(f"ERROR => {err}")
