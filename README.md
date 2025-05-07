# TonalFlex Butler

A gRPC server which handles side function for elk-os and sushi, like file transfer and specific os setups.

Current functions:

- Load/Save/Delete/Rename Sessions
- Load/Save/Delete/Rename NAM, IR, etc
- Wifi setup
- Midi setup

## Run Butler (linux)

```bash
# optional
python3 -m venv venv
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
python3 -m server.main
```

## Run Butler (MacOS)

In order to run rtmidi on MacOS, you need to run Python <= v3.11.

```bash
brew install python@3.11
python3.11 -m venv venv311
source venv311/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
python3 -m server.main
```
