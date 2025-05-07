from concurrent import futures
import grpc
from grpc_reflection.v1alpha import reflection
from proto import butler_pb2_grpc, butler_pb2  # Import from 'proto' directory

from server.services.session import SessionService
from server.services.file import FileService
from server.services.bluetooth import BluetoothService
from server.services.midi import MidiService


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add services to the server
    butler_pb2_grpc.add_SessionServicer_to_server(SessionService(), server)
    butler_pb2_grpc.add_FileServicer_to_server(FileService(), server)
    butler_pb2_grpc.add_BluetoothServicer_to_server(BluetoothService(), server)
    butler_pb2_grpc.add_MidiServicer_to_server(MidiService(), server)

    # Enable reflection
    SERVICE_NAMES = (
        butler_pb2.DESCRIPTOR.services_by_name["Session"].full_name,
        butler_pb2.DESCRIPTOR.services_by_name["Bluetooth"].full_name,
        butler_pb2.DESCRIPTOR.services_by_name["Midi"].full_name,
        butler_pb2.DESCRIPTOR.services_by_name["File"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port("[::]:52052")
    print("Butler gRPC server running on port 52052...")

    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
