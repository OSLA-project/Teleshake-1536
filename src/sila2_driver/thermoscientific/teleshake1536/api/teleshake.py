from __future__ import annotations

from time import sleep
from typing import Union

from serial import Serial

from .frame import ControlByte, Frame, FrameError, StatusByte
from .rpm_converter import Convert


class InternalError(Exception):
    pass


class ParameterError(Exception):
    pass


class Teleshake:
    @property
    def Settings(self):
        return self._settings

    @Settings.setter
    def Settings(self, value):
        self._settings = value

    def __init__(
        self,
        port: Union[str, Serial],
        baudrate: int = 9600,
        timeout: float = 1.0,
        parity: str = "N",
        stopbits: int = 1,
    ):
        """Create an object for communication with a Teleshake 1536 over serial port

        Args:
            port (str, Serial): Port to use (e.g. 'COM1' or an already open Serial-like object)
            baudrate (int, optional): Communication baudrate. Defaults to 9600.
            timeout (float, optional): How long to wait for a reply (seconds). Defaults to 1.0.
            parity (str, optional): Message parity. Defaults to "N".
            stopbits (int, optional): Stop bit. Defaults to 1.
        """
        self.Settings = {
            "port": port,
            "baudrate": baudrate,
            "timeout": timeout,
            "parity": parity,
            "stopbits": stopbits,
        }

    def __enter__(self):
        self.Open()
        return self

    def __exit__(self, *args):
        self.Close()

    def Close(self):
        port = self.Settings["port"]
        if isinstance(port, str):
            self._ser.close()

    def Open(self):
        port = self.Settings["port"]
        if isinstance(port, str):
            try:
                self._ser = Serial(**self.Settings)
            except Exception as ex:
                raise IOError from ex
        else:
            self._ser = port

    def GetLastError(self) -> str:
        raise NotImplementedError("This function should be overridden in sub-classes")

    def SendFrame(self, msg: Frame, addr: int = 0):
        msg = Frame.Create(
            msg.Cmd, [msg.Data0, msg.Data1, msg.Data2], ctrl_byte=ControlByte(addr=addr)
        )
        self._ser.read_all()
        self._ser.write(msg.Flatten())
        self._ser.flush()
        repl = Frame.Unflatten(self._ser.read(6))
        self.ValidateReply(repl, msg)
        return repl

    def ValidateReply(self, repl: Frame, msg: Frame):
        if repl.Cmd != msg.Cmd:
            raise FrameError(
                f"Command code mismatch error: 0x{repl.Cmd:02x} != 0x{msg.Cmd:02x}"
            )

        if repl.Ctrl.addr != msg.Ctrl.addr:
            raise FrameError(
                f"Address mismatch error: 0b{repl.Ctrl.addr:04b} != 0b{msg.Ctrl.addr:04b}"
            )

        if repl.Ctrl.error:
            raise InternalError(self.GetLastError())


class Teleshake1536(Teleshake):
    def CloseClamp(self, addr: int = 0):
        msg = Frame.Create(0x58)
        repl = self.SendFrame(msg, addr=addr)
        status = StatusByte.Unflatten(repl.Data0)
        if status.err:
            raise InternalError(self.GetLastError())
        sleep(2.0)  # Wait for clamps to close

    def GetInfo(self, addr: int = 0):
        msg = Frame.Create(0x23, [00, 00, 00])
        return self.SendFrame(msg, addr=addr)

    def GetLastError(self) -> str:
        lookup = {
            0: "ERR_NO_ERROR_RECORDED",
            1: "ERR_BUFFER_OVERFLOW",
            2: "ERR_NO_STOP_BIT",
            3: "ERR_UNKNOWN_COMMAND",
            4: "ERR_CRC",
            5: "ERR_DEV_ADDR_MISMATCH",
            6: "ERR_TIMEOUT",
            7: "ERR_NOT_INITIALIZED",
            8: "ERR_NOT_IN_REMOTE_MODE",
            9: "ERR_DEVICE_ALREADY_ON",
            10: "ERR_DEVICE_ALREADY_OFF",
            11: "ERR_N1_OVERFLOW",
            12: "ERR_N2_OVERFLOW",
            13: "ERR_N3_OVERFLOW",
            14: "ERR_CMD_NOT_ALLOWED",
        }

        msg = Frame.Create(0x25)
        repl = self.SendFrame(msg)
        err_no = repl.Data0
        return lookup[err_no]

    def GetPower(self, addr: int = 0):
        msg = Frame.Create(0x3F)
        repl = self.SendFrame(msg, addr=addr)
        return repl.Data0 / 0x100  # Power in arb units (0.0-1.0)

    def GetRPM(self, addr: int = 0) -> int:
        msg = Frame.Create(0x32)
        repl = self.SendFrame(msg, addr=addr)
        raw_cycle_time = repl.Data0 + repl.Data1 * 0x100 + repl.Data2 * 0x10000
        return Convert.ToRPM(raw_cycle_time)

    def GetSerial(self, addr: int = 0):
        frame = self.GetInfo(addr=addr)
        return f"{frame.Data1:02}.{frame.Data0:02}"

    def GetStatus(self, addr: int = 0):
        return StatusByte.Unflatten(self.GetInfo(addr=addr).Data2)

    def OpenClamp(self, addr: int = 0):
        msg = Frame.Create(0x57)
        repl = self.SendFrame(msg, addr=addr)
        status = StatusByte.Unflatten(repl.Data0)
        if status.err:
            raise InternalError(self.GetLastError())
        sleep(3.0)  # Wait for clamps to open

    def ResetDevice(self):
        raise NotImplementedError

    def SetPower(self, power: float, addr: int = 0):
        if power > 1 or power < 0:
            raise ParameterError("Output out of range error")

        power_rescale = int(power * 0x100)
        if power_rescale > 0xFF:
            power_rescale = 0xFF
        if power_rescale < 0:
            power_rescale = 0

        msg = Frame.Create(0x3E, [power_rescale])
        repl = self.SendFrame(msg, addr=addr)
        if repl.Data0 != power_rescale:
            raise IOError(f"Failed to set power to {power}")

    def SetRPM(self, rpm: int, addr: int = 0):
        if rpm < 4006 or rpm > 8484:
            raise ParameterError("RPM out of range error")

        rpm_rescale = Convert.ToCycleTimePC(rpm)
        msg = Frame.Create(
            0x33,
            [
                rpm_rescale & 0xFF,
                (rpm_rescale & 0xFF00) // 0x100,
                (rpm_rescale & 0xFF0000) // 0x10000,
            ],
        )
        repl = self.SendFrame(msg, addr=addr)
        if repl.Data0 + repl.Data1 * 0x100 + repl.Data2 * 0x10000 != rpm_rescale:
            raise IOError(f"Failed to set RPM to {rpm}")

    def StartDevice(self, addr: int = 0):
        msg = Frame.Create(0x30)
        repl = self.SendFrame(msg, addr=addr)
        status = StatusByte.Unflatten(repl.Data0)
        if status.err:
            raise InternalError(self.GetLastError())
        if not status.on:
            raise IOError(f"Status error : 0b{status:08b} (Not started)")

    def StopDevice(self, addr: int = 0):
        msg = Frame.Create(0x31)
        repl = self.SendFrame(msg, addr=addr)
        status = StatusByte.Unflatten(repl.Data0)
        if status.err:
            raise InternalError(self.GetLastError())
        if status.on:
            raise IOError(f"Status error : 0b{status:08b} (Not stopped)")
