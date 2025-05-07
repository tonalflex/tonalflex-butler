import subprocess
import re
from proto import butler_pb2, butler_pb2_grpc


class MidiService(butler_pb2_grpc.MidiServicer):
    def ListDevices(self, request, context):
        try:
            result = subprocess.check_output(["aconnect", "-l"], text=True)
            devices = []
            current_client = None
            for line in result.splitlines():
                if match := re.match(r"client (\\d+): '(.*?)'.*", line):
                    current_client = int(match.group(1))
                elif (
                    match := re.match(r"\\s+(\\d+) '(.*?)'", line)
                ) and current_client is not None:
                    port_id = int(match.group(1))
                    name = match.group(2)
                    devices.append(
                        butler_pb2.MidiDevice(
                            client_id=current_client, port_id=port_id, name=name
                        )
                    )
            return butler_pb2.MidiDevicesResponse(devices=devices)
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return butler_pb2.MidiDevicesResponse()

    def ConnectDevice(self, request, context):
        try:
            controller = f"{request.controller_client}:{request.controller_port}"
            sushi = f"{request.sushi_client}:{request.sushi_port}"
            subprocess.run(["aconnect", controller, sushi], check=True)
            return butler_pb2.MidiConnectResponse(
                success=True, message="Connected successfully"
            )
        except subprocess.CalledProcessError as e:
            return butler_pb2.MidiConnectResponse(success=False, message=str(e))


# import asyncio
# import subprocess
# import threading
# import grpc
# import re
# import rtmidi
# from bleak import BleakScanner, BleakClient
# from proto import butler_pb2, butler_pb2_grpc

# MIDI_SERVICE_UUID = "03b80e5a-ede8-4b33-a751-6ce34ec4c700"
# MIDI_CHARACTERISTIC_UUID = "7772e5db-3868-4112-a1a9-f2669d106bf3"


# # --- BLE MIDI Forwarder ---
# class BleMidiForwarder:
#     def __init__(self):
#         self.client = None
#         self.midi_out = rtmidi.MidiOut()
#         self.midi_out.open_virtual_port("BLE MIDI")

#     async def scan(self):
#         print("🔍 Starting BLE scan...")
#         devices = await BleakScanner.discover(timeout=5)
#         print(f"🔍 Found {len(devices)} devices:")
#         for d in devices:
#             print(f"  - {d.name} ({d.address})")

#         # Return all devices that have a name (ignore unnamed ones)
#         return [d for d in devices if d.name]

#     async def connect(self, address):
#         self.client = BleakClient(address)
#         await self.client.connect()
#         await self.client.start_notify(MIDI_CHARACTERISTIC_UUID, self.handle_midi)

#     async def handle_midi(self, _: int, data: bytearray):
#         print("RAW BLE DATA >>", list(data))
#         if len(data) >= 4:
#             midi = list(data[2:4])
#             if midi[0] & 0xF0 == 0xC0:
#                 self.midi_out.send_message(midi)


# # --- gRPC Service ---
# class MidiService(butler_pb2_grpc.MidiServicer):

#     def __init__(self):
#         self.forwarder = BleMidiForwarder()
#         self.loop = asyncio.new_event_loop()
#         threading.Thread(target=self.loop.run_forever, daemon=True).start()

#     def ScanBleDevices(self, request, context):
#         try:
#             future = asyncio.run_coroutine_threadsafe(self.forwarder.scan(), self.loop)
#             devices = future.result(timeout=10)
#             return butler_pb2.BleScanResponse(
#                 devices=[
#                     butler_pb2.BleDevice(name=d.name, address=d.address)
#                     for d in devices
#                 ]
#             )
#         except Exception as e:
#             context.set_details(str(e))
#             context.set_code(grpc.StatusCode.INTERNAL)
#             return butler_pb2.BleScanResponse()

#     def ConnectBleDevice(self, request, context):
#         try:
#             self.loop.run_until_complete(self.forwarder.connect(request.address))
#             return butler_pb2.BleConnectResponse(success=True, message="Connected.")
#         except Exception as e:
#             return butler_pb2.BleConnectResponse(success=False, message=str(e))

#     def DisconnectBleDevice(self, request, context):
#         try:
#             if self.forwarder.client:
#                 self.loop.run_until_complete(self.forwarder.client.disconnect())
#                 return butler_pb2.BleDisconnectResponse(
#                     success=True, message="Disconnected."
#                 )
#             else:
#                 return butler_pb2.BleDisconnectResponse(
#                     success=False, message="No device connected."
#                 )
#         except Exception as e:
#             return butler_pb2.BleDisconnectResponse(success=False, message=str(e))
