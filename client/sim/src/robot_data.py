from dataclasses import dataclass, field


@dataclass
class Timestamp:
    sec: int = 0
    nanosec: int = 0


@dataclass
class Vector3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class BatteryState:
    stamp: Timestamp = field(default_factory=Timestamp)
    battery_cell_balance_status_all: int = 0
    battery_charge_current_limit: int = 0
    battery_charge_cut_off_current: int = 0
    battery_charge_fault: int = 0
    battery_current: int = 0
    battery_current_stored_ah: int = 0
    battery_discharge_current_limit: int = 0
    battery_discharge_cut_off_voltage: int = 0
    battery_discharge_fault: int = 0
    battery_fullycharged: int = 0
    battery_heater_status: int = 0
    battery_max_allowed_charge_voltage: int = 0
    battery_numberofbatteries: int = 0
    battery_number_of_active_batteries: int = 0
    battery_number_of_batteries_fault: int = 0
    battery_operational_mode: int = 0
    battery_pack_voltage: int = 0
    battery_pack_voltage_all: int = 0
    battery_regen_current_limit: int = 0
    battery_remaining_charge_time: int = 0
    battery_remaining_run_time: int = 0
    battery_soc_percent: int = 100
    battery_soc_percent_all: int = 0
    battery_soh: int = 0
    battery_temperature: int = 0
    battery_temperature_all: int = 0
    battery_max_cell_voltage: int = 0
    battery_min_cell_voltage: int = 0
    master_node_id: int = 0


@dataclass
class ComputerState:
    stamp: Timestamp = field(default_factory=Timestamp)
    total_diskspace: int = 1_099_511_627_776
    used_diskspace: int = 329_853_488_332
    free_diskspace: int = 769_658_139_444
    total_memory: int = 0
    used_memory: int = 0
    free_memory: int = 0
    user_cpu: float = 0.0
    system_cpu: float = 0.0
    idle_cpu: float = 0.0
    computer_power: int = 0
    temperature_cpu: float = 0.0
    temperature_gpu: float = 0.0
    temperature_soc0: float = 0.0
    temperature_soc1: float = 0.0
    temperature_soc2: float = 0.0
    temperature_tboard: float = 0.0
    temperature_tdiode: float = 0.0
    temperature_tj: float = 0.0


@dataclass
class InHouseState:
    stamp: Timestamp = field(default_factory=Timestamp)
    driveblock_state: str = ""
    amr_state: str = ""
    front_amr_led_state: str = ""
    back_amr_led_state: str = ""
    elevator_pressure_state: str = ""
    amm_state: str = ""
    backpack_0_state: str = ""
    backpack_1_state: str = ""
    backpack_2_state: str = ""
    backpack_3_state: str = ""
    backpack_4_state: str = ""
    backpack_5_state: str = ""
    elevator_pressure_status1: str = ""
    elevator_pressure_status2: str = ""
    elevator_pressure_status3: str = ""
    elevator_pressure_status4: str = ""
    backpack_0_item_y: float = 0.0
    backpack_1_item_y: float = 0.0
    backpack_2_item_y: float = 0.0
    backpack_3_item_y: float = 0.0
    backpack_4_item_y: float = 0.0
    backpack_5_item_y: float = 0.0
    backpack_0_item_z: float = 0.0
    backpack_1_item_z: float = 0.0
    backpack_2_item_z: float = 0.0
    backpack_3_item_z: float = 0.0
    backpack_4_item_z: float = 0.0
    backpack_5_item_z: float = 0.0
    amr_roll: float = 0.0
    amr_pitch: float = 0.0
    elevator_pressure_cylinder1_psi: int = 0
    elevator_pressure_cylinder2_psi: int = 0
    elevator_pressure_cylinder3_psi: int = 0
    elevator_pressure_cylinder4_psi: int = 0
    driveblock_distance_1: float = 0.0
    driveblock_distance_2: float = 0.0
    driveblock_distance_3: float = 0.0
    driveblock_distance_4: float = 0.0
    driveblock_distance_5: float = 0.0
    driveblock_distance_6: float = 0.0
    driveblock_distance_7: float = 0.0
    driveblock_distance_8: float = 0.0
    driveblock_left_pressure_1: float = 0.0
    driveblock_left_pressure_2: float = 0.0
    driveblock_left_pressure_3: float = 0.0
    driveblock_left_pressure_4: float = 0.0
    driveblock_left_pressure_5: float = 0.0
    driveblock_left_pressure_6: float = 0.0
    driveblock_right_pressure_1: float = 0.0
    driveblock_right_pressure_2: float = 0.0
    driveblock_right_pressure_3: float = 0.0
    driveblock_right_pressure_4: float = 0.0
    driveblock_right_pressure_5: float = 0.0
    driveblock_right_pressure_6: float = 0.0
    driveblock_item_x: float = 0.0
    amr_pressure_1: float = 0.0
    amr_pressure_2: float = 0.0
    amr_pressure_3: float = 0.0
    amr_pressure_4: float = 0.0
    amr_pressure_5: float = 0.0
    amr_pressure_6: float = 0.0
    amr_pressure_7: float = 0.0
    amr_pressure_8: float = 0.0


@dataclass
class KincoState:
    stamp: Timestamp = field(default_factory=Timestamp)
    trolley_y_movedone: int = 0
    elevator_y_movedone: int = 0
    trolley_y_washomed: int = 0
    elevator_y_washomed: int = 0
    trolley_y_position_meters: float = 0.0
    elevator_y_position_meters: float = 0.0
    wire_encoder_position_meters: float = 0.0
    trolley_y_operationmode: int = 0
    elevator_y_operationmode: int = 0
    trolley_y_operationmodebuffer: int = 0
    elevator_y_operationmodebuffer: int = 0
    trolley_y_current: int = 0
    elevator_y_current: int = 0
    trolley_y_voltage: int = 0
    elevator_y_voltage: int = 0


@dataclass
class NavigationState:
    stamp: Timestamp = field(default_factory=Timestamp)
    confidence: float = 0.0
    x: float = 0.0
    y: float = 0.0
    angle: float = 0.0
    current_station: str = ""
    vx: float = 0.0
    vy: float = 0.0
    w: float = 0.0
    yaw: float = 0.0
    roll: float = 0.0
    pitch: float = 0.0
    steer: float = 0.0
    blocked: bool = False
    emergency: bool = False


@dataclass
class TeknicState:
    stamp: Timestamp = field(default_factory=Timestamp)
    arm_z_movedone: int = 0
    driveblock_z_movedone: int = 0
    cups_x_movedone: int = 0
    burrow_x_movedone: int = 0
    amr_cups_left_y_movedone: int = 0
    amr_cups_right_y_movedone: int = 0
    arm_z_washomed: int = 0
    driveblock_z_washomed: int = 0
    cups_x_washomed: int = 0
    burrow_x_washomed: int = 0
    amr_cups_left_y_washomed: int = 0
    amr_cups_right_y_washomed: int = 0
    arm_z_position_meters: float = 0.0
    driveblock_z_position_meters: float = 0.0
    cups_x_position_meters: float = 0.0
    burrow_x_position_meters: float = 0.0
    amr_cups_left_y_position_meters: float = 0.0
    amr_cups_right_y_position_meters: float = 0.0
    arm_z_torque: float = 0.0
    driveblock_z_torque: float = 0.0
    cups_x_torque: float = 0.0
    burrow_x_torque: float = 0.0
    amr_cups_left_y_torque: float = 0.0
    amr_cups_right_y_torque: float = 0.0
    arm_z_velocity: float = 0.0
    driveblock_z_velocity: float = 0.0
    cups_x_velocity: float = 0.0
    burrow_x_velocity: float = 0.0
    amr_cups_left_y_velocity: float = 0.0
    amr_cups_right_y_velocity: float = 0.0
    arm_z_ina: int = 0
    burrow_x_inb: int = 0


@dataclass
class RobotState:
    stamp: Timestamp = field(default_factory=Timestamp)
    healthy: bool = True
    global_position: Vector3 = field(default_factory=Vector3)


@dataclass
class RobotStateLowFrequency:
    stamp: Timestamp = field(default_factory=Timestamp)
    battery_state: BatteryState = field(default_factory=BatteryState)
    computer_state: ComputerState = field(default_factory=ComputerState)
    in_house_state: InHouseState = field(default_factory=InHouseState)
    kinco_state: KincoState = field(default_factory=KincoState)
    navigation_state: NavigationState = field(default_factory=NavigationState)
    teknic_state: TeknicState = field(default_factory=TeknicState)
