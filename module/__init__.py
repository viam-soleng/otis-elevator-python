from viam.components.generic import Generic
from viam.components.sensor import Sensor
from viam.resource.registry import Registry, ResourceCreatorRegistration
from .otis import OtisElevator


Registry.register_resource_creator(Generic.SUBTYPE,
                                   OtisElevator.GENERIC_MODEL,
                                   ResourceCreatorRegistration(OtisElevator.new))

Registry.register_resource_creator(Sensor.SUBTYPE,
                                   OtisElevator.SENSOR_MODEL,
                                   ResourceCreatorRegistration(OtisElevator.new))
