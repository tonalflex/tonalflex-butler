import asyncio
import platform
import subprocess
import threading
from bleak import BleakScanner, BleakClient
import rtmidi
from proto import butler_pb2, butler_pb2_grpc

MIDI_CHARACTERISTIC_UUID = "7772e5db-3868-4112-a1a9-f2669d106bf3"


class BleMidiForwarder:

    def __init__(self):
        self.clients = {}  # address: {"client": BleakClient, "name": str}
        self.midi_out = rtmidi.MidiOut()
        self.midi_out.open_virtual_port("BLE MIDI")

    async def scan(self):
        print("🔍 Starting BLE scan...")
        devices = await BleakScanner.discover(timeout=5)
        print(f"Found {len(devices)} devices.")
        for d in devices:
            print(f" - {d.name} ({d.address})")
        return [d for d in devices if d.name]

    async def connect(self, address, name=""):
        if address in self.clients and self.clients[address]["client"].is_connected:
            print(f"🔁 Already connected to {address}")
            return
        client = BleakClient(address)
        await client.connect()
        await client.start_notify(MIDI_CHARACTERISTIC_UUID, self.handle_midi)
        self.clients[address] = {"client": client, "name": name}
        print(f"✅ Connected to {name or address}")

    async def disconnect(self, address):
        info = self.clients.get(address)
        if info and info["client"].is_connected:
            await info["client"].disconnect()
            print(f"🔌 Disconnected from {address}")
            del self.clients[address]
        else:
            print(f"⚠️ No active connection to {address}")

    def list_connected_devices(self):
        return [
            {"address": addr, "name": info["name"]}
            for addr, info in self.clients.items()
        ]

    def get_device_name(self, address: str) -> str:
        info = self.clients.get(address)
        return info["name"] if info and "name" in info else address

    @staticmethod
    def unpair_os_device(name_or_address):
        system = platform.system()
        try:
            if system == "Linux":
                print(f"Running Linux bluetoothctl remove {name_or_address}")
                subprocess.run(["bluetoothctl", "remove", name_or_address], check=True)
            elif system == "Darwin":
                print(f"Running MacOS blueutil --unpair {name_or_address}")
                subprocess.run(["blueutil", "--unpair", name_or_address], check=True)
            else:
                raise RuntimeError(f"Unsupported platform: {system}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Unpair tool not found: {e.filename}") from e
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Unpair command failed: {e}") from e

    async def handle_midi(self, _: int, data: bytearray):
        print("RAW BLE DATA >>", list(data))
        if len(data) >= 4:
            midi = list(data[2:4])
            if midi[0] & 0xF0 == 0xC0:
                self.midi_out.send_message(midi)


class BluetoothService(butler_pb2_grpc.BluetoothServicer):

    def __init__(self):
        self.forwarder = BleMidiForwarder()
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

    def ScanDevices(self, request, context):
        try:
            future = asyncio.run_coroutine_threadsafe(self.forwarder.scan(), self.loop)
            devices = future.result(timeout=10)
            return butler_pb2.BluetoothScanResponse(
                devices=[
                    butler_pb2.BluetoothDevice(name=d.name, address=d.address)
                    for d in devices
                ]
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return butler_pb2.BluetoothScanResponse()

    def ConnectDevice(self, request, context):
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.forwarder.connect(request.address, request.name), self.loop
            )
            future.result(timeout=10)
            return butler_pb2.BluetoothConnectResponse(
                success=True, message="Connected."
            )
        except Exception as e:
            return butler_pb2.BluetoothConnectResponse(success=False, message=str(e))

    def DisconnectDevice(self, request, context):
        try:
            if request.address not in self.forwarder.clients:
                return butler_pb2.BluetoothDisconnectResponse(
                    success=False, message="No such device connected."
                )

            future = asyncio.run_coroutine_threadsafe(
                self.forwarder.disconnect(request.address), self.loop
            )
            future.result(timeout=5)

            # Try unpairing — fallback gracefully
            name_or_address = self.forwarder.get_device_name(request.address)
            try:
                self.forwarder.unpair_os_device(name_or_address)
                return butler_pb2.BluetoothDisconnectResponse(
                    success=True,
                    message=f"Disconnected and unpaired {name_or_address}.",
                )
            except Exception as e:
                return butler_pb2.BluetoothDisconnectResponse(
                    success=True,
                    message=f"Disconnected {name_or_address}, but unpair failed: {e}",
                )

        except Exception as e:
            return butler_pb2.BluetoothDisconnectResponse(success=False, message=str(e))

    def ListConnectedDevices(self, request, context):
        devices = self.forwarder.list_connected_devices()
        return butler_pb2.BluetoothScanResponse(
            devices=[
                butler_pb2.BluetoothDevice(name=dev["name"], address=dev["address"])
                for dev in devices
            ]
        )
