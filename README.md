# Otis Elevator Python Module

This is a [Viam module](https://docs.viam.com/manage/configuration/#modules) for [Otis](https://www.otis.com/en/us)'s family of elevators. THis module provides a gateway to receiving status updates and sending out requests for various interactions.

This otis-elevators module is particularly useful in applications that require an Otis elevator to be operated in conjunction with other robots or technical systems offered by the [Viam Platform](https://www.viam.com/) and/or separate through custom code. 

## Configure your Otis Elevator

> [!NOTE]
> Before configuring your Kuka Arm, you must [add a machine](https://docs.viam.com/fleet/machines/#add-a-new-machine).

Navigate to the **CONFIGURE** tab of your machine’s page in [the Viam app](https://app.viam.com/). Click the **+** icon next to your machine part in the left-hand menu and select **Component**. Select the `sensor` or `generic` type, then search for and select the `sensor / otis-elevator` or `generic / otis-elevator` model. Click **Add module**, then enter a name or use the suggested name for your arm and click **Create**.

On the new component panel, copy and paste the following attribute template into your component's attributes field:

```json
{
  "client_id": "<STRING>",
  "client_secret": "<STRING>",
  "group_id": "<STRING>",
  "installation_id": "<STRING>",
  "log_level": "<BOOL>"
}
```

Edit the attributes as applicable.

> [!NOTE]
> For more information, see [Configure a Machine](https://docs.viam.com/build/configure/).

## Attributes

The following attributes are available:

| Name | Type | Inclusion | Description |
| ---- | ---- | --------- | ----------- |
| `client_id` | string | **Required** | The client API id provided by Otis in order to get an access token.  |
| `client_secret` | string | **Required** | The client API secret provided by Otis to get an access token.  |
| `group_id` | string | **Required** | The group id that corresponds to the desired group of elevators.  |
| `installation_id` | string | **Required** | The installation id that corresponds to the desired installation location.  |
| `log_level` | bool | Optional | A bool that, if true, will log all responses and requests made to the Otis API (via SocketIO) |