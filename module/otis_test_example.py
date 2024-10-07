import asyncio
from datetime import datetime
from typing import Mapping
from viam.robot.client import RobotClient
from viam.components.sensor import Sensor
from viam.utils import SensorReading

async def connect():
    opts = RobotClient.Options.with_api_key( 
        api_key = "<API_KEY>",
        api_key_id = "API_KEY_ID"
    )
    return await RobotClient.at_address('otis-main.covge5vgpo.viam.cloud', opts)


async def test_car_call(otis_elevator : Sensor, state : Mapping[str, SensorReading]):
    
    desired_floor = 9
    timeout = 30

    for i, s in state.items():
        test_command = {"sendCarCall": 
                        {
                            "groupId": 1,
                            "machineId": int(i), 
                            "floor": desired_floor,
                            "side": s["doorStatus"][0]["side"], 
                            "deck": s["doorStatus"][0]["deck"], 
                            "type": "STANDARD"   
                        }
                    }

        # Send command
        response = await otis_elevator.do_command(command=test_command)
        if response["Success"] != True:
            raise Exception("failed to get response from car call test's command request")
        
        # Confirm success
        found = False
        start = datetime.now()
        while (datetime.now() - start).seconds < timeout:
            return_state = await otis_elevator.get_readings()
            if return_state[str(i)]["position"] == desired_floor:
                found = True
                break

            await asyncio.sleep(1)

        if not found:
            raise Exception("failed to achieve desired_floor ({}) before timeout ({})".format(desired_floor, timeout))
        
    return

async def main():
    machine = await connect()
    
    otis_elevator = Sensor.from_robot(machine, "otis-elevator")
    car_statuses = await otis_elevator.get_readings()

    # Test Example
    await test_car_call(otis_elevator, car_statuses)


if __name__ == '__main__':
    asyncio.run(main())