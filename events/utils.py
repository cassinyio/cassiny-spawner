from typing import Dict

import msgpack


class DockerEvent():
    """Class to handle docker events."""

    _keys = frozenset((
        "action",
        "type",
        "time",
        "name",
        "user_id",
        "exit_code",
    ))
    _attributes = frozenset((
        "com.docker.swarm.service.name",
        "user_id",
        "log_uuid",
        "service_type",
        "exitCode",
    ))

    def __init__(self) -> None:
        self.action = None
        self.type = None
        self.time = None
        self.log_uuid = None
        self.name = None
        self.user_id = None

    def pack(self, *, event: Dict):
        self.action = event['Action']
        self.type = event['Type']
        self.time = event['time'].strftime("%d/%m/%Y %H:%M:%S")

        if "Actor" in event and "Attributes" in event["Actor"]:
            self._pack_attrs(event_attrs=event["Actor"]["Attributes"])
        return self

    def _pack_attrs(self, *, event_attrs: Dict):
        """"""
        for key in self._attributes & event_attrs.keys():
            if key == 'exitCode':
                self.__dict__['exit_code'] = event_attrs[key]
            elif key == 'com.docker.swarm.service.name':
                self.__dict__['name'] = event_attrs[key]
            elif key == 'user_id':
                self.__dict__[key] = int(event_attrs[key])
            elif key == 'log_uuid':
                self.__dict__[key] = event_attrs[key]

    def to_dict(self):
        return {key: self.__dict__[key] for key in self._keys & self.__dict__.keys()}

    def unpack(self, *, message):
        msg_unpacked = msgpack.unpackb(
            message, use_list=False, encoding='utf-8')
        for key in self._keys & msg_unpacked.keys():
            self.__dict__[key] = msg_unpacked[key]
        return self
