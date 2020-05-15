# coding: utf-8

# https://developer.nuki.io/page/nuki-bridge-http-api-1-10/4#heading--lock-actions
ACTION_LOCK_UNLOCK = 1
ACTION_LOCK_LOCK = 2
ACTION_LOCK_UNLATCH = 3
ACTION_LOCK_LOCK_N_GO = 4
ACTION_LOCK_LOCK_N_GO_WITH_UNLATCH = 5

ACTION_OPENER_ACTIVATE_RTO = 1
ACTION_OPENER_DEACTIVATE_RTO = 2
ACTION_OPENER_ELECTRIC_STRIKE_ACTUATION = 3
ACTION_OPENER_ACTIVATE_CONTINUOUS = 4
ACTION_OPENER_DEACTIVATE_CONTINUOUS = 5

# https://developer.nuki.io/page/nuki-bridge-http-api-1-10/4#heading--info
BRIDGE_TYPE_HW = 1
BRIDGE_TYPE_SW = 2

# https://developer.nuki.io/page/nuki-bridge-http-api-1-10/4#heading--device-types
DEVICE_TYPE_LOCK = 0
DEVICE_TYPE_OPENER = 2

# https://developer.nuki.io/page/nuki-bridge-http-api-1-10/4#heading--modes
MODE_LOCK_DOOR = 2
MODE_OPENER_DOOR = 2
MODE_OPENER_CONTINUOUS = 3

# https://developer.nuki.io/page/nuki-bridge-http-api-1-10/4/#heading--lock-states
STATE_LOCK_UNCALIBRATED = 0
STATE_LOCK_LOCKED = 1
STATE_LOCK_UNLOCKING = 2
STATE_LOCK_UNLOCKED = 3
STATE_LOCK_LOCKING = 4
STATE_LOCK_UNLATCHED = 5
STATE_LOCK_UNLOCKED_LOCK_N_GO = 6
STATE_LOCK_UNLATCHING = 7
STATE_LOCK_MOTOR_BLOCKED = 254
STATE_LOCK_UNDEFINED = 255

STATE_OPENER_UNTRAINED = 0
STATE_OPENER_ONLINE = 1
STATE_OPENER_RTO_ACTIVE = 3
STATE_OPENER_OPENER_OPEN = 5
