from pulp import *
class PV:
    def __init__(self, om = 0.0005 , output = list()):
        self.om = om
        self.output = output
    def show(self):
        return {"运行成本(元/kWh)":self.om}


class electricStorage:
    def __init__(self, om = 0.005, Cbw = 0.00075 , capacity = 9600, SOCmin = 0.1, SOCmax = 0.9, SOCint = 0.1, Pmin = -1250, Pmax = 1250, efficiency = 0.95, selfRelease = 0.0025):
        self.om = om
        self.Cbw = Cbw
        self.capacity = capacity
        self.SOCmin = SOCmin
        self.SOCmax = SOCmax
        self.SOCint = SOCint
        self.Pmin = Pmin
        self.Pmax = Pmax
        self.efficiency = efficiency
        self.selfRelease = selfRelease
        self.maxDetP = self.Pmax * 1
        self.power_into = {}
        self.power_outof = {}
        self.energy = {}
    def show(self):
        return {"运行成本(元/kWh)":self.om,
                "折旧费用(元/kWh)":self.Cbw,
                "容量(kWh)":self.capacity,
                "最小SOC":self.SOCmin,
                "最大SOC":self.SOCmax,
                "初始SOC":self.SOCint,
                "最大充电功率(KW)":self.Pmax,
                "最大放电功率(KW)":-self.Pmin,
                "自损耗系数":self.selfRelease,
                "效率":self.efficiency}


class absorptionChiller:
    def __init__(self, om = 0.00008, COP_htc = 0.8, COP_hth = 1, Hmin = 0, Hmax = 1000):
        self.om = om
        self.COP_htc = COP_htc
        self.COP_hth = COP_hth
        self.Hmin = Hmin
        self.Hmax = Hmax
        self.result = {}
    def show(self):
        return {"运行成本(元/kWh)":self.om,
                "热-冷转化比":self.COP_htc,
                "热-热转化比":self.COP_hth}

class boiler:
    def __init__(self, om = 0.04, Pmax = 1000, Pmin = 0, efficiency = 0.95):
        self.om = om
        self.Pmin = Pmin
        self.Pmax = Pmax
        self.efficiency = efficiency
        self.result = {}
    def show(self):
        return {"运行成本(元/kWh)":self.om,
                "最大功率(kW)":self.Pmax,
                "最小功率(kW)":self.Pmin,
                "效率":self.efficiency}

class heatStorage:
    def __init__(self, om = 0.04, capacity = 2000, Tmin = 0, Tmax = 0.95, Tint = 0.1, Hmin = -1500, Hmax = 1500, selfRelease = 0.003):
        self.om = om
        self.capacity = capacity
        self.Tmin = Tmin
        self.Tmax = Tmax
        self.Tint = Tint
        self.Hmin = Hmin
        self.Hmax = Hmax
        self.selfRelease = selfRelease
        self.maxDetP = self.Hmax * 0.4
        self.result = {}
    def show(self):
        return {"运行成本(元/kWh)":self.om,
                "容量(kWh)":self.capacity,
                "最大储热量":self.Tmax,
                "初始储热量":self.Tint,
                "最大储热功率(KW)":self.Hmax,
                "最大放热功率(KW)":-self.Hmin}

class coldStorage:
    def __init__(self, om = 0.01, capacity = 3000, Tmin = 0.1, Tmax = 0.95, Tint = 0.1, Hin = 500, Hout = 500, Pmin = 0, Pmax = 500, maxdetP = 500, EER = 3 , efficiency = 0.9 , COP = 3 , Partition_in = 0.9, Partition_out = 0.9, mode = "并联" ,self_release = 0.001):
        self.om = om
        self.capacity = capacity
        self.Tmin = Tmin
        self.Tmax = Tmax
        self.Tint = Tint
        self.Hin = Hin
        self.Hout = Hout
        self.Pmax = Pmax
        self.Pmin = Pmin
        self.EER = EER
        self.efficiency = efficiency
        self.COP = COP
        self.Partition_in = Partition_in
        self.Partition_out = Partition_out
        self.mode = mode
        self.maxdetP = maxdetP
        self.self_release = self_release
        self.result_electricity_tank = {}
        self.result_cold_tank = {}
        self.result_electricity_ref = {}
    def show(self):
        return {"运行成本(元/kWh)":self.om,
                "容量(kWh)":self.capacity,
                "最大储冷量":self.Tmax,
                "最小储冷量":self.Tmin,
                "初始储冷量":self.Tint,
                "最大储冷功率(KW)":self.Hin,
                "最大供冷功率(KW)":-self.Hout,
                "制冷机的制冷能效比":self.COP,
                "供冷冷量分配系数":self.Partition_out,
                "储冷冷量分配系数":self.Partition_in,
                "能效比":self.EER,
                "效率":self.efficiency}

class airConditioner:## P>=0 cooling, P<0 heating
    def __init__(self, om = 0.0097, Pmax = 500, Pmin = 0, EER = 4.3 , COP = 3.6):
        self.om = om
        self.Pmax = Pmax
        self.EER = EER
        self.COP = COP
        self.Pmin = Pmin
        self.result = {}
    def show(self):
        return {"运行成本(元/kWh)":self.om,
                "最大制冷功率(kW)":self.Pmax,
                "最大制热功率(kW)":self.Pmin,
                "制冷能效比":self.EER,
                "制热能效比":self.COP}

class gasTurbine:
    def __init__(self, om = 0.063, Pmax = 1000, Pmin = 50, efficiency = 0.6, heat_recycle = 0.6):
        self.om = om
        self.Pmax = Pmax
        self.Pmin = Pmin
        self.efficiency = efficiency
        self.heat_recycle = heat_recycle
        self.HER = (1 - efficiency)/efficiency
        self.result = {}
    def show(self):
        return {"运行成本(元/kWh)":self.om,
                "最大技术出力(kW)":self.Pmax,
                "最小技术出力(kW)":self.Pmin,
                "效率":self.efficiency,
                "热电比":self.HER,
                "余热锅炉回收效率":self.heat_recycle}


class utility:
    def __init__(self, buy_price = 0.8, sell_price = 0, gas_price = 0.349,steam_price = 348/800):
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.gas_price = gas_price
        self.result = {}
        self.steam_price = steam_price
        self.gas_utility = {}
    def show(self):
        return {"上网电价":self.sell_price,
                "天然气价格(元/kWh)":self.gas_price}

class inverter:
    def __init__(self, ac_dc = 0.95 , dc_ac = 0.95):
        self.ac_dc_efficiency = ac_dc
        self.dc_ac_efficiency = dc_ac
        self.result = {}
    def show(self):
        return {"交流-直流转化效率":self.ac_dc_efficiency,
                "直流-交流转化效率":self.dc_ac_efficiency}

