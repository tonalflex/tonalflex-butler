from concurrent import futures
import grpc
from proto import butler_pb2_grpc  # Import from 'proto' directory
from server.session_service import SessionServiceServicer

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    butler_pb2_grpc.add_SessionServiceServicer_to_server(SessionServiceServicer(), server)
    server.add_insecure_port('[::]:52052')
    print("Butler gRPC server running on port 52052...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()