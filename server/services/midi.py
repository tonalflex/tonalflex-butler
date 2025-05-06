import asyncio
import subprocess
import grpc
import re
import rtmidi
from bleak import BleakScanner, BleakClient
from proto import butler_pb2, butler_pb2_grpc

MIDI_SERVICE_UUID = "03b80e5a-ede8-4b33-a751-6ce34ec4c700"
MIDI_CHARACTERISTIC_UUID = "7772e5db-3868-4112-a1a9-f2669d106bf3"


# --- BLE MIDI Forwarder ---
class BleMidiForwarder:
    def __init__(self):
        self.midi_out = rtmidi.MidiOut()
        self.midi_out.open_virtual_port("FootCtrl BLE MIDI")
        self.device_name = "FootCtrl"
        self.ble_client = None

    async def handle_midi(self, _: int, data: bytearray):
        print("RAW BLE DATA >>", list(data))
        if len(data) >= 4:
            midi = list(data[2:4])
            if midi[0] & 0xF0 == 0xC0:
                print("BLE MIDI >>", midi)
                self.midi_out.send_message(midi)

    async def run(self):
        print("🔍 Scanning for BLE MIDI devices...")
        devices = await BleakScanner.discover(timeout=5)
        target = next(
            (d for d in devices if d.name and self.device_name in d.name), None
        )

        if not target:
            print("❌ FootCtrl not found.")
            return

        print(f"✅ Found: {target.name} ({target.address})")

        self.ble_client = BleakClient(target.address)
        await self.ble_client.connect()
        await self.ble_client.start_notify(MIDI_CHARACTERISTIC_UUID, self.handle_midi)

        print("🎵 Subscribed. Listening for BLE MIDI...")
        while True:
            await asyncio.sleep(1)


# --- gRPC Service ---
class MidiService(butler_pb2_grpc.MidiServicer):
    def ListDevices(self, request, context):
        try:
            result = subprocess.check_output(["aconnect", "-l"], text=True)
            devices = []

            current_client = None
            for line in result.splitlines():
                if match := re.match(r"client (\d+): '(.*?)'.*", line):
                    current_client = int(match.group(1))
                elif (
                    match := re.match(r"\s+(\d+) '(.*?)'", line)
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
