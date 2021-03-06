import socket
import tqdm
import os
import sys

SEPARATOR = "+=+"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

# get line arguments
filename = sys.argv[1]
host = sys.argv[2]
port = int(sys.argv[3])

# get the file size
filesize = os.path.getsize(filename)

# create the client socket
s = socket.socket()

print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected.")

# send the filename and filesize
s.send(f"{filename}{SEPARATOR}{filesize}".encode())

# start sending the file
progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
with open(filename, "rb") as f:
    for _ in progress:
        # each time read given amount of bytes
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            # file transmitting is done
            break
        s.sendall(bytes_read)
        progress.update(len(bytes_read))

# close the socket
s.close()