import sys
import os
from grpc_tools import protoc

def generate_proto_stubs():
    # Use 'proto' to match your directory structure
    proto_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../proto"))
    output_path = proto_path
    proto_file = os.path.join(proto_path, "butler.proto")

    # Debug: Print paths to verify
    print(f"Proto path: {proto_path}")
    print(f"Proto file: {proto_file}")

    # Check if proto file exists
    if not os.path.exists(proto_file):
        raise FileNotFoundError(f"Proto file not found at: {proto_file}")

    result = protoc.main((
        '',  # Empty first arg for protoc
        f'-I{proto_path}',  # Include path for proto files
        f'--python_out={output_path}',  # Output for Python stubs
        f'--grpc_python_out={output_path}',  # Output for gRPC stubs
        proto_file,
    ))

    if result != 0:
        raise RuntimeError(f"protoc failed with exit code {result}")
    else:
        print("[gRPC] Proto stubs compiled successfully.")

    # Modify the generated butler_pb2.py file to use 'proto' import
    grpc_stub_path = os.path.join(proto_path, "butler_pb2_grpc.py")
    with open(grpc_stub_path, "r+") as f:
        content = f.read()
        content = content.replace("import butler_pb2 as", "from proto import butler_pb2 as")
        f.seek(0)
        f.write(content)
        f.truncate()

if __name__ == "__main__":
    generate_proto_stubs()