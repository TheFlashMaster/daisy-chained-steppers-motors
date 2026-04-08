#name "main.py" to run on micropython on startup
from machine import UART, Pin
import network
import socket
import time
import re
import secrets

# --- CONFIG ---
SSID = secrets.WIFI_2_SSID
PASSWORD = secrets.WIFI_2_PASSWORD

# UART0 init (TX=GP0, RX=GP1)
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
led = Pin("LED", Pin.OUT)

# --- WIFI Connect ---
def connect_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    print("Connecting to WIFI...", end="")
    while not wlan.isconnected():
        led.toggle()
        time.sleep(0.5)
        print(".", end="")
    
    led.value(1)
    ip = wlan.ifconfig()[0]
    print(f"\nConnected! IP-Adresse: {ip}")
    return ip

def get_html(p1="0", s1="5000", p2="0", s2="5000", p3="0",s3="3000"):
    return f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: sans-serif; text-align: center; padding: 10px; background: #eee; }}
            .card {{ background: white; padding: 15px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 90%; max-width: 350px; }}
            input[type=number], button {{ padding: 10px; margin: 5px; font-size: 16px; border-radius: 5px; border: 1px solid #ccc; width: 80%; }}
            .slider {{ width: 90%; margin: 10px 0; }}
            .btn-move {{ background: #008CBA; color: white; border: none; cursor: pointer; }}
            .btn-both {{ background: #4CAF50; color: white; border: none; cursor: pointer; }}
            .btn-home {{ background: #f44336; color: white; border: none; cursor: pointer; }}
            .label {{ font-weight: bold; margin-top: 15px; color: #333; }}
            hr {{ margin: 15px 0; border: 0; border-top: 5px solid #ddd; }}
            #joystick-area {{ 
                width: 330px; height: 70px; background: #444; 
                margin: 15px auto; position: relative; border: 2px solid #666; overflow: hidden;
            }}
            #dot {{ 
                width: 15px; height: 15px; background: #00ff00; 
                border-radius: 50%; position: absolute; 
                
                transform: translate(-50%, -50%);
                box-shadow: 0 0 10px #00ff00;
            }}
            #dot2 {{ 
                width: 8px; height: 8px; background: #ffff00; 
                border-radius: 50%; position: absolute; 
                
                transform: translate(-50%, -50%);
                box-shadow: 0 0 10px #ffff00;
            }}
            .info {{ font-size: 0.8em; color: #aaa; margin-top: 10px; }}
        </style>
        <script>
            let dotX = {p1} / 10;
            let dotY = {p2} / 10;
            const areaSizeX = 330; 
            const areaSizeY = 50; 
            const speed = 5; 
            const turn = 15; 
            let rotation = {p3};
            const radius = 20;

            function moveDot(e) {{
                const key = e.key.toLowerCase();
                if (key === 'w') dotY -= speed;
                if (key === 's') dotY += speed;
                if (key === 'a') dotX -= speed;
                if (key === 'd') dotX += speed;
                if (key === 'q') rotation += turn;
                if (key === 'e') rotation -= turn;

                dotX = Math.max(0, Math.min(areaSizeX, dotX));
                dotY = Math.max(0, Math.min(areaSizeY, dotY));
                rotation = Math.max(0, Math.min(150, rotation));

                const dot = document.getElementById('dot');
                dot.style.left = dotX + "px";
                dot.style.top = dotY + "px";
                
                let displayRotation = rotation + 15; 

                let radiant = displayRotation * (Math.PI / 180);

                let dotX2 = dotX + radius * Math.cos(radiant);
                let dotY2 = dotY + radius * Math.sin(radiant);

                const dot2 = document.getElementById('dot2');
                dot2.style.left = dotX2 + "px";
                dot2.style.top = dotY2 + "px";

                document.getElementById('coord-display').innerText = "X: " + dotX*10 + " | Y: " + dotY*10 + " | T: " + rotation;
                s1.value = dotX*10;
                n1.value = dotX*10;
                v1.innerText = dotX*10;
                
                s2.value = dotY*10;
                n2.value = dotY*10;
                v2.innerText = dotY*10;
                
                s3.value = rotation;
                n3.value = rotation;
                
            }}
            window.onload = function() {{
            moveDot({{ key: "" }});
            }}
        </script>
    </head>
    <body onkeydown="moveDot(event)">
        <div class="card">
            <h2>Motor Control</h2>
            
            <div id="joystick-area">
                <div id="dot"></div>
                <div id="dot2"></div>
            </div>
            <div id="coord-display" style="margin-bottom: 0px;">X: {p1} | Y: {p2} | T: {p3}</div>
            
            <hr>

            <form action="/set" method="get">
                <div class="label">Motor 1: <span id="v1">{p1}</span></div>
                <input type="number" id="n1" name="p1" min="0" max="3300" value="{p1}">
                <input type="range" id="s1" class="slider" min="0" max="3300" value="{p1}" oninput="n1.value=this.value; v1.innerText=this.value">
                <input type="number" name="sp1" value="{s1}">
                <button type="submit" name="action" value="m1" class="btn-move">Move M1</button>

                <hr>

                <div class="label">Motor 2: <span id="v2">{p2}</span></div>
                <input type="number" id="n2" name="p2" min="0" max="500" value="{p2}">
                <input type="range" id="s2" class="slider" min="0" max="500" value="{p2}" oninput="n2.value=this.value; v2.innerText=this.value">
                <input type="number" name="sp2" value="{s2}">
                <button type="submit" name="action" value="m2" class="btn-move">Move M2</button>

                <hr>

                <div class="label">Motor 3: <span id="v3">{p3}</span></div>
                <input type="number" id="n3" name="p3" min="0" max="150" value="{p3}">
                <input type="range" id="s3" class="slider" min="0" max="150" value="{p3}" oninput="n3.value=this.value; v3.innerText=this.value">
                <input type="number" name="sp3" value="{s3}">
                <button type="submit" name="action" value="m3" class="btn-move">Move M3</button>

                <hr style="border-top: 5px solid #444;">

                <button type="submit" name="action" value="both" class="btn-both">MOVE SYNC</button>
                <button type="submit" name="action" value="home" class="btn-home">HOME ALL</button>
            </form>
        </div>
    </body>
    </html>
    """

# --- Server Start ---
ip = connect_wlan()
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 80))
s.listen(1)

lp1, ls1 = "0", "5000"
lp2, ls2 = "0", "5000"
lp3, ls3 = "0", "3000"
diff_m1 = 0

while True:
    try:
        cl, addr = s.accept()
        request = cl.recv(1024).decode('utf-8')
        
        if "/set?" in request:
            def get_val(name, req):
                match = re.search(name + "=([^&\\s]*)", req)
                return match.group(1) if match else None
            
            # Werte aus URL extrahieren
            action = get_val("action", request)
            if action == "m1" or action == "both":
                p1, sp1 = get_val("p1", request), get_val("sp1", request)
                diff_m1 = int(p1) - int(lp1)
                time_m1 = ((((int(1_000_000 / int(sp1)))*2.1)*abs(diff_m1)*16)/1000000) # zeitpro schritt * schritte zu bewegen * 16 wegen microstepping +.01 ausgleichs/timingfactor
                if p1: lp1, ls1 = p1, sp1
            
            if action == "m2" or action == "both":
                p2, sp2 = get_val("p2", request), get_val("sp2", request)
                diff_m2 = int(p2) - int(lp2)
                if p2: lp2, ls2 = p2, sp2
                
            if action == "m3" or action == "both":
                p3, sp3 = get_val("p3", request), get_val("sp3", request)
                diff_m3 = int(p3) - int(lp3)
                if p3: lp3, ls3 = p3, sp3
            
            print("---------------------------------")
            
            if action == "both" and str(diff_m1) != "0":
                ls2 = int((32 * abs(diff_m2)) / time_m1)
                ls3 = int((32 * abs(diff_m3)) / time_m1)
                print(f"Chainged speed for M2: {ls2}, Chainged speed for M3: {ls3}; movement m1: {diff_m1}, time: {time_m1}")

            
            print("Uart send: ")
            if action == "m1":
                uart.write(f"1,{lp1},{ls1}\n")
                print(f"1,{lp1},{ls1}")
                print(f"Movement m1: {diff_m1} Time: {time_m1}seconds")
            elif action == "m2":
                uart.write(f"2,{lp2},{ls2}\n")
                print(f"2,{lp2},{ls2}")
                print(f"Movement m2: {diff_m2}")
            elif action == "m3":
                uart.write(f"3,{lp3},{ls3}\n")
                print(f"3,{lp3},{ls3}")
                print(f"Movement m3: {diff_m3}")

            elif action == "both":
                uart.write(f"1,{lp1},{ls1}\n")
                print(f"1,{lp1},{ls1}")
                print(f"Movement m1: {diff_m1} Time: {time_m1}seconds")
                time.sleep(0.05)
                uart.write(f"2,{lp2},{ls2}\n")
                print(f"2,{lp2},{ls2}")
                print(f"Movement m2: {diff_m2}")
                time.sleep(0.05)
                uart.write(f"3,{lp3},{ls3}\n")
                print(f"3,{lp3},{ls3}")
                print(f"Movement m3: {diff_m3}")
            
            elif action == "home":
                lp1 = 0
                lp2 = 0
                lp3 = 80
                uart.write(f"1,home,{ls1}\n")
                print(f"1,home,{ls1}")
                time.sleep(0.05)
                uart.write(f"2,home,{ls2}\n")
                print(f"2,home,{ls2}")
                time.sleep(0.05)
                uart.write(f"3,home,{ls3}\n")
                print(f"3,home,{ls3}")
                
            #Current_m1 = lp1
            #Current_m2 = lp2

            
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(get_html(lp1, ls1, lp2, ls2, lp3, ls3))
        cl.close()
    except Exception as e:
        print("Fehler:", e)
        if 'cl' in locals(): cl.close()
