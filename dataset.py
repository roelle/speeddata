"""Data access interface

This module provides a comfortable (fun) interface object for data.

Data is categorized into Signals, Channels, and Sets.

A Signal is a single namable entity such a one or a few columns of
data. A voltage measurement might be a good example of a signal.

A Channel is a collection of Signals with a common abscissa e.g. time.
Voltage and current measurements at the same time interval could be two
signals in a channel.

A Set is a collection of channels related by the range of their
abscissa. There might be a channel with a 1 Hz rate, a 1 kHz rate, and
an asynchronous channel but each start and end around the same absolute
time.

Convenient access is the primary design goal, so signals are elevated
to the Set object and can result in name conflicts. Further, there are
several ways to access a signal.

Each of these shoudl return the same signal:
* `data.channel['one_k'].signal['voltage_a']`
* `data.channel['one_k'].voltage_a`
* `data.one_k.signal['voltage_a']`
* `data.one_k.voltage_a`
* `data.voltage_a`

Further, since the properties exist in the object, tab-completion
should work at each level per the tool used.

"""
import numpy as np
import pandas as pd

class Signal(np.ndarray):
    """Named data belonging to a collection (channel)"""

    def __new__(
        cls,
        value=None,
        name=None,
        channel=None,
    ):
        obj = np.asarray(value).view(cls)
        obj.name = name
        obj.channel = channel

        return obj

    @property
    def t(self): # pylint: disable=C0103
        """Signal time index"""
        return self.channel.time

class Channel():
    """Collection of named signals with a common abscissa"""

    def __init__( # pylint: disable=W0102
        self,
        time=None, # nd.array n x 1
        real_time=None, # nd.array n x 1
        name: str = None,
        signals: dict = {},
    ) -> None:
        self.time = time
        self.real_time = real_time
        self.name = name
        self.signal = {}
        self.add_signals(signals)

    def add_signals( # pylint: disable=W0102
        self,
        signals: dict = {},
    ) -> None:
        """Add signals to a data Channel"""
        for name, signal in signals.items():
            # Assign this channel to the signal
            setattr(signal, 'channel', self)
            setattr(signal, 'name', name)
            # Add the signal to the base channel properties
            self.__dict__[name] = signal
        self.signal.update(signals) # Extend the existing signals

    def __repr__(self):
        r =  f'{self.name}:'
        r += f' {len(self.signal)} signals'
        r += f' with {len(self.time)} rows'
        r += '\n'
        for name, signal in self.signal.items():
            w = 1 if len(signal.shape) < 2 else signal.shape[1]
            r += f'  {name:<32}: {signal.shape[0]}x{w}\n'
        return r

    @staticmethod
    def load_csv(
        file: str,
        channel_name: str = None,
        index_col: int = 0,
    ):
        """Load a columnar csv table into a channel from file."""

        if channel_name is None:
            channel_name = file.replace('.csv', '')

        return Channel.from_df(pd.read_csv(file, index_col=index_col), channel_name)

    @staticmethod
    def from_csv(
        csv: str,
        channel_name: str = 'csv',
        index_col: int = 0,
    ):
        """Load a columnar csv table into a channel."""

        return Channel.from_df(pd.read_table(csv, index_col=index_col), channel_name)

    @staticmethod
    def from_df(
        df: pd.DataFrame,
        channel_name: str = 'df',
    ):
        """Load a pandas dataframe to a channel."""

        # Turn columns into signals
        signals = {}
        for signal_name in df.columns:
            clean_name = signal_name.strip().replace(" ", "_")
            # Add a new item to the dictionary
            signals[clean_name] = Signal(df[signal_name])

        return Channel(time=df.index, name=channel_name, signals=signals)


class Set():
    """Collection of related dataset channels"""

    def __init__( # pylint: disable=W0102
        self,
        channels: dict = {},
    ):
        self.channel = {}
        self.add_channels(channels)

    def add_channels( # pylint: disable=W0102
        self,
        channels: dict = {},
    ) -> None:
        """Add channels to a data Set"""

        self.channel.update(channels) # Extend existing channels
        for name, channel in channels.items():
            # Add the channel to the base set properties
            self.__dict__[name] = channel
            setattr(channel, 'name', name)
            # Add the signals to the base set properties
            for signal_name, signal in channel.signal.items():
                self.__dict__[signal_name] = signal

    def __repr__(self):
        r = '' # pylint: disable=C0103
        for channel in self.channel.values():
            r += repr(channel) # pylint: disable=C0103

        return r

    def add_csv(
        self,
        files: dict = None,
        index_col: int = 0,
    ):
        """Add a columnar csv tables into new channels in a Set."""

        # Allow passing a single file in - name the channel by the file
        if isinstance(files, str):
            files = {files.replace('.csv', ''): files}

        # Allow passing a list of files - name the channels by the files
        if isinstance(files, list):
            files = {file.replace('.csv', ''): file for file in files}

        for n, f in files.items(): # pylint: disable=C0103
            self.add_channels({n: Channel.load_csv(f, n, index_col=index_col)})

    def add_df(
        self,
        df: dict = {},
    ):
        """Add dataframes as new channels in a Set."""

        # Allow passing a single DataFrame in - name the channel df
        if isinstance(df, pd.DataFrame):
            df = {'df': df}

        # Allow passing a list of DataFrames - name the channels by index
        if isinstance(df, list):
            df = {f'df{i}': df for (i, df) in enumerate(df)}

        for n, d in df.items(): # pylint: disable=C0103
            self.add_channels({n: Channel.from_df(d, n)})


def read_csv(*args, **kwargs) -> Set:
    """Add columnar csv tables into a new channels in a new Set."""

    dataset = Set()
    dataset.add_csv(*args, **kwargs)
    return dataset