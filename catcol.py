import os
import avro.schema
import avro.datafile
import avro.io
import h5py

# Paths to input Avro file and output HDF5 file
hdf5_file = "data/data.h5"
signal_name = "time"

# Open Avro file and extract signal data
signal_data = []

for filename in os.listdir('data'):
    if filename.endswith('.avro'): 
        with open('data/' + filename, "rb") as f:
            print(filename)
            # Open Avro file using DataFileReader
            reader = avro.datafile.DataFileReader(f, avro.io.DatumReader())

            for record in reader:
                if signal_name in record:
                    signal_data.append(record[signal_name])

            reader.close()

# Write the signal to an HDF5 file
with h5py.File(hdf5_file, "w") as hf:
    hf.create_dataset(signal_name, data=signal_data, compression="gzip")

print(f"Signal '{signal_name}' written to {hdf5_file}.")
