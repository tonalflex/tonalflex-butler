# server/session_service.py
from concurrent import futures
import grpc
import os
import json
from proto import butler_pb2, butler_pb2_grpc
from storage.file_manager import save_session, load_session, list_sessions, delete_session, rename_session

SESSION_DIR = "sessions"


class SessionService(butler_pb2_grpc.SessionServicer):
    def SaveSession(self, request, context):
        try:
            save_session(SESSION_DIR, request.name, request.json_data)
            return butler_pb2.SaveSessionResponse(
                success=True, message="Saved successfully"
            )
        except Exception as e:
            return butler_pb2.SaveSessionResponse(success=False, message=str(e))

    def LoadSession(self, request, context):
        data = load_session(SESSION_DIR, request.name)
        if data:
            return butler_pb2.LoadSessionResponse(json_data=data, found=True)
        else:
            return butler_pb2.LoadSessionResponse(json_data="", found=False)

    def ListSessions(self, request, context):
        names = list_sessions(SESSION_DIR)
        return butler_pb2.ListSessionsResponse(session_names=names)

    def DeleteSession(self, request, context):
        success, message = delete_session(SESSION_DIR, request.name)
        return butler_pb2.DeleteSessionResponse(success=success, message=message)
    
    def RenameSession(self, request, context):
        success, message = rename_session(SESSION_DIR, request.old_name, request.new_name)
        return butler_pb2.RenameSessionResponse(success=success, message=message)
