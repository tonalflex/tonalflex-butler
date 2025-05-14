# server/services/file.py
import os
from proto import butler_pb2, butler_pb2_grpc
from storage import file_manager

NAM_DIR = "NAM"
IR_DIR = "IR"

def get_path(folder):
    if folder == "/home/mind/NAM":
        return NAM_DIR
    elif folder == "/home/mind/IR":
        return IR_DIR
    else:
        raise ValueError("Invalid folder: must be 'NAM' or 'IR'")

class FileService(butler_pb2_grpc.FileServicer):
    def ListFiles(self, request, context):
        try:
            path = get_path(request.folder)
            files = file_manager.list_files(path)
            return butler_pb2.ListFilesResponse(filenames=files)
        except Exception as e:
            context.set_code(3)  # INVALID_ARGUMENT
            context.set_details(str(e))
            return butler_pb2.ListFilesResponse()

    def UploadFile(self, request, context):
        try:
            path = get_path(request.folder)
            file_manager.save_file(path, request.filename, request.content)
            return butler_pb2.FileOperationResponse(success=True, message="Uploaded")
        except Exception as e:
            return butler_pb2.FileOperationResponse(success=False, message=str(e))

    def DownloadFile(self, request, context):
        try:
            path = get_path(request.folder)
            content = file_manager.read_file(path, request.filename)
            if content is None:
                return butler_pb2.DownloadFileResponse(found=False, content=b"")
            return butler_pb2.DownloadFileResponse(found=True, content=content)
        except Exception as e:
            context.set_code(13)  # INTERNAL
            context.set_details(str(e))
            return butler_pb2.DownloadFileResponse(found=False, content=b"")

    def DeleteFile(self, request, context):
        try:
            path = get_path(request.folder)
            success, message = file_manager.delete_file(path, request.filename)
            return butler_pb2.FileOperationResponse(success=success, message=message)
        except Exception as e:
            return butler_pb2.FileOperationResponse(success=False, message=str(e))

    def RenameFile(self, request, context):
        try:
            path = get_path(request.folder)
            success, message = file_manager.rename_file(path, request.old_name, request.new_name)
            return butler_pb2.FileOperationResponse(success=success, message=message)
        except Exception as e:
            return butler_pb2.FileOperationResponse(success=False, message=str(e))
