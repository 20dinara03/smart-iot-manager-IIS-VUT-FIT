from .dashboard import Dashboard
from .auth import AuthenticationLoginView, AuthenticationRegisterView, logout
from .groups import GroupList, ConcreteGroup
from .users import Users, UserDetail, update_user_groups
from .device import DeviceList, DeviceDetail, CreateDeviceView, DeleteDeviceView, UpdateDeviceView
from .device_types import DeviceTypeList, DeviceTypeCreate, DeviceTypeDetail, DeleteDeviceTypeView, UpdateDeviceTypeView
from .device_groups import (DeviceGroupListView, CreateDeviceGroupView, DeleteDeviceGroupView,
                            DeviceGroupDetailView, UpdateDeviceGroupView)
