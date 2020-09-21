import socket
from threading import Thread
import os
import tqdm


clients = []
BUFFER_SIZE = 4096
SEPARATOR = "+=+"


# Thread to listen to one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # close connection
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        # receive the file
        received = self.sock.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        
        # add 'copy' part
        filename_parts = filename.split('.')
        filename = ""
        for part in filename_parts[:-1]:
            filename = filename + "." + part
        filename = filename[1:] + "_copy"

        # check if such file exists and make another name
        i = 1
        while os.path.exists(filename + str(i) + "." + filename_parts[-1]):
            i = i+1
        filename = filename + str(i) + "." + filename_parts[-1]

        filename = os.path.basename(filename)

        filesize = int(filesize)

        # Write to the file stream
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            for _ in progress:
                # read bytes from the socket (receive)
                bytes_read = self.sock.recv(BUFFER_SIZE)
                if not bytes_read:    
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
        
        self._close()


def main():
    next_name = 1

    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # reuse address; in OS address will be reserved after app closed for a while
    # so if we close and imidiatly start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # listen to all interfaces at 8800 port
    sock.bind(('', 8800))
    sock.listen()
    
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        # start new thread to deal with client
        ClientListener(name, con).start()


if __name__ == "__main__":
    main()