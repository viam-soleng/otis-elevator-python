# Interfacing with the Otis Elevator

This is a Socket.IO service that provides real-time two-way communication. Below are the details on both publishing and subscribing to /api/oid/v1.

## Send Requests

This section describes all of the events that you can send to the API in order to remotely control the elevator.

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

#### Payload

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

This section describes all of the events that you will receive from the API while interacting with it.

### 1. Car Call Event (carCall)

This is the event that is fired in response to a sendCarCall event.

#### Payload 

| Name | Type | Description | 
| ---- | ---- | ----------- | 
| `carCallState` | string("carCallAccepted", "carCallServed") | The state of the carCall as determined by the elevator controller. Possible values include: carCallAccepted - This state means that the elevator controller has accepted the sendCarCall event that was sent to the API and is dispatching the specific machine to the chosen floor. carCallServed - This state means that the elevator controller had dispatched the specific machine to the chosen floor, the machine had arrived at the floor and the doors successfully opened. |
| `deck` | string("TOP", "BOTTOM") | The deck on which the car call will be served. |
| `floor` | int | The index of the destination floor that the car will be sent to (note, floor positions are zero-based indexed). |
| `groupId` | int | The id of the elevator group that the machine is in. |
| `machineId` | int | The id of the machine that is serving the sendCarCall event. |
| `side` | string("FRONT", "REAR") | Indicates whether the front door of the elevator or the rear door of the elevator will open once the destination floor is reached. |
| `type` | string("STANDARD", "WHEELCHAIR") | Indicates the type of car call that was placed. Valid values are: STANDARD - corresponds to a standard car call. WHEELCHAIR - corresponds to a wheelchair car call. |

#### Example

```json
{
    "carCallState": "carCallAccepted",
    "deck": "BOTTOM",
    "floor": 9,
    "groupId": 1,
    "machineId": 2,
    "side": "FRONT",
    "type": "STANDARD"
}
```


### 2. Car Mode Event (carMode)

This event is fired when there is a change in the car mode for a machine.

#### Payload 

| Name | Type | Description | 
| ---- | ---- | ----------- | 
| `groupId` | int | The id of the elevator group that the machine is in. |
| `machineId` | int | The id of the machine that is serving the sendCarCall event. |
| `mode` | string | The three letter code of the mode to which the machine has changed. Modes can vary per elevator group. Common values include: NOR - Normal mode, IDL - Idle mode, NAV - Not Available, DHB - Door Hold Mode, ATT - Robotic mode for Attendant like operation, EFO - Emergency Fire Service Operation, EFS - Emergency Fireman Service, EQO - Earthquake Operation, EHS - Express Priority Service mode, ISC - Independent service mode, or PKS - Park and shut down mode. IDL and NOR are indicative of normal elevator operation and are best suited for taking demand from robots via API's. Other modes like EFO and EFS indicate certain special or emergency conditions in the building. Elevator's response during these emergency modes is in accordance to local state or national codes and may not always be optimal for robots. |

For guidance on determining best course of action during these emergency or special modes, please contact OID support at support-oid@otis.com

#### Example

```json
{
    "groupId": 1,
    "machineId": 5,
    "mode": "ISC"
}
```


### 3. Car Position Event (carPosition)

This event shows the current floor position of the machine in a group when the machine is moving between floors.

#### Payload 

| Name | Type | Description | 
| ---- | ---- | ----------- | 
| `groupId` | int | The id of the elevator group that the machine is in. |
| `machineId` | int | The id of the machine that is serving the sendCarCall event. |
| `position` | int | The floor position that the machine has changed to. |

#### Example

```json
{
    "groupId": 1,
    "machineId": 5,
    "position": 2
}
```


### 4. Car Status Event (carStatus)

This event shows the current floor position of the machine in a group when the machine is moving between floors.

#### Payload 

| Name | Type | Description | 
| ---- | ---- | ----------- | 
| `committedDirection` | string("DOWN", "NONE", "UP") | The direction in which the machine is committed to moving next. |
| `committedPosition` | int | The floor position to which the machine is committed to moving next. |
| `direction` | string("DOWN", "NONE", "UP") | The direction in which the machine is moving. |
| `doorStatus` | array | This is an array of objects that indicates the door status for each door on the car. It includes: "deck" - string("BOTTOM", "TOP"), "side" - string("FRONT", "READ"), "state" - string("CLOSED", "CLOSING", "OPENING", "OPENED") |
| `load` | array | The load of the elevator cab. It includes either "BOTTOM" or "TOP" with the associated load value. Possible load values include: EMPTY - The elevator cab is less than 10% of its capacity. FULL - The elevator cab is between 80% and 110% of its capacity. NORMAL - The elevator cab is between 10% and 50% of its capacity. OVERLOADED - The elevator cab is above 110% of its capacity. PEAK - The elevator cab is between 50% and 80% of its capacity. |
| `machineId` | int | The id of the machine for which the status is being returned. |
| `mode` | int | The three letter code of the mode to which the machine has changed. Modes can vary per elevator group. Common values include: NOR - Normal mode. IDL - Idle mode. NAV - Not Available. DHB - Door Hold Mode. ATT - Robotic mode for Attendant like operation. EFO - Emergency Fire Service Operation. EFS - Emergency Fireman Service. EQO - Earthquake Operation. EHS - Express Priority Service mode. ISC - Independent service mode. PKS - Park and shut down mode. |
| `position` | int | The floor position that the machine has changed to. |

#### Example

```json
{
    "committedDirection": "UP",
    "committedPosition": 10,
    "direction": "UP",
    "doorStatus":[
        {
            "deck": "BOTTOM",
            "side": "FRONT",
            "state": "CLOSED"
        },
        {
            "deck": "BOTTOM",
            "side": "REAR",
            "state": "CLOSED"
        }
    ],
    "load": 
    {
        "TOP": "EMPTY",
        "BOTTOM": "EMPTY"
    },
    "machineId": 3,
    "mode": "IDL",
    "position": 8
}
```


### 5. Destination Request Event (destinationRequest)

This event is fired in response to a sendDestinationRequest.

#### Payload 

| Name | Type | Description | 
| ---- | ---- | ----------- | 
| `destinationRequestState` | string("destinationRequestAccepted") | The state of the destinationRequest as determined by the elevator controller. Possible values include: destinationRequestAccepted - This state means that the elevator controller has accepted the sendDestinationRequest event that was sent to the API and is dispatching the assigned machine to the floor specified in the sendDestinationRequest event. |
| `machineId` | int | The id of the machine that was assigned by the elevator controller to serve the sendDestinationRequest. |
| `groupId` | int | The id of the elevator group that the machine is in. |

#### Example

```json
{
    "destinationRequestState": "destinationRequestAccepted",
    "groupId": 1,
    "machineId": 2
}
```


### 6. Direction Event (direction)

This event is fired if there is a change in the current direction of a machine.

#### Payload 

| Name | Type | Description | 
| ---- | ---- | ----------- | 
| `destinationRequestState` | string("UP", "DOWN", "NONE") | The new direction that the machine is now going in. Valid values are: DOWN - indicates that the elevator is moving in the 'down' direction. NONE - indicates that the elevator does not have a direction assigned (this happens when the elevator is in idle mode). UP- indicates that the elevator is moving in the 'up' direction. |
| `machineId` | int | The id of the machine that is serving the sendCarCall event. |
| `groupId` | int | The id of the elevator group that the machine is in. |

#### Example

```json
{
    "direction": "UP",
    "groupId": 1,
    "machineId": 2
}
```


### 7. Door Status Event (doorStatus)

This event is fired when the state of the machine door has changed.

#### Payload 

| Name | Type | Description | 
| ---- | ---- | ----------- | 
| `destinationRequestState` | string("UP", "DOWN", "NONE") | The new direction that the machine is now going in. Valid values are: DOWN - indicates that the elevator is moving in the 'down' direction. NONE - indicates that the elevator does not have a direction assigned (this happens when the elevator is in idle mode). UP- indicates that the elevator is moving in the 'up' direction. |
| `machineId` | int | The id of the machine that is serving the sendCarCall event. |
| `groupId` | int | The id of the elevator group that the machine is in. |
| `deck` | string("TOP", "BOTTOM") | The deck on which the state of the door has changed. |
| `side` | string("FRONT", "REAR") | Indicates the side of the elevator for which the door status has changed. |
| `state` | string("CLOSED", "CLOSING", "OPENED", "OPENING") | The state that the door has changed to. Valid values for this field are: CLOSED - indicates that the door is fully closed. CLOSING - indicates that the door is in the process of closing from an opened state, but hasn't fully closed yet. OPENED - indicates that the door is fully open. OPENING - indicates that the door is in the process of opening from a closed state, but hasn't fully opened yet. |

#### Example

```json
{
    "deck": "BOTTOM",
    "groupid": 1,
    "machineId": 5,
    "side": "FRONT",
    "state": "OPENING"
}
```


### 8. Exception Event (exception)

This event is sent if an error occurs when communicating with the API.

#### Payload 

| Name | Type | Description | 
| ---- | ---- | ----------- | 
| `socketId` | string | The Id of the socket on which the error occurred. |
| `timestamp` | string | The time at which the error occurred in ISO 8601 format. |
| `message` | string | A user friendly message that indicates the nature of the error. |
| `code` | int | The code that represents the specific error that was encountered. Error codes will follow the below convention: 4xxxx Client side errors, 41xxx - Validation errors, 42xxx - Authorization errors, 43xxx - Connection errors, 5xxxx - Application side errors, 51xxx - Elevator controller errors, or 52xxx - Other server side errors. |

#### Example

```json
{
    "code": 41000,
    "message": "The application cannot complete the operation because the type is either missing or invalid. Please supply a valid value in the 'type' field.",
    "timestamp": "2022-10-18T05:39:53+0000",
    "socketId": "D2J1GrHUtYyxJM6QAAAA"
}
```


### 9. Group Status Event (groupStatus)

This event is sent right at the point of connecting to the API to give you a snapshot of the state of the elevator group in that moment.

#### Payload 

| Name | Type | Description | 
| ---- | ---- | ----------- | 
| `available` | bool | An indication of whether or not the elevator group is available for service. |
| `groupId` | int | The id of the elevator group for which the status is being given. |
| `groupMode` | int | The numeric code indicating the mode of the group. |
| `modeName` | string | The three letter code of the mode of the group. |
| `machines` | array | This array contains the various machines with relevant information:  available - bool, machineId - string, mode - string, and position - int. |

#### Example

```json
{
    "groupId": 1,
    "available": true,
    "machines": [
        {
        "machineId": 1,
        "available": true,
        "position": 9,
        "mode": "NOR"
        },
        {
        "machineId": 2,
        "available": true,
        "position": 5,
        "mode": "NOR"
        }
    ]
}
```


### 10. Hall Call Event (hallCall)

This is the event that is fired in response to a sendHallCall event.

#### Payload 

| Name | Type | Description | 
| ---- | ---- | ----------- | 
| `hallCallState` | string("hallCallAccepted", "hallCallServed") | The state of the hallCall as determined by the elevator controller. Possible values include: hallCallAccepted - This state means that the elevator controller has accepted the sendHallCall event that was sent to the API and is dispatching a machine to the floor specified in the sendHallCall event.hallCallServed - This state means that the elevator controller had dispatched a machine to the floor specified sendHallCall event, the machine had arrived at the floor and the doors successfully opened. |
| `groupId` | int | The id of the elevator group that the machine is in. |
| `machineId` | int | The id of the machine that has been assigned and is serving the sendHallCall event. |
| `floor` | int | The index of the floor to which the assigned machine is being sent (note, floor positions are zero-based indexed). |
| `deck` | string("TOP", "BOTTOM") | The deck on which the hall call will be served. |
| `direction` | string("UP", "DOWN") | The direction indicated in the sendHallCall event. |

#### Example

```json
{
    "hallCallState": "hallCallAccepted",
    "groupId": 4,
    "machineId": 1,
    "floor": 14,
    "deck": "BOTTOM",
    "direction": "DOWN",
    "side": "FRONT",
    "type": "STANDARD"
}
```


### 11. Load Change Event (loadChange)

This event is fired when the load of a machine changes.

#### Payload 

| Name | Type | Description | 
| ---- | ---- | ----------- | 
| `groupId` | int | The id of the elevator group that the machine is in. |
| `machineId` | int | The id of the machine that has had its load change. |
| `loadLevel` | string | The load level of the machine. Possible values include: EMPTY - This indicates that the machine is now empty. NORMAL - This indicates that the machine has a normal load. PEAK - This indicates that the machine is experiencing peak load. FULL - This indicates that the machine is full. OVERLOADED - This indicates that the machine is overloaded. |
| `deck` | string("TOP", "BOTTOM") | The deck of the machine on which the load has changed. |

#### Example

```json
{
    "groupId": 1,
    "machineId": 2,
    "loadLevel": "NORMAL",
    "deck": "BOTTOM"
}
```

s
### 12. Session Data Event (sessionData)

This event is sent upon a successful connection to the API. This includes relevant information related to the session that is started which can be helpful for tracking or debugging purposes.

#### Payload 

| Name | Type | Description | 
| ---- | ---- | ----------- | 
| `socketId` | string | The Id of the socket that is established upon connection. This is unique for every session on the API. |
| `timestamp` | string | The time at which the socket was successfully established in ISO 8601 format. |

#### Example

```json
{
    "socketId": "Eh6t1n1OGp4CwQArADcU", 
    "timestamp": "2024-10-03T17:48:56.114Z"
}
```
