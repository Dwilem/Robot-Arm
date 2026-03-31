import asyncio
import websockets
import threading
import face_recognition
import cv2
import numpy as np
import queue
import time
import logging

frame_queue = queue.Queue(maxsize=1) 

# Load known face encodings and names
known_image1 = face_recognition.load_image_file("person1.jpg")
known_encoding1 = face_recognition.face_encodings(known_image1)[0]


known_encodings = [known_encoding1]
known_names = ["Agukis"]

logging.basicConfig(level=logging.DEBUG)

def FaceRecognisionLoop(stop_event):
    face_locations = []
    names = []
    frame_count = 0
    while not stop_event.is_set():
        if not frame_queue.empty():
            frame = frame_queue.get()
            processed_frame, names, face_locations= recognize_faces_in_frame(frame)
            
            
            # Process frame every 3rd frame
            if frame_count % 3 == 0:  # every 3rd frame
                processed_frame, names, face_locations = recognize_faces_in_frame(frame)
            else:
                processed_frame = frame
                #names = []
            frame_count += 1
            
            for (top, right, bottom, left), names in zip(face_locations, names):

                # Draw rectangle and label
                cv2.rectangle(processed_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(processed_frame, names, (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            print("Detected:", names)

            # Display using OpenCV (non-blocking)
            cv2.imshow("Face Recognition", processed_frame)
            cv2.waitKey(1)
            #cv2.destroyAllWindows()
            print("Detected:", names)
        else:
            time.sleep(0.1)
    cv2.destroyAllWindows()

def recognize_faces_in_frame(frame):

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert BGR to RGB if needed
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_frame, model='hog')
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    face_names = []

    face_locations = [(top*4, right*4, bottom*4, left*4) for (top,right,bottom,left) in face_locations]

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare with known faces
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"

        # Pick best match
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_names[best_match_index]

        face_names.append(name)
        
        """
        # Draw rectangle and label
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        """

    return frame, face_names, face_locations



# Simple handler for new WebSocket connections
async def handler(websocket, path):
    print(f"New connection from {websocket.remote_address}")
    frame_count = 0
    try:
        image_bytes = b""
        async for message in websocket:
            if isinstance(message, bytes):
                print(f"Received {len(message)} bytes")
                image_bytes += message
            elif message == b"EOF" or message == "EOF":
                print("End of Frame received")

                # Convert bytes to OpenCV image
                nparr = np.frombuffer(image_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                # Check if frame is valid
                if frame is None:
                    print("Failed to decode frame")
                    image_bytes = b""
                    continue

                if not frame_queue.full():
                    frame_queue.put(frame)
                else:
                    # Replace old frame if full
                    try:
                        frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                    frame_queue.put(frame)

                image_bytes = b""
                #await websocket.send("Image received")
            else:
                print(f"Received t`ex`t: {message}")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")

# Start server
async def StartServer():

    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket server running on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    
    stop_event = threading.Event()
    threading.Thread(target=lambda: asyncio.run(StartServer()), daemon=True).start()
    threading.Thread(target=FaceRecognisionLoop, args=(stop_event,), daemon=True).start()

    print("Press Ctrl+C to exit")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
        print("Exiting...")





