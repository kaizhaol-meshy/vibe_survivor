# -*- coding: utf-8 -*-
import asyncio
import websockets
from aiohttp import web
import threading
import sys
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from graphics import Frame
import json  # Add this import at the top


class Server:
    def __init__(self, port=8080):
        self.current_frame = None
        self.dt = 0.016  # 60fps
        self.keys_pressed = {}  # Add this line to store key states
        self.mouse_pos = (0, 0)  # Add this line to store mouse position
        self.mouse_clicked = False  # Add this line to track mouse clicks
        self.app = web.Application()
        self.app.router.add_get("/", self.handle_index)
        self.port = port
        self.websocket_port = port + 1

    def update_frame(self, frame):
        self.current_frame = frame

    def get_key_pressed(self):
        """Return the current state of pressed keys"""
        return self.keys_pressed

    def get_mouse_info(self):
        """Return the current mouse position and click state"""
        # Reset click state after it's read
        clicked = self.mouse_clicked
        self.mouse_clicked = False
        return self.mouse_pos, clicked

    async def websocket_handler(self, websocket):
        try:
            while True:
                # Handle incoming key events
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=0.001)
                    data = json.loads(message)  # Changed from eval() to json.loads()
                    
                    # Check if it's a mouse event
                    if 'type' in data and data['type'] == 'mouse':
                        if 'clicked' in data and data['clicked']:
                            self.mouse_clicked = True
                        if 'x' in data and 'y' in data:
                            self.mouse_pos = (data['x'], data['y'])
                    else:
                        # It's a keyboard event - normalize key names
                        normalized_keys = {}
                        for key in data:
                            # Convert key to lowercase for letter keys
                            normalized_key = key.lower() if len(key) == 1 else key
                            normalized_keys[normalized_key] = True
                        self.keys_pressed = normalized_keys
                except asyncio.TimeoutError:
                    pass

                # Send frame data
                if self.current_frame:
                    await websocket.send(self.current_frame.serialize())
                await asyncio.sleep(self.dt)
        except websockets.exceptions.ConnectionClosed:
            pass

    async def handle_index(self, request):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Physics Simulation</title>
        </head>
        <body style="margin:0">
            <canvas id="canvas" width="1024" height="576" style="display:block;margin:0 auto;"></canvas>
            <script>
                const canvas = document.getElementById('canvas');
                const ctx = canvas.getContext('2d');

                function drawObject(obj) {{
                    switch(obj.type) {{
                        case 'sphere':
                            ctx.beginPath();
                            ctx.arc(obj.x, obj.y, obj.radius, 0, 2 * Math.PI);
                            ctx.fillStyle = obj.color;
                            ctx.fill();
                            break;

                        case 'rectangle':
                            ctx.fillStyle = obj.color;
                            ctx.fillRect(obj.x, obj.y, obj.width, obj.height);
                            break;

                        case 'text':
                            ctx.font = `${{obj.font_size}}px Arial`;
                            ctx.fillStyle = obj.color;
                            ctx.fillText(obj.text, obj.x, obj.y);
                            break;
                            
                        case 'circle':
                            ctx.beginPath();
                            ctx.arc(obj.x, obj.y, obj.radius, 0, 2 * Math.PI);
                            ctx.fillStyle = obj.color;
                            ctx.fill();
                            break;
                            
                        case 'triangle':
                            ctx.save();
                            ctx.translate(obj.x, obj.y);
                            ctx.rotate(obj.angle * Math.PI / 180);
                            
                            ctx.beginPath();
                            ctx.moveTo(0, -obj.size/2);
                            ctx.lineTo(-obj.size/2, obj.size/2);
                            ctx.lineTo(obj.size/2, obj.size/2);
                            ctx.closePath();
                            
                            ctx.fillStyle = obj.color;
                            ctx.fill();
                            ctx.restore();
                            break;
                            
                        case 'cross':
                            ctx.save();
                            ctx.translate(obj.x, obj.y);
                            
                            const halfSize = obj.size / 2;
                            const lineWidth = obj.size / 5;
                            
                            // 绘制十字形
                            ctx.fillStyle = obj.color;
                            
                            // 水平线
                            ctx.fillRect(-halfSize, -lineWidth/2, obj.size, lineWidth);
                            
                            // 垂直线
                            ctx.fillRect(-lineWidth/2, -halfSize, lineWidth, obj.size);
                            
                            ctx.restore();
                            break;
                    }}
                }}

                function connectWebSocket() {{
                    const ws = new WebSocket(`ws://${{window.location.hostname}}:{self.websocket_port}`);
                    const keysPressed = {{}};

                    // Add key event listeners
                    window.addEventListener('keydown', (event) => {{
                        // Prevent default behavior for game controls
                        if (['w', 'a', 's', 'd', 'q', ' '].includes(event.key.toLowerCase())) {{
                            event.preventDefault();
                        }}
                        keysPressed[event.key] = true;
                        ws.send(JSON.stringify(keysPressed));
                    }});

                    window.addEventListener('keyup', (event) => {{
                        delete keysPressed[event.key];
                        ws.send(JSON.stringify(keysPressed));
                    }});
                    
                    // Add mouse event listeners
                    canvas.addEventListener('mousemove', (event) => {{
                        const rect = canvas.getBoundingClientRect();
                        const x = event.clientX - rect.left;
                        const y = event.clientY - rect.top;
                        ws.send(JSON.stringify({{
                            type: 'mouse',
                            x: x,
                            y: y
                        }}));
                    }});
                    
                    canvas.addEventListener('click', (event) => {{
                        const rect = canvas.getBoundingClientRect();
                        const x = event.clientX - rect.left;
                        const y = event.clientY - rect.top;
                        ws.send(JSON.stringify({{
                            type: 'mouse',
                            x: x,
                            y: y,
                            clicked: true
                        }}));
                    }});

                    ws.onmessage = function(event) {{
                        const objects = JSON.parse(event.data);

                        // Clear canvas
                        ctx.clearRect(0, 0, canvas.width, canvas.height);

                        // Draw all objects
                        objects.forEach(drawObject);
                    }};

                    ws.onclose = function() {{
                        console.log('WebSocket connection closed. Reconnecting...');
                        setTimeout(connectWebSocket, 1000);
                    }};

                    ws.onerror = function(error) {{
                        console.error('WebSocket error:', error);
                    }};
                }}

                connectWebSocket();
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type="text/html")

    def start(self):
        self.server_thread = threading.Thread(target=lambda: asyncio.run(self._start()))
        self.server_thread.daemon = True
        self.server_thread.start()

    async def _start(self):
        # Setup file watcher
        event_handler = FileChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, path=".", recursive=False)
        observer.start()

        # Start websocket server
        ws_server = await websockets.serve(
            self.websocket_handler, "0.0.0.0", self.websocket_port
        )

        # Start HTTP server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", self.port)
        await site.start()

        print("Servers started:")
        print(f"- Web server running at http://localhost:{self.port}")
        print(f"- WebSocket server running at ws://localhost:{self.websocket_port}")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down servers...")
            # Clean shutdown
            observer.stop()
            observer.join()
            ws_server.close()
            await ws_server.wait_closed()
            await runner.cleanup()


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = 0

    def on_modified(self, event):
        if event.src_path.endswith("server.py"):
            current_time = time.time()
            if current_time - self.last_modified > 1:  # Debounce multiple events
                self.last_modified = current_time
                print("\nServer restarting...")
                os.execv(sys.executable, ["python"] + sys.argv)


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.start())
