import asyncio
import sys

from viam.module.module import Module
from viam.components.generic import Generic
from viam.components.sensor import Sensor

from .otis import OtisElevator


async def main(address: str):
    """This function creates and starts a new module, after adding all desired resources.
    Resources must be pre-registered. For an example, see the `__init__.py` file.
    Args:
        address (str): The address to serve the module on
    """
    module = Module(address)
    module.add_model_from_registry(Generic.SUBTYPE, OtisElevator.GENERIC_MODEL)
    module.add_model_from_registry(Sensor.SUBTYPE, OtisElevator.SENSOR_MODEL)
    await module.start()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Need socket path as command line argument")

    asyncio.run(main(sys.argv[1]))
