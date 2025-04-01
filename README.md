# TonalFlex Butler
A gRPC server which handles side function for elk-os and sushi, like file transfer and specific os setups. 

Current functions:
- List all json files
- Receive json as string and save as file
- Load and transfer json file as string
- Delete json file


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