const dgram = require('dgram');
const WebSocket = require("ws");
const avro = require("avro-js");
const fs = require("fs");
const Long = require('long');

// Configuration
// Subscribe to decimated multicast stream (matches config/global.yaml)
const MULTICAST_GROUP = '239.1.1.2';
const UDP_PORT = 6001;
const WEBSOCKET_PORT = 8080;
const SCHEMA_FILE = '../../config/agents/example.avsc';

// Define a custom Avro type for Long
// See https://github.com/apache/avro/blob/main/lang/js/doc/Advanced-usage.md#custom-long-types
var longType = avro.types.LongType.using({
  fromBuffer: function (buf) {
    return new Long(buf.readInt32LE(), buf.readInt32LE(4));
  },
  toBuffer: function (n) {
    var buf = new Buffer(8);
    buf.writeInt32LE(n.getLowBits());
    buf.writeInt32LE(n.getHighBits(), 4);
    return buf;
  },
  fromJSON: Long.fromValue,
  toJSON: function (n) { return +n; },
  isValid: Long.isLong,
  compare: function (n, m) { return n.compare(m); }
});

// Load the Avro schema with the custom Long type
const schema = avro.parse(
    JSON.parse(fs.readFileSync(SCHEMA_FILE, "utf8")),
    {registry: {'long': longType}}
);
console.log(schema);

// Create a UDP socket for multicast
const udpSocket = dgram.createSocket({ type: 'udp4', reuseAddr: true });

// Create a WebSocket server
const wss = new WebSocket.Server({ port: WEBSOCKET_PORT });
console.log(`WebSocket server listening on ws://localhost:${WEBSOCKET_PORT}`);

// Broadcast the latest data to all connected WebSocket clients
function broadcast(data) {
    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(data));
        }
    });
}

// Set up UDP multicast subscription
udpSocket.on('message', (msg, rinfo) => {
    console.log(msg);
    console.log(`Raw message: ${msg.toString('hex')}`);
    try {
        // Decode Avro data
        const decoded = schema.fromBuffer(msg);
        console.log(`Received data: ${JSON.stringify(decoded)} from ${rinfo.address}:${rinfo.port}`);
        // Convert Long `time` field to a readable format
        if (Long.isLong(decoded.time)) {
            decoded.time = new Date(decoded.time.toNumber() / 1e6).toISOString(); // Convert nanoseconds to milliseconds
        }
        console.log(decoded);
        // Broadcast to WebSocket clients
        broadcast(decoded);
    } catch (err) {
        console.error('Failed to decode message:', err);
    }
});

udpSocket.on('listening', () => {
    const address = udpSocket.address();
    console.log(`UDP socket listening on ${address.address}:${address.port}`);
    udpSocket.addMembership(MULTICAST_GROUP); // Join the multicast group
    console.log(`Joined multicast group ${MULTICAST_GROUP}`);
});

// Bind UDP socket
udpSocket.bind(UDP_PORT);
