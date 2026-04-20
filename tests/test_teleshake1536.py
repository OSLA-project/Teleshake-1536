import unittest
from queue import Queue

from sila2_driver.thermoscientific.teleshake1536.api.frame import Frame
from sila2_driver.thermoscientific.teleshake1536.api.teleshake import Teleshake1536


class TeleShake1536_IO:
    def __init__(self) -> None:
        self.output: bytes = []
        self.LoadedData = Queue()

    def flush(self):
        pass

    def read(self, num: int):
        o = self.output[0:num]
        self.output = self.output[num:]
        return o

    def read_all(self):
        o = self.output
        self.output = []
        return o

    def write(self, msg: bytes):
        msg: Frame = Frame.Unflatten(msg)
        data = []
        if not self.LoadedData.empty():
            data = self.LoadedData.get_nowait()
        rpl = Frame.Create(code=msg.Cmd, data=data, ctrl_byte=msg.Ctrl)
        self.output += rpl.Flatten()


class TestTeleshake1536(unittest.TestCase):
    def setUp(self) -> None:
        self.serial = TeleShake1536_IO()

    def test_CloseClamp(self):
        with Teleshake1536(self.serial) as shaker:
            shaker.CloseClamp()

    def test_GetInfo(self):
        with Teleshake1536(self.serial) as shaker:
            shaker.GetInfo()

    def test_GetLastError(self):
        with Teleshake1536(self.serial) as shaker:
            shaker.GetLastError()

    def test_GetPower(self):
        with Teleshake1536(self.serial) as shaker:
            shaker.GetPower()

    def test_GetRPM(self):
        self.serial.LoadedData.put_nowait([0, 0, 1])
        with Teleshake1536(self.serial) as shaker:
            shaker.GetRPM()

    def test_GetSerial(self):
        with Teleshake1536(self.serial) as shaker:
            shaker.GetSerial()

    def test_GetStatus(self):
        with Teleshake1536(self.serial) as shaker:
            shaker.GetStatus()

    def test_OpenClamp(self):
        with Teleshake1536(self.serial) as shaker:
            shaker.OpenClamp()

    def test_SetPower(self):
        self.serial.LoadedData.put_nowait([0x100 // 2, 0, 0])
        with Teleshake1536(self.serial) as shaker:
            shaker.SetPower(0.5)

    def test_SetRPM(self):
        self.serial.LoadedData.put_nowait([23, 28, 1])
        with Teleshake1536(self.serial) as shaker:
            shaker.SetRPM(5000)

    def test_StartDevice(self):
        self.serial.LoadedData.put_nowait([0b000000010, 0, 0])
        with Teleshake1536(self.serial) as shaker:
            shaker.StartDevice()

    def test_StopDevice(self):
        with Teleshake1536(self.serial) as shaker:
            shaker.StopDevice()
