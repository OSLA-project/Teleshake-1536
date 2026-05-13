from __future__ import annotations

from dataclasses import dataclass, field


class FrameError(Exception):
    pass


@dataclass
class Frame:
    Ctrl: ControlByte = field(default_factory=lambda: ControlByte())
    Cmd: int = 0
    Data2: int = 0
    Data1: int = 0
    Data0: int = 0
    Crc: int = 0

    @staticmethod
    def Create(code: int, data: list[int] = [], ctrl_byte: ControlByte = None) -> Frame:
        if data:
            data.extend([0, 0])
        else:
            data = [0, 0, 0]

        if ctrl_byte is None:
            ctrl_byte = ControlByte()

        return Frame(
            Ctrl=ctrl_byte,
            Cmd=code % 0x100,
            Data2=data[2] % 0x100,
            Data1=data[1] % 0x100,
            Data0=data[0] % 0x100,
            Crc=sum([ctrl_byte.Flatten(), code, data[2], data[1], data[0]]) % 0x100,
        )

    def Flatten(self):
        d = [0] * 6
        d[0] = self.Ctrl.Flatten()
        d[1] = self.Cmd
        d[2] = self.Data2
        d[3] = self.Data1
        d[4] = self.Data0
        d[5] = self.Crc
        return bytes(d)

    @staticmethod
    def Unflatten(buffer: bytes) -> Frame:
        Frame.Validate(buffer)
        return Frame(
            Ctrl=ControlByte.Unflatten(buffer[0]),
            Cmd=buffer[1],
            Data2=buffer[2],
            Data1=buffer[3],
            Data0=buffer[4],
            Crc=buffer[5],
        )

    @staticmethod
    def Validate(buffer: bytes):
        if len(buffer) == 0:
            raise TimeoutError

        if len(buffer) != 6:
            raise FrameError("Buffer length error")

        if sum(buffer[0:5]) % 0x100 != buffer[5]:
            raise FrameError("Checksum error")


@dataclass
class ControlByte:
    addr: int = 0b0000
    error: bool = False
    dirty: bool = True
    mode: bool = True
    len: bool = False

    def Flatten(self):
        d = self.addr
        d += 0b00010000 * self.error
        d += 0b00100000 * self.dirty
        d += 0b01000000 * self.mode
        d += 0b10000000 * self.len
        return d

    @staticmethod
    def Unflatten(data: int) -> ControlByte:
        ControlByte.Validate(data)
        return ControlByte(
            addr=data & 0b00001111,
            error=(data & 0b00010000) != 0,
            dirty=(data & 0b00100000) != 0,
            mode=(data & 0b01000000) != 0,
            len=(data & 0b10000000) != 0,
        )

    @staticmethod
    def Validate(data: int):
        if data & 0b10000000 != 0:  # Message length
            # Manual is not clear how to handle non-zero values
            raise NotImplementedError("Don't know how to deal with this")


@dataclass
class StatusByte:
    accel: bool  # Device is in acceleration/deceleration phase.
    on: bool  # Drive runs (RS232-controlled).
    err: bool  # An error has occurred.
    poti_off: bool  # The potentiometer is in the OFF position.
    debug: bool  # Debug mode on.
    address_set: bool  # Device address allocated.
    prog: bool  # Transmitted values are stored in the internal EEPROM; upon the next device start, the values set per PC and stored in the EEPROM apply.
    clamp_closed: bool  # Clamps for the microtiter plate closed. Is always erased or set upon execution of the command openClamp or closeClamp gelöscht (*always 1 unless the device is equipped with a clamp motor).

    @staticmethod
    def Unflatten(data: int) -> StatusByte:
        return StatusByte(
            accel=(data & 0b00000001) != 0,
            on=(data & 0b00000010) != 0,
            err=(data & 0b00000100) != 0,
            poti_off=(data & 0b00001000) != 0,
            debug=(data & 0b00010000) != 0,
            address_set=(data & 0b00100000) != 0,
            prog=(data & 0b01000000) != 0,
            clamp_closed=(data & 0b10000000) != 0,
        )
