# Interfacing with the Otis Elevator

## Send Requests

### 1. Send Car Call Event (sendCarCall)

This is the event to send when you want to send a machine to a specific floor. It is the programmatic equivalent of pressing the button of a floor once you have entered an elevator. Once this event is sent to the API, the API will respond back with a carCall event that will notify you of the state of your car call. If a sendCarCall event is sent and the API responds back with a carCall event where the carCallState is carCallAccepted, then the API will broadcast to you the following events for the particular machine for which the sendCarCall event was sent:

 - carCall
 - carPosition
 - direction
 - doorStatus
 - loadChange

Once the API has responded with a carCall event where the carCallState is carCallServed, and the door has done a full door cycle (you will receive doorStatus events where the state is OPENING , OPENED, CLOSING, and CLOSED, in that order), the above events will stop being sent to you for that particular machine (unless you have another sendCarCall, sendHallCall, or sendDestinationRequest in progress for the same machine).

#### Payload

| Name | Type | Inclusion | Description | 
| ---- | ---- | --------- | ----------- | 
| `deck` | string("TOP", "BOTTOM") | **Required** | The deck on which the car call is being placed for (if this sendCarCall is being executed after a sendHallCall , the hallCall event in response will indicate which deck is assigned). |
| `floor` | int | **Required** | The index of the destination floor that the car should be sent to (note, floor positions are zero-based indexed).  |
| `groupId` | int | **Required** | The id of the elevator group that the machine is in.  |
| `machineId` | int | **Required** | The id of the machine for which the car call is being placed.  |
| `side` | string("FRONT", "REAR") | **Required** | Indicates whether the front door of the elevator or the rear door of the elevator should open once the destination floor is reached.  |
| `type` | string("STANDARD", "WHEELCHAIR", "EXTENDED") | **Required** | Indicates the type of car call that is being placed. Valid values are: STANDARD - corresponds to a standard car call. WHEELCHAIR - corresponds to a wheelchair car call. EXTENDED - corresponds to a extended car call. |
| `dwellTime` | string(float) | Optional | The number of seconds that the door should stay opened when reaching the destination floor. This number must a value between 0.5 and 25.5 and must be in 0.5 increments (i.e., "10.5" or "9.0"). This feature is only available for select elevator groups.  |

For additional guidance, please contact OID support at support-oid@otis.com

#### Example

```json
{
    "groupId": 1,
    "deck": "BOTTOM",
    "side": "FRONT",
    "floor": 15,
    "machineId": 2,
    "type": "STANDARD"
}
```


### 2. Send Car Command Event (sendCarCommand)

This is the event to send when you want to change the mode of a specific car within the group. Currently we support the following mode to be changed:

- DHB - Door hold operation
- ATT - Robotic mode exhibiting attendant like behavior

Both **DHB** and **ATT** modes are similar and allow for additional control of doors to better facilitate robot's entry and exit process. It is important that these modes are turned OFF immediately after robot enters or exists the elevator to avoid inconvenience to other passengers. These modes may require elevator parameter tuning to make them optimal for robotic operations.Elevators response to these modes may show some variance depending on elevator type and region. For guidance on optimal usage, please contact OID support at support-oid@otis.com

#### Payload

| Name | Type | Inclusion | Description | 
| ---- | ---- | --------- | ----------- | 
| `deck` | string("TOP", "BOTTOM") | **Required** | The deck for which this mode change will be affected. |
| `groupId` | int | **Required** | The id of the elevator group that the machine is in.  |
| `machineId` | int | **Required** | The id of the machine for which the mode is being changed.  |
| `mode` | string("DHB", "ATT") | **Required** | The name of this mode in which to put the car.  |
| `side` | string("FRONT", "REAR") | **Required** | The side of the elevator for which this mode change will affect.  |
| `state` | bool | **Required** | A boolean value indicating whether or not the particular mode should be enabled (true) or disabled (false).  |

#### Example

```json
{
    "deck": "TOP",
    "groupId": 1,
    "machineId": 2,
    "mode": "DHB",
    "side": "FRONT",
    "state": true
}
```


### 3. Send Car Status Event (sendCarStatus)

This is the event to send when you want to receive a snapshot of the current state of a machine. Once this event is sent to the API, the API will respond back with a carStatus event which will tell you the current state of that car.

#### Payload

| Name | Type | Inclusion | Description | 
| ---- | ---- | --------- | ----------- | 
| `groupId` | int | **Required** | The id of the elevator group that the machine is in.  |
| `machineId` | int | **Required** | The id of the machine for which the current status is being requested  |

#### Example

```json
{
    "groupId": 1,
    "machineId": 2,
}
```


### 4. Send Destination Request Event (sendDestinationRequest)

This is the event to send when you want to call a machine to a floor and supply it with the desired destination (called destination dispatch). Once this event is sent to the API, the API will respond back with a destinationRequest event that will notify you of the assigned car. The API will broadcast to you the following events for the particular machine for which the sendDestinationRequest event was sent:


- carCall
- carPosition
- direction
- doorStatus
- loadChange

Once a full door cycle has occurred (you will receive doorStatus events where the state is OPENING,OPENED, CLOSING, and CLOSED, in that order), the above events will stop being sent to you for that particular machine (unless you have another sendCarCall, sendHallCall , or sendDestinationRequest in progress for the same machine).

#### Payload

| Name | Type | Inclusion | Description | 
| ---- | ---- | --------- | ----------- | 
| `destFloor` | int | **Required** | The index of the destination floor that the car should be sent to (note, floor positions are zero-based indexed). |
| `destSide` | string("FRONT", "REAR") | **Required** | Indicates whether the front door of the elevator or the rear door of the elevator should open once the destination floor is reached. Valid values are: FRONT - corresponds to the FRONT door. REAR - corresponds to the REAR door.  |
| `srcFloor` | int | **Required** | The index of the floor from which the call is originating (note, floor positions are zero-based indexed). |
| `srcSide` | string("FRONT", "REAR") | **Required** | Indicates whether the front door of the elevator or the rear door of the elevator should open once machine reaches the floor from which the call originated. Valid values are: FRONT - corresponds to the FRONT door. REAR - corresponds to the REAR door.  |
| `groupId` | int | **Required** | The id of the elevator group that the machine is in.  |
| `type` | string | **Required** | Indicates the type of car call that is being placed. Valid values are: STANDARD - corresponds to a standard car call. WHEELCHAIR - corresponds to a wheelchair car call. VIP - corresponds to an VIP destination request.  |
| `dwellTime` | float | Optional | The number of seconds that the door should stay opened when reaching the destination floor. This number must a value between 0.5 and 25.5 and must be in 0.5 increments (i.e., "10.5" or "9.0"). This feature is only available for select elevator groups.  |
| `walkTime` | int(15, 30, 45) | Optional | The approximate time, in seconds, that it would take the passenger to reach the elevator.  |


For additional guidance, please contact OID support at support-oid@otis.com

#### Example

```json
{
    "groupId": 1,
    "destFloor": 9,
    "destSide": "FRONT",
    "srcFloor": 4,
    "srcSide": "FRONT",
    "walkTime": 15,
    "type": "STANDARD"
}
```


### 5. Send Hall Call Event (sendHallCall)

This is the event to send when you want to call a machine to a specific floor. It is the programmatic equivalent of pressing the "up" or "down" button while waiting in the hall for an elevator to arrive. Once this event is sent to the API, the API will respond back with a hallCall event that will notify you of the state of your hall call. If a sendHallCall event is sent and the API responds back with a hallCall event where the hallCallState is hallCallAccepted, then the API will broadcast to you the following events for the assigned machine for which the sendHallCall event was sent:

- carCall
- carPosition
- direction
- doorStatus
- loadChange

Once the API has responded with a hallCall event where the hallCallState is hallCallServed, and the door has done a full door cycle (you will receive doorStatus events where the state is OPENING,OPENED ,CLOSING, and CLOSED, in that order), the above events will stop being sent to you for that particular machine (unless you have another sendCarCall, sendHallCall, or sendDestinationRequest in progress for the same machine).

| Name | Type | Inclusion | Description | 
| ---- | ---- | --------- | ----------- | 
| `direction` | string("UP", "DOWN") | **Required** | The direction in which destination floor is located. |
| `floor` | int | **Required** | The index of the destination floor that the car should be sent to (note, floor positions are zero-based indexed).  |
| `groupId` | int | **Required** | The id of the elevator group that the machine is in.  |
| `side` | string("FRONT", "REAR") | **Required** | Indicates whether the front door of the elevator or the rear door of the elevator should open once the destination floor is reached.  |
| `type` | string("STANDARD", "WHEELCHAIR", "EXTENDED") | **Required** | The type of hall call that is being placed. Valid values are: STANDARD - corresponds to a standard car call. WHEELCHAIR - corresponds to a wheelchair car call. VIP - corresponds to an VIP destination request. EXTENDED - corresponds to an extended hall call. EHS - corresponds to Express Priority hall call. EHS call type enables robots priority access for riding elevators with no other passengers. After initiating this call, elevator demand is re-routed to other elevators and/or is served prior to dispatching the elevator to the robot's landing. The robot can then enter an empty(in most cases)elevator and place their final destination call. The elevator will not stop at any other floors until the robot's request has been served. Additional benefits of this call include selecting a particular car in a group to perform robotic operation, along with slightly longer door open times. |

For additional guidance, please contact OID support at support-oid@otis.com

#### Example

```json
{
    "groupId": 1,
    "direction": "DOWN",
    "side": "FRONT",
    "floor": 2,
    "type": "STANDARD"
}
```


## Receive Responses

TBD

