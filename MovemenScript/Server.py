import asyncio
import json
import threading
import tkinter as tk
import websockets

# Shared state
state = {"Base": 0, "Shoulder": 0, "Elbow": 0, "WristX": 0, "WristY": 0, "Speed": 0}
clients = set()

lastBase = state["Base"]
lastShoulder = state["Shoulder"]
lastElbow = state["Elbow"]
lastWristX = state["WristX"]
lastWristY = state["WristY"]
lastSpeed = state["Speed"]

#WEBSOCKET SERVER
async def ws_handler(websocket, path):
    clients.add(websocket)
    print(f"[WebSocket] Client connected: {websocket.remote_address}")
    try:
        while True:
            await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)
        print(f"[WebSocket] Client disconnected: {websocket.remote_address}")  


async def broadcaster():
    global lastBase, lastShoulder, lastElbow, lastWristX, lastWristY, lastSpeed
    while True:
        # Only send if state changed
        if (state["Base"] != lastBase or
            state["Shoulder"] != lastShoulder or
            state["Elbow"] != lastElbow or
            state["WristX"] != lastWristX or
            state["WristY"] != lastWristY or
            state["Speed"] != lastSpeed):

            msg = json.dumps(state)
            dead = []

            for ws in list(clients):
                try:
                    await ws.send(msg)
                except:
                    dead.append(ws)

            for ws in dead:
                clients.remove(ws)

            # Debug print
            if clients:
                print(f"[WebSocket] Sending {msg} to {len(clients)} clients")

            # Update last values
            lastBase = state["Base"]
            lastShoulder = state["Shoulder"]
            lastElbow = state["Elbow"]
            lastWristX = state["WristX"]
            lastWristY = state["WristY"]
            lastSpeed = state["Speed"]

        await asyncio.sleep(0.05)


async def ws_main():
    server = await websockets.serve(ws_handler, "0.0.0.0", 8765, ping_interval=5, ping_timeout=2)
    print("[WebSocket] Server started on port 8765")
    asyncio.create_task(broadcaster())
    await asyncio.Future()  # run forever


def start_ws_server():
    asyncio.run(ws_main())

#CallBacks
def on_Base(val):
    state["Base"] = int(float(val))
def on_Shoulder(val):
    state["Shoulder"] = int(float(val))

def on_Elbow(val):
    state["Elbow"] = int(float(val))

def on_WristX(val):
    state["WristX"] = int(float(val))

def on_WristY(val):
    state["WristY"] = int(float(val))
    
def on_Speed(val):
    state["Speed"] = int(float(val))

#GUI

def start_gui():
    root = tk.Tk()
    root.title("Servo Controller")
    root.geometry("800x400") 

    InitialAngle = 90

    tk.Label(root, text="Base").pack()
    BaseSlider =  tk.Scale(root, from_=0, to=180, orient="horizontal", command=on_Base)
    BaseSlider.pack(fill="x")
    BaseSlider.set(InitialAngle)

    tk.Label(root, text="Shoulder").pack()
    ShoulderSlider = tk.Scale(root, from_=0, to=180, orient="horizontal", command=on_Shoulder)
    ShoulderSlider.pack(fill="x")
    ShoulderSlider.set(InitialAngle)

    tk.Label(root, text="Elbow").pack()
    ElbowSlider = tk.Scale(root, from_=0, to=180, orient="horizontal", command=on_Elbow)
    ElbowSlider.pack(fill="x")
    ElbowSlider.set(InitialAngle)

    tk.Label(root, text="WristX").pack()
    WristXSlider = tk.Scale(root, from_=0, to=180, orient="horizontal", command=on_WristX)
    WristXSlider.pack(fill="x")
    WristXSlider.set(InitialAngle)

    tk.Label(root, text="WristY").pack()
    WristYSlider = tk.Scale(root, from_=0, to=180, orient="horizontal", command=on_WristY)
    WristYSlider.pack(fill="x")
    WristYSlider.set(InitialAngle)

    tk.Label(root, text="Speed").pack()
    SpeedSlider = tk.Scale(root, from_=0, to=10, orient="horizontal", command=on_Speed)
    SpeedSlider.pack(fill="x")
    SpeedSlider.set(0)

    root.mainloop()

def main():
    ws_thread = threading.Thread(target=start_ws_server, daemon=True)
    ws_thread.start()
    start_gui()

if __name__ == "__main__":
    main()
