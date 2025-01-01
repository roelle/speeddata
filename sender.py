import socket
import time
import random
import io
import avro.schema
from avro.io import DatumWriter, BinaryEncoder
DEBUG = True
if DEBUG:
    from avro.datafile import DataFileWriter

WORD_FILE = "/usr/share/dict/american-english"

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    schema = avro.schema.parse(open("schema.avsc", "r", encoding='utf-8').read())
    writer = DatumWriter(schema)
    if DEBUG:
        fwriter = DataFileWriter(open("data/data.avro", "wb"), DatumWriter(), schema)
        fwriter.sync_marker = b'\xa4\x8a\x1e\x90\x05\x04$x\nh3\x7f\xc2P\x95c'
        fwriter.flush()
        print(fwriter.sync_marker)
        print(' '.join(f'{byte:02X}' for byte in fwriter.sync_marker))
    words = [word.rstrip('\n') for word in open(WORD_FILE, 'r', encoding='utf-8')]
    index = 0
    try:
        while True:
            word = words[random.randrange(0, len(words))]
            message = f'The word of the moment is: {word}'
            t = time.time_ns()

            data = {
                "time": t,
                "message": message, 
                "number": index
            }

            writer.write(data, BinaryEncoder(bytes_io := io.BytesIO()))
            if DEBUG:
                fwriter.append(data)
                fwriter.flush()
            sock.sendto(bytes_io.getvalue(), ("127.0.0.1", 26000))

            print(t, message, index)
            print(bytes_io.getvalue(), '\n')

            index += 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        if DEBUG:
            fwriter.close()

if __name__ == "__main__":
    main()
