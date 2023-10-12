"""BuildingConfig Model

SPDX-FileCopyrightText: Maximilian Hillen <maximilian.hillen@dlr.de>

"""
import pandas as pd
from calculate_gain_by_Sun import Window
from dataclasses import dataclass
import os

mainPath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
tabula_df = pd.DataFrame(
    pd.read_csv(
        os.path.join(
            mainPath, "thermal_building_model", "tabula_data_sorted.csv"
        ),
        low_memory=False,
    )
)


@dataclass
class BuildingConfig:
    r"""
    The BuildingConfig gets generated by the function build_building_config of the building class

    Parameters
    ----------
    h_ve: numeric :
        Value which describes the conductance to ventilation in W/K.
    h_tr_w : numeric
        Value which describes the conductance to exterior through glazed surfaces in W/K.
    h_tr_em : numeric
        Value which describes the conductance of opaque surfaces to exterior in W/K.
    h_tr_is : numeric
        Value which describes the conductance from the conditioned air to interior zone surface in W/K.
    mass_area : list
        Value which describes the effective mass area in m2
    h_tr_ms : numeric
        Value which describes the transmittance from the internal air to the thermal mass in W/K.
    c_m : numeric
        Value of room capacitance in kWh/K
    floor_area : numeric
        Value of the floor area in m2.
    heat_transfer_coefficient_ventilation : numeric
        Value of...
    total_air_change_rate : numeric
        Value of total air changes in m3/s
    Notes
    -----
    Examples
    --------
    """
    total_internal_area: float
    h_ve: float
    h_tr_w: float
    h_tr_em: float
    h_tr_is: float
    mass_area: float
    h_tr_ms: float
    c_m: float
    floor_area: float
    heat_transfer_coefficient_ventilation: float
    total_air_change_rate: float


class Building:
    def __init__(
        self,
        tabula_building_code: str,
        class_building: str,
        number_of_time_steps: float,
    ):
        self.tabula_building_code = tabula_building_code
        self.class_building = class_building
        self.number_of_time_steps = number_of_time_steps
        # DIN 13790: 12.3.1.2
        self.list_class_buildig = {
            "very light": {"a_m_var": 2.5, "c_m_var": 80000},
            "light": {"a_m_var": 2.5, "c_m_var": 110000},
            "average": {"a_m_var": 2.5, "c_m_var": 165000},
            "heavy": {"a_m_var": 3.0, "c_m_var": 260000},
            "very heavy": {"a_m_var": 3.0, "c_m_var": 370000},
        }
        self.building_config = {}

    def calculate_all_parameters(self):
        self.get_building_parameters_from_csv()
        self.total_internal_area: float = self.calc_internal_area()
        self.h_ve: float = self.calc_h_ve()
        self.h_tr_w: float = self.calc_h_tr_w()
        self.h_tr_em: float = self.calc_h_tr_em()
        self.h_tr_is: float = self.calf_h_tr_is()
        self.mass_area: float = self.calc_mass_area()
        self.h_tr_ms: float = self.calf_h_tr_ms()
        self.c_m: float = self.calc_c_m()
        # self.solar_gains : list  = self.calc_solar_gaings_through_windows()
        self.building_config = self.build_building_config()

    def build_building_config(self):
        building_config = BuildingConfig(
            total_internal_area=self.total_internal_area,
            h_ve=self.h_ve,
            h_tr_w=self.h_tr_w,
            h_tr_em=self.h_tr_em,
            h_tr_is=self.h_tr_is,
            mass_area=self.mass_area,
            h_tr_ms=self.h_tr_ms,
            c_m=self.c_m,
            floor_area=self.floor_area,
            heat_transfer_coefficient_ventilation=self.heat_transfer_coefficient_ventilation,
            total_air_change_rate=self.total_air_change_rate,
        )
        return building_config

    def get_building_parameters_from_csv(self):
        row = tabula_df.loc[
            tabula_df["Code_BuildingVariant"] == self.tabula_building_code
        ]
        list_type = ["", "Measure_", "Actual_"]
        t_b = list_type[1]
        self.opaque_elements = ["wall", "roof", "floor"]

        self.a_roof = {
            "a_roof_1": float(row["A_Roof_1"].values[0]),
            "a_roof_2": float(row["A_Roof_2"].values[0]),
        }
        self.u_roof = {
            "u_roof_1": float(row["U_" + str(t_b) + "Roof_1"].values[0]),
            "u_roof_2": float(row["U_" + str(t_b) + "Roof_2"].values[0]),
        }
        self.b_roof = {
            "b_roof_1": float(row["b_Transmission_Roof_1"].values[0]),
            "b_roof_2": float(row["b_Transmission_Roof_2"].values[0]),
        }

        self.a_floor = {
            "a_floor_1": float(row["A_Floor_1"].values[0]),
            "a_floor_2": float(row["A_Floor_2"].values[0]),
        }
        self.u_floor = {
            "u_floor_1": float(row["U_" + str(t_b) + "Floor_1"].values[0]),
            "u_floor_2": float(row["U_" + str(t_b) + "Floor_2"].values[0]),
        }
        self.b_floor = {
            "b_floor_1": float(row["b_Transmission_Floor_1"].values[0]),
            "b_floor_2": float(row["b_Transmission_Floor_2"].values[0]),
        }

        self.a_wall = {
            "a_wall_1": float(row["A_Wall_1"].values[0]),
            "a_wall_2": float(row["A_Wall_2"].values[0]),
            "a_wall_3": float(row["A_Wall_3"].values[0]),
        }
        self.u_wall = {
            "u_wall_1": float(row["U_" + str(t_b) + "Wall_1"].values[0]),
            "u_wall_2": float(row["U_" + str(t_b) + "Wall_2"].values[0]),
            "u_wall_3": float(row["U_" + str(t_b) + "Wall_3"].values[0]),
        }
        self.b_wall = {
            "b_wall_1": float(row["b_Transmission_Wall_1"].values[0]),
            "b_wall_2": float(row["b_Transmission_Wall_2"].values[0]),
            "b_wall_3": float(row["b_Transmission_Wall_3"].values[0]),
        }

        self.a_door = {"a_door_1": float(row["A_Door_1"].values[0])}
        self.u_door = {
            "u_door_1": float(row["U_" + str(t_b) + "Door_1"].values[0])
        }

        self.a_window = {
            "a_window_1": float(row["A_Window_1"].values[0]),
            "a_window_2": float(row["A_Window_2"].values[0]),
        }
        self.a_window_specific = {
            "a_window_horizontal": float(row["A_Window_Horizontal"].values[0]),
            "a_window_east": float(row["A_Window_East"].values[0]),
            "a_window_south": float(row["A_Window_South"].values[0]),
            "a_window_west": float(row["A_Window_West"].values[0]),
            "a_window_north": float(row["A_Window_North"].values[0]),
        }
        self.delta_u_thermal_bridiging = {
            "delta_u_thermal_bridiging": float(
                row["delta_U_ThermalBridging"].values[0]
            )
        }
        self.u_window = {
            "u_window_1": float(row["U_" + str(t_b) + "Window_1"].values[0]),
            "u_window_2": float(row["U_" + str(t_b) + "Window_2"].values[0]),
        }

        self.g_gl_n_window = {
            "g_gl_n_window_1": float(
                row["g_gl_n_" + str(t_b) + "Window_1"].values[0]
            ),
            "g_gl_n_window_2": float(
                row["g_gl_n_" + str(t_b) + "Window_2"].values[0]
            ),
        }

        self.floor_area = float(row["A_C_Ref"].values[0])
        self.heat_transfer_coefficient_ventilation = float(
            row["h_Ventilation"].values[0]
        )

        # References to check results
        self.q_transmission_losses_annual = float(
            row["q_ht_tr"].values[0] * self.floor_area
        )  # [kWh/a)]
        self.q_ventilation_losses_annual = float(
            row["q_ht_ve"].values[0] * self.floor_area
        )  # [kWh/a)]
        self.q_total_losses_annual = float(
            row["q_ht"].values[0]
        )  # [kWh/(m²a)]
        self.q_solar_gains_annual = float(
            row["q_sol"].values[0]
        )  # [kWh/(m²a)]
        self.q_internal_gains_annual = float(
            row["q_int"].values[0]
        )  # [kWh/(m²a)]
        self.q_internal_gains_annual = float(
            row["q_int"].values[0]
        )  # [kWh/(m²a)]
        self.total_air_change_rate = float(
            row["n_air_use"] + row["n_air_infiltration"]
        )  # [1/h]
        self.room_height = float(row["h_room"])  # [m]
        self.q_total_losses = float(row["q_ht"] * self.floor_area)  # [kWh/a]
        self.q_heating_demand_annual = float(
            row["q_h_nd"] * self.floor_area
        )  # [kWh/a]
        self.h_transmission = float(
            row["h_Transmission"] * self.floor_area
        )  # [W/K]
        self.h_ventilation = float(
            row["h_Ventilation"] * self.floor_area
        )  # [W/K]

    def calc_internal_area(self):
        # DIN 7.2.2.2
        var_at = 4.5  # the dimensionless ratio between the surface area of all surfaces facing into the room and the useful area.
        total_internal_area = self.floor_area * var_at
        return total_internal_area

    def calc_h_tr_em(self):
        h_tr_em = 0
        a_external = 0
        for x in range(1, len(self.a_wall) + 1):
            h_tr_em = (
                h_tr_em
                + self.a_wall["a_wall_" + str(x)]
                * self.u_wall["u_wall_" + str(x)]
                * self.b_wall["b_wall_" + str(x)]
            )
            a_external = a_external + self.a_wall["a_wall_" + str(x)]

        for x in range(1, len(self.a_roof) + 1):
            h_tr_em = (
                h_tr_em
                + self.a_roof["a_roof_" + str(x)]
                * self.u_roof["u_roof_" + str(x)]
                * self.b_roof["b_roof_" + str(x)]
            )
            a_external = a_external + self.a_roof["a_roof_" + str(x)]

        for x in range(1, len(self.a_floor) + 1):
            h_tr_em = (
                h_tr_em
                + self.a_floor["a_floor_" + str(x)]
                * self.u_floor["u_floor_" + str(x)]
                * self.b_floor["b_floor_" + str(x)]
            )
            a_external = a_external + self.a_floor["a_floor_" + str(x)]

        for x in range(1, len(self.a_door) + 1):
            h_tr_em = (
                h_tr_em
                + self.a_door["a_door_" + str(x)]
                * self.u_door["u_door_" + str(x)]
            )
            a_external = a_external + self.a_door["a_door_" + str(x)]
        h_tr_em = (
            h_tr_em
            + self.delta_u_thermal_bridiging["delta_u_thermal_bridiging"]
            * a_external
        )
        return h_tr_em  # [W/K]

    def calc_h_tr_w(self):
        h_tr_w = 0
        a_window = 0
        for x in range(1, len(self.a_window) + 1):
            h_tr_w = (
                h_tr_w
                + self.a_window["a_window_" + str(x)]
                * self.u_window["u_window_" + str(x)]
            )
            a_window = a_window * self.a_window["a_window_" + str(x)]
        h_tr_w = (
            h_tr_w
            + self.delta_u_thermal_bridiging["delta_u_thermal_bridiging"]
            * a_window
        )
        return h_tr_w  # [W/K]

    def calc_h_ve(self):
        # Determine the ventilation conductance, based on DIN13790 9.3.1
        air_cap_vol_heat = 1200  # volume-related heat storage capacity of the air in [J/(m^3 * K)]
        total_air_change_per_hour = (
            self.total_air_change_rate * self.room_height * self.floor_area
        )  # [m^3 / h]

        h_ve = (air_cap_vol_heat / 3600) * total_air_change_per_hour  # [W/K]
        return h_ve

    def calf_h_tr_ms(self):
        h_tr_ms = 9.1 * self.mass_area
        return h_tr_ms

    def calf_h_tr_is(self):
        h_tr_is = 3.45 * self.total_internal_area
        return h_tr_is

    def calc_mass_area(self):
        # Based on ISO standard 12.3.1.2
        mass_area = (
            self.floor_area
            * self.list_class_buildig[self.class_building]["a_m_var"]
        )
        return mass_area

    def calc_c_m(self):
        # [kWh/K] Room Capacitance. Based on ISO standard 12.3.1.2
        c_m = (
            self.floor_area
            * self.list_class_buildig[self.class_building]["c_m_var"]
        )
        return c_m

    def calc_solar_gaings_through_windows(self, object_location_of_building):
        a_window_total = 0
        g_gl_n_window_avg = 0
        for x in range(1, len(self.u_window) + 1):
            a_window_total = (
                a_window_total + self.a_window["a_window_" + str(x)]
            )

        for x in range(1, len(self.g_gl_n_window) + 1):
            g_gl_n_window_avg = (
                g_gl_n_window_avg
                + (
                    self.g_gl_n_window["g_gl_n_window_" + str(x)]
                    * self.a_window["a_window_" + str(x)]
                )
                / a_window_total
            )

        compass_directions = {
            "north": {"azimuth_tilt": 270, "alititude_tilt": 90},
            "east": {"azimuth_tilt": 90, "alititude_tilt": 90},
            "south": {"azimuth_tilt": 180, "alititude_tilt": 90},
            "west": {"azimuth_tilt": 0, "alititude_tilt": 90},
            "horizontal": {"azimuth_tilt": 0, "alititude_tilt": 0},
        }
        list_solar_gains = []
        for hour in range(self.number_of_time_steps):
            sum_solar_gains = 0
            for x in compass_directions:
                (
                    altitude,
                    azimuth,
                ) = object_location_of_building.calc_sun_position(
                    latitude_deg=48.16,
                    longitude_deg=46.38,
                    year=2015,
                    hoy=hour,
                )
                azimuth_tilt = compass_directions[x]["azimuth_tilt"]
                alititude_tilt = compass_directions[x]["alititude_tilt"]
                window_var = Window(
                    azimuth_tilt=azimuth_tilt,
                    alititude_tilt=alititude_tilt,
                    glass_solar_transmittance=g_gl_n_window_avg,
                    glass_light_transmittance=0.8,
                    area=self.a_window_specific["a_window_" + str(x)],
                )

                window_var.calc_solar_gains(
                    sun_altitude=altitude,
                    sun_azimuth=azimuth,
                    normal_direct_radiation=object_location_of_building.weather_data[
                        "dirnorrad_Whm2"
                    ][
                        hour
                    ],
                    horizontal_diffuse_radiation=object_location_of_building.weather_data[
                        "difhorrad_Whm2"
                    ][
                        hour
                    ],
                )
                sum_solar_gains = window_var.solar_gains + sum_solar_gains
            list_solar_gains.append(sum_solar_gains)
        return list_solar_gains
