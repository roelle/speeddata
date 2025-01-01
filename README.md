# SpeedData

SpeedData is a lightweight, ephemoral, high-performance system for receiving, batching, and visualizing data streamed over a network. The project leverages UDP multicast for low-latency communication, Avro for efficient serialization, and WebSockets for real-time updates in the browser.

Do you have a complex machine with a distributed control and telemetry system you would like to instrument? SpeedData makes data collection and visualization easy.

This isn't a data lake or warehouse or any of those long-term stable data relationships. This is Speed Dating for data. Data passes by on the screen pretty quickly. Make sure you figure out which data you want to set up a second date with.

#### Features
- Data is collected in real-time from all your sources and chached to disk for as long as your storage supports (based on rate, sources, and disk size)
- The lastest data can be viewed on easily configurable web-pages numerically and graphically
- Data in the cache can be tagged and stored for anlysis (as a file to be moved to more durable storage)
- SpeedData can run on a Raspberry Pi oron Wifi a 16-core Xeon with quad 10Gbit Ethernet ports (collecting 10Mbps or 100Gbps respectively)
![Live web data](screencast.gif)

#### Technical details
- Data is sent efficiently over the wire using UDP and Avro's encoding
- Data is re-served (with decimation) over UDP multicast to visualization systems, also very efficient
  - Zero processing makes this extremely fast and efficient for handling significant amounts of data (as much as the network will support)
- Websockets are used to update data on local web pages for ephemoral visualization
- The real-time data is effectively row-based with a persistant Avro schema
- Batches of data (time-ranges) can be rotated into column-based data for easier analysis of specific signals and stored as HDF5 files
  - The signals may be filtered, decimated, or all converted to HDF5 depending how large of a file you can tolerate

## Concepts
Data is categorized into Signals, Channels, and Sets.

A **Signal** is a single namable entity such a one or a few columns of
data. A voltage measurement might be a good example of a signal. In Avro, each
signal will be a field. In HDF5, each signal is a dataset. Naming is hard.

A **Channel** is a collection of Signals with a common abscissa e.g. time.
Voltage and current measurements at the same time interval could be two
signals in a channel. In the Avro domain, each channel has it's own schema.
In HDF5, each channel is a group

A **Set** is a collection of channels related by the range of their
abscissa. There might be a channel with a 1 Hz rate, a 1 kHz rate, and
an asynchronous channel but each start and end around the same absolute
time. Avro has no analog, as the set is a collection of disparate schema.
HDF5 will have one set per file.

## Architecture
![Architecture diagram](diagram.svg)

### Components
1. **Source**:
   - A source of data - a data channel. `sender.py` is an example with extra 
   debugging capabilities, including saving to file for comparison with the
   relay. Data is send as Avro encoded packets with a consistent schema and
   one packet per time sample.
2. **Relay**:
   - The relay receives data over UDP (different ports) from all the sources.
   It writes in Avro format to disk and relays each packate back out over a
   multicast group. The Avro write involves no translation and can be very
   efficient.
   - `rowdog.py` is a Python, low-performance, first-pass proof-of-concept.
3. **Stripchart Server**
   - Subscribe to the relay multicasts, deserialize all the Avro packets, and
   publish all signals oer websockets.
   - `server.js` is the first attemp.
4. **Stripchart Frontend and HTML**:
   - The receiving end of the websocket that updates values on a webpage as
   configured in the HTML.
   - `frontend.js` and `index.html` are the intial proof-of-concepts.
4. **Pivot** (Row-to-Column Transformer):
   - Transforms row-based Avro data into column-based HDF5 files for storage
   and analysis.
   - `catcol.py` is a proof-of-concept of this process.

## Installation

### Prerequisites
- **Python 3.x**
- **Node.js**

### Clone the Repository
```bash
git clone https://github.com/roelle/speeddata.git
cd speeddata
```

### Install Dependencies
```sh
./install
```
### Removal
Just delete the folder. Everything is local to the project in the proof-of-concept.

## Usage
Start processes
```sh
./start
```

Stop processes
```sh
./stop
```

Convert data (Avro rows to HDF5 columns)
```sh
python -m catcol
```

### View Frontend
Open `index.html` in a browser to view live data updates. `./start` will automatically open this file.

## Roadmap

### v0.1 (current) - January 2025
- Proof-of-concept, not real functionality
- Basic end-to-end functionality
- Example source, relay, pivot, and web visualization

### v0.2 - February 2025
- Create folder system e.g. app/language
- Add a build system
- Add tests
- Add Python load into Roelle DataSet

### v0.3 - March 2025
- Rest API for pivot
- Add configurability
- Configurable decimation for relay
- Add JupyterLab
- Add a load-to-dataset from Avro
- Add stripchart to visualization capability 

### v0.4 - April 2025
- Investigate larger data objects in HDF5 files for better compression (would change storage format).
- Improve performance. Port the relay to a compiled langage. 
- Create a status and control website (registration, channels, signals etc.)
- Add channel registration (via REST)

### v0.5 - May 2025
- Firm interfaces
- Add docuemntation
- Choose a License

### v0.6 - June 2025
- dockerize
- Split apps into repositories (speeddata: relay, stripchart, pivot)
- Build docker container for 

### v0.7 - July 2025
- Start using git issues to track improvements and roadmap
- Optimize a build and tune for a Raspberry Pi and provide instructions for use

### v0.8 - August 2025

### v0.9 - September 2025

### v1.0 - October 2025

### v2.0

## Contributing
Contributions are dubious at the moment while the architecture is in flux.
If you want to participate, reach out to the maintainer, roelle, for a
discussion.

## License
TBD - Subject to change (will be open, not GPL)