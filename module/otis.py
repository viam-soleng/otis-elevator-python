import asyncio
import json
import sys
import time
import requests
from typing import Any, List, ClassVar, Mapping, Optional
from datetime import datetime

import socketio
from viam.components.generic import Generic
from viam.components.sensor import Sensor
from viam.components.component_base import ValueTypes
from viam.proto.app.robot import ComponentConfig, RobotConfig
from viam.proto.common import ResourceName, Geometry
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.logging import getLogger
from viam.utils import SensorReading

from google.protobuf.json_format import ParseDict


class OtisElevator(Generic, Sensor):
    GENERIC_MODEL: ClassVar[Model] = Model(ModelFamily("marriott", "generic"), "otis-elevator")
    SENSOR_MODEL: ClassVar[Model] = Model(ModelFamily("marriott", "sensor"), "otis-elevator")
    LOGGER = getLogger(__name__)

    log_level = False
    passive_sensor = False
    exception_check_timeout = 0.5

    # Config inputs
    client_id = ""
    client_secret = ""
    installation_id = ""
    group_id = ""

    # General connection info
    access_key = ""
    socketId = ""
    socketTimestamp = ""

    url_access_key = "https://sandbox.ems.otis.com/auth/realms/ems/protocol/openid-connect/token"
    url_socketio_conn = "https://sandbox.ems.otis.com?groupIds={}"

    conn = None
    ready = False

    # Otis state variables
    group_state = {}
    numElevators = 0
    car_states = {}
    current_exception = ""


    @classmethod
    # Constructor for otis elevator dispatch integration
    def new(cls, config: ComponentConfig,
            dependencies: Mapping[ResourceName, ResourceBase]):
        elevator = cls(config.name)
        elevator.reconfigure(config, dependencies)

        return elevator

    @classmethod
    # Validates JSON Configuration
    def validate(cls, config: ComponentConfig):

        client_id_input = config.attributes.fields["client_id"].string_value
        if client_id_input == "":
            raise Exception("client_id is needed to continue")

        client_secret_input = config.attributes.fields["client_secret"].string_value
        if client_secret_input == "":
            raise Exception("client_secret is needed to continue")

        installation_id_input = config.attributes.fields["installation_id"].string_value
        if installation_id_input == "":
            raise Exception("installation_id is needed to continue")

        group_id_input = config.attributes.fields["group_id"].string_value
        if group_id_input == "":
            raise Exception("group_id is needed to continue")       
        return

    @classmethod
    # Reconfigure module by resetting various processes as needed
    def reconfigure(self, config: ComponentConfig,
                    dependencies: Mapping[ResourceName, ResourceBase]):
        
        def get_attribute_from_config(attribute_name: str, default, of_type=None):
            if attribute_name not in config.attributes.fields:
                return default

            if default is None:
                if of_type is None:
                    raise Exception(
                        "If default value is None, of_type argument can't be empty"
                    )
                type_default = of_type
            else:
                type_default = type(default)

            if type_default == bool:
                return config.attributes.fields[attribute_name].bool_value
            elif type_default == int:
                return int(config.attributes.fields[attribute_name].number_value)
            elif type_default == float:
                return config.attributes.fields[attribute_name].number_value
            elif type_default == str:
                return config.attributes.fields[attribute_name].string_value
            elif type_default == list:
                return list(config.attributes.fields[attribute_name].list_value)
            elif type_default == dict:
                return dict(config.attributes.fields[attribute_name].struct_value)


        # Log level
        self.log_level = get_attribute_from_config("log_level", False, bool)
        self.passive_sensor = get_attribute_from_config("passive", False, bool)
        self.exception_check_timeout = get_attribute_from_config("exception_timeout", 0.5, float)

        # Get new access token if needed
        client_id_input = config.attributes.fields["client_id"].string_value
        client_id_input =  get_attribute_from_config("client_id", None, str)
        client_secret_input =  get_attribute_from_config("client_secret", None, str)

        if self.client_id != client_id_input or self.client_secret != client_secret_input:
            self.client_id = client_id_input
            self.client_secret = client_secret_input

            resp = self.get_access_key()
            self.access_key = resp.json()["access_token"]   

        # Establish socketio connection if needed
        installation_id_input =  get_attribute_from_config("installation_id", None, str)
        group_id_input =  get_attribute_from_config("group_id", None, str)
        if self.installation_id != installation_id_input or self.group_id != group_id_input:
            self.installation_id = installation_id_input
            self.group_id = group_id_input
            self.ready = False

            if self.conn != None:
                self.conn.disconnect()

            self.establish_socketio_conn()

            task_init = asyncio.create_task(self.initialize_otis_resources())
            while not task_init.done:
                time.sleep(.1)

        return

    @classmethod  
    # Implements the get_readings by returning the current car_states
    async def get_readings(
        self, *, extra: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None, **kwargs
    ) -> Mapping[str, SensorReading]:
        
        return self.car_states

    @classmethod
    # Implements the do_command and processing the given commands
    async def do_command(self, command: Mapping[str, ValueTypes], *,
                         timeout: Optional[float] = None,
                         **kwargs) -> Mapping[str, ValueTypes]:

        if not self.passive_sensor:
            for k,v in command.items():
                if self.log_level:
                    self.LOGGER.info("REQUEST: {} | {}".format(k,v))

                self.current_exception = ""
                await self.conn.emit(k, v)

                err = await self.check_for_exception()
                if err != "":
                    return {"Response": "Error {}".format(err)}
                else:
                    return {"Response": "Success"}
        
        return {"Response": "Warning: This part is not confirmed to accept commands, set 'passive' to false enable behavior."}
    
    @classmethod
    # Implements the get_geometries, currently returns nothing
    async def get_geometries(self) -> List[Geometry]:
        return 

    @classmethod
    # Perform an HTTP POST request to get access token
    def get_access_key(self) -> requests.Response:
        args = {
	        "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        url = self.url_access_key
        return requests.post(url, data = args)  
    
    @classmethod
    # Creates a SocketIO connection and sets up events to monitor, connection will be run in async loop
    def establish_socketio_conn(self):

        # Create socketio client
        conn = socketio.AsyncClient()

        url = self.url_socketio_conn.format(self.group_id)

        headers = {
            "installationId": self.installation_id,
            "Authorization": self.access_key
        }

        # Add events to monitor:
        # Current options: carCall, carMode, carPosition, carStatus, destinationRequest, direction,
        #                  doorStatus, exception, groupStatus, hallCall, loadChange, sessionData
        # More information: https://developers.otis.com/socketio#
        @conn.event
        async def sessionData(data):
            # Response format ex.
            # {
            #   'socketId': 'Eh6t1n1OGp4CwQArADcU', 
            #   'timestamp': '2024-10-03T17:48:56.114Z'
            # }
            print("sessionData: {}".format(data))

            self.socketId = data["socketId"]
            self.socketTimestamp = data["timestamp"]

        @conn.event
        async def groupStatus(data):
            # Response format ex.
            # {
            #   'groupId': 1, 
            #   'available': True, 
            #   'modeName': 'NOR', 
            #   'groupMode': 142, 
            #   'noOfElevators': 2, 
            #   'noOfActiveElevators': 2, 
            #   'hallCallsQueueLength': 2, 
            #   'totalCallsQueueLength': 3, 
            #   'machines': [
            #       {'machineId': '1', 'available': True, 'position': 3, 'mode': 'NOR'}, 
            #       {'machineId': '2', 'available': True, 'position': 10, 'mode': 'NOR'}
            #   ]
            # }

            if self.log_level:
                self.LOGGER.info("groupStatus: {}".format(data))

            self.group_state = data
            self.ready = True

        @conn.event
        async def carMode(data):
            # Response format ex.
            # {
            #   'groupId': 1, 
            #   'machineId': 2, 
            #   'mode': 'NOR'
            # }

            if self.log_level:
                self.LOGGER.info("carMode: {}".format(data))

            machine_id = str(data["machineId"])
            self.car_states[machine_id]["mode"] = data["mode"]

        @conn.event
        async def direction(data):
            # Response format ex.
            # {
            #   'groupId': 1, 
            #   'machineId': 1, 
            #   'direction': 'NONE'
            # }

            if self.log_level:
                self.LOGGER.info("direction: {}".format(data))

            machine_id = str(data["machineId"])
            self.car_states[machine_id]["direction"] = data["direction"]

        @conn.event
        async def carPosition(data):
            # Response format ex.
            # {
            #   'groupId': 1, 
            #   'machineId': 2, 
            #   'position': 6
            # }

            if self.log_level:
                self.LOGGER.info("carPosition: {}".format(data))

            machine_id = str(data["machineId"])
            self.car_states[machine_id]["position"] = data["position"]

        @conn.event
        async def carStatus(data):
            # Response format ex.
            # { 
            #   'machineId': '1', 
            #   'load': {'BOTTOM': 'EMPTY'}, 
            #   'direction': 'NONE', 
            #   'committedDirection': 'UP', 
            #   'position': 13, 
            #   'committedPosition': 13, 
            #   'doorStatus': [{'state': 'CLOSED', 'deck': 'BOTTOM', 'side': 'REAR'}], 
            #   'mode': 'NOR'
            # }
            
            if self.log_level:
                self.LOGGER.info("carStatus: {}".format(data))

            machine_id = str(data["machineId"])
            self.car_states[machine_id] = data

        @conn.event
        async def doorStatus(data):
            # Response format ex.
            # {
            #   'groupId': 1, 
            #   'machineId': 2, 
            #   'state': 'CLOSED', 
            #   'deck': 'BOTTOM', 
            #   'side': 'FRONT'
            # }

            if self.log_level:
                self.LOGGER.info("doorStatus: {}".format(data))

            machine_id = str(data["machineId"])
            for door in self.car_states[machine_id]["doorStatus"]:
                if door["deck"] == data["deck"] and door["side"] == data["side"]:
                    door["state"] = data["state"]


        @conn.event
        async def loadChange(data):
            # Response format ex.
            #  {
            #   "groupId": 1,
            #   "machineId": 2,
            #   "loadLevel": "NORMAL",
            #   "deck": "BOTTOM"
            # }

            if self.log_level:
                self.LOGGER.info("loadChange: {}".format(data))

            machine_id = str(data["machineId"])
            self.car_states[machine_id]["load"][data["deck"]] = data["loadLevel"]

        @conn.event
        async def hallCall(data):
            # Response format ex.
            # {
            #   'hallCallState': 'hallCallAccepted', 
            #   'groupId': 1, 
            #   'machineId': 1, 
            #   'floor': 9, 
            #   'deck': 'BOTTOM', 
            #   'side': 'FRONT', 
            #   'direction': 'UP', 
            #   'hallCallType': 'STD_HALL_CALL_UP', 
            #   'type': 'STANDARD'
            # }

            if self.log_level:
                self.LOGGER.info("hallCall: {}".format(data))

            # -------------------- TBD --------------------

        @conn.event
        async def carCall(data):
            # Response format ex.
            # {
            #   "carCallState": "carCallAccepted",
            #   "deck": "BOTTOM",
            #   "floor": 9,
            #   "groupId": 1,
            #   "machineId": 2,
            #   "side": "FRONT",
            #   "type": "STANDARD"
            # }

            if self.log_level:
                self.LOGGER.info("carCall: {}".format(data))

            # -------------------- TBD --------------------

        @conn.event
        async def destinationRequest(data):
            # Response format ex.
            # {
            #   "destinationRequestState": "destinationRequestAccepted",
            #   "groupId": 1,
            #   "machineId": 2
            # }

            if self.log_level:
                self.LOGGER.info("destinationRequest: {}".format(data))

            # -------------------- TBD --------------------

        @conn.event
        async def exception(data):
            # Response format ex.
            # {
            #   "code": 41000,
            #   "message": "The application cannot complete the operation...",
            #   "timestamp": "2022-10-18T05:39:53+0000",
            #   "socketId": "D2J1GrHUtYyxJM6QAAAA"
            # } 

            if self.log_level:
                self.LOGGER.info("exception: {}".format(data))

            self.current_exception = data["message"]

        # Start socketio client connection
        async def connect_async():
            await conn.connect(url, headers, socketio_path="/api/oid/v1")
            await conn.wait()

        loop = asyncio.get_event_loop()
        loop.create_task(connect_async())

        self.conn = conn

    @classmethod
    async def check_for_exception(self) -> str:
        now = datetime.now()
        while (datetime.now() - now).microseconds < int(self.exception_check_timeout*1000) and self.current_exception == "":
            await asyncio.sleep(0.1)

        return self.current_exception
    
    @classmethod
    # Initializes resources (currently car states) after the SocketIO connection has been made
    async def initialize_otis_resources(self):
        while not self.ready:
            await asyncio.sleep(.1)

        for i in range(self.group_state["noOfElevators"]):
            data = {
                "groupId": 1,
                "machineId": i+1
            }
            await self.conn.emit("sendCarStatus",data)


async def main():
    elevator = OtisElevator("test")

    with open("otis_login.json", 'r') as file:
        config_data = json.load(file)

    config_data["log_level"] = True

    cfg = ComponentConfig(attributes=config_data)

    elevator.reconfigure(cfg, {})

    await asyncio.sleep(2)

    print("-------------------------------")

    cmd = "sendHallCall"

    data =  {
                "groupId": 1,
                "floor": 9,
                "side": "FRONT", 
                "direction": "UP", 
                "deck":"LOWER", 
                "type": "STANDARD"   
            }
    
    await elevator.do_command({cmd: data})
    
    await asyncio.sleep(300)

    sys.exit()

if __name__ == '__main__':
    asyncio.run(main())
