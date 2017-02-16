# buffer.py
Simply curses program that provides write buffer information, oriented for use during large transfers.

## Preview
Roughly 4 seconds into this video, I begin a large transfer.

[![ScreenShot](https://i.imgur.com/0tDYaIJ.png)](https://drewnutter.com/bufferpy.ogv)

## Installation (crude)
```
# wget -qO- https://drewnutter.com/buf.sh | sh
```

## Usage
```
buffer.py
```

## Known issues
* Counter of transfered data relies on change in buffer which seems to miss something like 20% of the actual transfer.
