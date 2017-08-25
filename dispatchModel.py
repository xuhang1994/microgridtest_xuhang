"""
Created on Wed Jun 21 12:25:40 2017

@author: Master Shi
"""
from pulp import *
from microgrid import *
import pandas as pd
import json
import math
import copy
import numpy

##This is ShiYunHui's first try of Github, hello!
def define_variables(pv1,es1,absc1,bol1,cs1,ac1,gt1,ut,inv):
    global power_es1_into, power_es1_outof, energy_es1, power_absc1, power_bol1, power_cs1, coldintotank, coldoutoftank, power_ac1, power_gte1, om_es1, om_absc1, om_bol1, om_cs1, om_ac1, om_gte1, power_utility, dc, z_pwut, det_pwut_l, det_pwut_u, aux_pwst, det_ice, z_acdc, det_acdc, det_es, hourly_cost, low_heat, medium_heat, high_heat, Q_ref, S_ice, i, bigM
    power_es1_into = list()
    power_es1_outof = list()
    energy_es1 = list()
    power_absc1 = list()
    power_bol1 = list()
    # power_hs1 = list()
    # energy_hs1 = list()
    power_cs1 = list()
    coldintotank = list()
    coldoutoftank = list()
    power_ac1 = list()
    power_gte1 = list()
    om_es1 = list()
    om_absc1 = list()
    om_bol1 = list()
    # om_hs1 = list()
    om_cs1 = list()
    om_ac1 = list()
    om_gte1 = list()
    power_utility = list()
    dc = list()
    z_pwut = list()
    det_pwut_l = list()
    det_pwut_u = list()
    aux_pwst = list()  ##convex
    det_ice = list()
    z_acdc = list()
    det_acdc = list()
    det_es = list()
    hourly_cost = list()
    low_heat = list()
    medium_heat = list()
    high_heat = list()
    Q_ref = list()
    S_ice = list()
    for i in range(96):
        # Regular variables
        energy_es1.append(LpVariable('energyStoredinBattery_' + str(i)))
        power_absc1.append(LpVariable('absorptionChiller1Power_' + str(i), absc1.Hmin, absc1.Hmax))  ##
        power_bol1.append(LpVariable('boiler1Power_' + str(i), bol1.Pmin, bol1.Pmax))  ##
        #    power_hs1.append(LpVariable('heatStorage1Power_'+str(i),hs1.Hmin,hs1.Hmax))  ##
        #    energy_hs1.append(LpVariable('EnergyinHeatStorage_'+ str(i)))
        power_cs1.append(LpVariable('coldStorage1Power_' + str(i), 0, cs1.Pmax))  ##
        power_ac1.append(LpVariable('airConditionerPower_' + str(i), 0, ac1.Pmax))  ##
        power_gte1.append(LpVariable('gasTurbineElectricalPower_' + str(i), gt1.Pmin, gt1.Pmax))  ##
        power_utility.append(LpVariable('utilityPower_' + str(i)))  ##
        dc.append(LpVariable('DCnetload_' + str(i)))  ## AC-DC when >0, DC-AC when <0
        low_heat.append(LpVariable('low_heat_' + str(i), lowBound=0))
        medium_heat.append(LpVariable('medium_heat_' + str(i), lowBound=0))
        high_heat.append(LpVariable('high_heat_' + str(i), lowBound=0))
        Q_ref.append(LpVariable('Q_ref_' + str(i), lowBound=0))
        S_ice.append(LpVariable('S_ice_' + str(i), cs1.Tmin * cs1.capacity, cs1.Tmax * cs1.capacity))

        # OM variables
        om_es1.append(LpVariable('OMes_' + str(i)))
        om_absc1.append(LpVariable('OMabsc_' + str(i)))
        om_bol1.append(LpVariable('OMbol_' + str(i)))
        # om_hs1.append(LpVariable('OMhs_'+str(i)))
        om_cs1.append(LpVariable('OMcs_' + str(i)))
        om_ac1.append(LpVariable('OMac_' + str(i)))
        om_gte1.append(LpVariable('OMgte_' + str(i)))
        # deal with piecewise linear function
        '''of Utility power sell/buy price difference'''
        z_pwut.append(LpVariable('utilityAuxPower_' + str(i)))  ##
        det_pwut_l.append(LpVariable('utilityAuxPowerLowerBound_' + str(i), cat=LpBinary))
        det_pwut_u.append(LpVariable('utilityAuxPowerUpperBound_' + str(i), cat=LpBinary))

        '''of depreciation cost '''
        aux_pwst.append(LpVariable('electricStorageAuxiliaryVariable_' + str(i), lowBound=0))  ##

        '''of cold storage input/output efficiency difference in equality constraints '''
        det_ice.append(LpVariable('iceSign' + str(i), cat=LpBinary))
        coldintotank.append(LpVariable('coldintotank_' + str(i), lowBound=0, upBound=cs1.Hin))
        coldoutoftank.append(LpVariable('coldoutoftank_' + str(i), lowBound=0, upBound=cs1.Hout))
        '''of DC/AC and AC/DC conversion efficiency difference'''
        z_acdc.append(LpVariable('ACDC_' + str(i)))
        det_acdc.append((LpVariable('acdcSign' + str(i), cat=LpBinary)))
        '''of electrical storage'''
        det_es.append(LpVariable('det_es_' + str(i), cat=LpBinary))
        power_es1_into.append(LpVariable('electricStorage1Powerinto_' + str(i), 0, es1.Pmax))
        power_es1_outof.append(LpVariable('electricStorage1Poweroutof_' + str(i), 0, - es1.Pmin))
        '''of hourly cost'''
        hourly_cost.append(LpVariable('hourly_cost_' + str(i)))
    bigM = 10000000
def define_Constraints(optimalDispatch,pv1,es1,absc1,bol1,cs1,ac1,gt1,ut,inv):

    '''Hourly Cost'''
    for i in range(96):
        optimalDispatch += hourly_cost[i] == om_es1[i] + om_absc1[i] + om_cs1[i] + om_bol1[i] + om_ac1[i] + 0.25 * \
                                                                                                            ut.buy_price[
                                                                                                                i] * \
                                                                                                            power_utility[
                                                                                                                i] + \
                                             om_gte1[i] + aux_pwst[i] + (power_gte1[i] * (1 / gt1.efficiency) +
                                                                         power_bol1[i] * (
                                                                         1 / bol1.efficiency)) * 0.25 * ut.gas_price + \
                                             high_heat[i] * ut.steam_price * 0.25  # + om_hs1[i]
    '''of Electricity'''
    es1selfrelease = [math.pow((1 - es1.selfRelease), 95 - i) for i in range(96)]
    for i in range(96):
        ## ac power balance
        #optimalDispatch += power_utility[i] + power_gte1[i] == acload[i] + z_acdc[i] + power_ac1[i] + power_cs1[
            #i] + 0.025 * (ac1.EER + 1) * power_ac1[i]
        ## dc power balance
        #optimalDispatch += dc[i] + pv1.output[i] + power_es1_outof[i] == dcload[i] + power_es1_into[i]
        optimalDispatch += power_utility[i] + power_gte1[i] + pv1.output[i] + power_es1_outof[i] == acload[i] + power_ac1[i] + power_cs1[
            i] + power_es1_into[i]
        ## MAX-MIN power bound constraints already represented in LpVariables
        ## Electrical Storage capacity constraint
        if i == 0:
            optimalDispatch += energy_es1[i] == es1.SOCint * es1.capacity
        else:
            optimalDispatch += energy_es1[i] == energy_es1[i - 1] * (1 - es1.selfRelease) + 0.25 * (
            es1.efficiency * power_es1_into[i] - (1 / es1.efficiency) * power_es1_outof[i])

        optimalDispatch += energy_es1[i] <= es1.SOCmax * es1.capacity
        optimalDispatch += energy_es1[i] >= es1.SOCmin * es1.capacity
        ## Electrical Storage power changing rate constraint
        if i >= 1:
            optimalDispatch += power_es1_into[i] - power_es1_into[i - 1] >= -es1.maxDetP
            optimalDispatch += power_es1_into[i] - power_es1_into[i - 1] <= es1.maxDetP
            optimalDispatch += power_es1_outof[i] - power_es1_outof[i - 1] >= -es1.maxDetP
            optimalDispatch += power_es1_outof[i] - power_es1_outof[i - 1] <= es1.maxDetP

        #if i in range(88, 95):
            #optimalDispatch += power_es1_outof[i] == 0

    ## Electrical Storage Zero constraint
    # optimalDispatch += energy_es1[0] == energy_es1[95]
    optimalDispatch += energy_es1[0] == energy_es1[95] * (1 - es1.selfRelease) + 0.25 * (
    es1.efficiency * power_es1_into[0] - (1 / es1.efficiency) * power_es1_outof[0])
    '''of Heat'''
    for i in range(96):
        ## heat balance
        ##optimalDispatch += high_heat[i] + power_bol1[i] + gt1.HER * gt1.heat_recycle * power_gte1[i] == power_absc1[i] + steam_heat[i] + water_heat[i]
        optimalDispatch += high_heat[i] + power_bol1[i] >= steam_heat[i]
        optimalDispatch += medium_heat[i] == 0.3 * steam_heat[i] + power_gte1[i] * gt1.HER * gt1.heat_recycle
        optimalDispatch += high_heat[i] + power_bol1[i] - steam_heat[i] + medium_heat[i] >= power_absc1[i]
        optimalDispatch += medium_heat[i] >= power_absc1[i]
        optimalDispatch += low_heat[i] == 0.1 * steam_heat[i] + power_gte1[i] * gt1.HER * gt1.heat_recycle * 0.3
        optimalDispatch += medium_heat[i] - (power_absc1[i] - high_heat[i] - power_bol1[i] + steam_heat[i]) + low_heat[
            i] >= water_heat[i]  # + power_hs1[i]
        '''
        ## heat storage capacity constraint
        if i == 0:
            optimalDispatch += energy_hs1[i] == hs1.Tint * hs1.capacity
        else:
            optimalDispatch += energy_hs1[i] == energy_hs1[i-1] * (1 - hs1.selfRelease) + 0.25 * power_hs1[i]

        optimalDispatch += energy_hs1[i] <= hs1.Tmax* hs1.capacity
        optimalDispatch += energy_hs1[i] >= hs1.Tmin* hs1.capacity
        ## Heat Storage power changing rate constraint
        if i >= 1:
            optimalDispatch += power_hs1[i] - power_hs1[i - 1] >= -hs1.maxDetP
            optimalDispatch += power_hs1[i] - power_hs1[i - 1] <= hs1.maxDetP
        ## heatStorage Zero constraint
    optimalDispatch += energy_hs1[0] == energy_hs1[95]
    '''
    '''of Cold'''
    for i in range(96):
        ## cold balance
        optimalDispatch += power_absc1[i] * absc1.COP_htc + coldoutoftank[i] + power_ac1[i] * ac1.EER + Q_ref[i] == \
                           cold_load[i]
        optimalDispatch += power_cs1[i] * cs1.EER - coldintotank[i] == Q_ref[i]
        if cs1.mode == '串联':
            optimalDispatch += Q_ref[i] >= cs1.Partition_out * coldoutoftank[i] - bigM * (1 - det_ice[i]) - 0.001
            optimalDispatch += Q_ref[i] <= cs1.Partition_out * coldoutoftank[i] + bigM * (1 - det_ice[i]) + 0.001
            optimalDispatch += Q_ref[i] >= cs1.Partition_in * coldintotank[i] - bigM * det_ice[i] - 0.001
            optimalDispatch += Q_ref[i] <= cs1.Partition_in * coldintotank[i] + bigM * det_ice[i] + 0.001
        ## cold storage capacity constraint
        if i == 0:
            optimalDispatch += coldintotank[i] >= - cs1.maxdetP
            optimalDispatch += coldintotank[i] <= cs1.maxdetP
            optimalDispatch += S_ice[i] == cs1.capacity * cs1.Tint

        if i >= 1:
            optimalDispatch += (coldoutoftank[i] - coldintotank[i]) - (
            coldoutoftank[i - 1] - coldintotank[i - 1]) >= - cs1.maxdetP
            optimalDispatch += (coldoutoftank[i] - coldintotank[i]) - (
            coldoutoftank[i - 1] - coldintotank[i - 1]) <= cs1.maxdetP
            optimalDispatch += S_ice[i] == S_ice[i - 1] * (1 - cs1.self_release) + 0.25 * (
            coldintotank[i] - coldoutoftank[i])
        ## cold storge zero constraint
        optimalDispatch += S_ice[i] <= cs1.Tmax * cs1.capacity
        optimalDispatch += S_ice[i] >= cs1.Tmin * cs1.capacity
    # optimalDispatch += S_ice[0] == S_ice[95]
    optimalDispatch += S_ice[0] == S_ice[95] * (1 - cs1.self_release) + 0.25 * (coldintotank[0] - coldoutoftank[0])
    '''of OM cost'''
    for i in range(96):
        optimalDispatch += om_es1[i] >= 0.25 * (power_es1_into[i]) * es1.om
        optimalDispatch += om_es1[i] >= -0.25 * (power_es1_into[i]) * es1.om
        optimalDispatch += om_absc1[i] >= 0.25 * power_absc1[i] * absc1.om
        optimalDispatch += om_absc1[i] >= -0.25 * power_absc1[i] * absc1.om
        optimalDispatch += om_bol1[i] >= 0.25 * power_bol1[i] * bol1.om
        optimalDispatch += om_bol1[i] >= -0.25 * power_bol1[i] * bol1.om
        #    optimalDispatch += om_hs1[i] >= 0.25 *power_hs1[i] * hs1.om
        #    optimalDispatch += om_hs1[i] >= -0.25 *power_hs1[i] * hs1.om
        optimalDispatch += om_cs1[i] >= 0.25 * power_cs1[i] * cs1.om
        optimalDispatch += om_cs1[i] >= -0.25 * power_cs1[i] * cs1.om
        optimalDispatch += om_ac1[i] >= 0.25 * power_ac1[i] * ac1.om
        optimalDispatch += om_ac1[i] >= -0.25 * power_ac1[i] * ac1.om
        optimalDispatch += om_gte1[i] >= 0.25 * power_gte1[i] * gt1.om
        optimalDispatch += om_gte1[i] >= -0.25 * power_gte1[i] * gt1.om
    '''of auxuliary variables'''
    for i in range(96):
        ## Utility power sell/buy price difference
        optimalDispatch += det_pwut_l[i] + det_pwut_u[i] == 1
        optimalDispatch += power_utility[i] >= 0 - 10 * bigM * (1 - det_pwut_u[i])
        optimalDispatch += power_utility[i] >= - bigM - 10 * bigM * (1 - det_pwut_l[i])
        optimalDispatch += power_utility[i] <= bigM + 10 * bigM * (1 - det_pwut_u[i])
        optimalDispatch += power_utility[i] <= 0 + 10 * bigM * (1 - det_pwut_l[i])
        optimalDispatch += z_pwut[i] >= 0.25 * ut.buy_price[i] * power_utility[i] - bigM * (1 - det_pwut_u[i])
        optimalDispatch += z_pwut[i] >= - 0.25 * ut.sell_price * power_utility[i] - bigM * (1 - det_pwut_l[i])

        ##depreciation cost
        optimalDispatch += aux_pwst[i] >= 0.25 * es1.Cbw * power_es1_outof[i]

        ##Cold Storage SOS1 constraint
        optimalDispatch += coldintotank[i] <= (1 - det_ice[i]) * bigM + 0.001
        optimalDispatch += coldoutoftank[i] <= det_ice[i] * bigM + 0.001

        ##Eletrical Storage SOS1 constraint
        optimalDispatch += power_es1_outof[i] <= (1 - det_es[i]) * bigM + 0.01
        optimalDispatch += power_es1_into[i] <= det_es[i] * bigM + 0.01
        '''
        ##dc-ac det_acdc = 1 if dc < 0
        optimalDispatch += dc[i] + bigM * det_acdc[i] >= 0
        optimalDispatch += dc[i] <= bigM * (1 - det_acdc[i])
        optimalDispatch += z_acdc[i] - dc[i] * inv.dc_ac_efficiency <= bigM * (1 - det_acdc[i]) + 0.001
        optimalDispatch += z_acdc[i] - dc[i] * inv.dc_ac_efficiency >= -bigM * (1 - det_acdc[i]) - 0.001
        optimalDispatch += inv.ac_dc_efficiency * z_acdc[i] - dc[i] <= bigM * det_acdc[i] + 0.001
        optimalDispatch += inv.ac_dc_efficiency * z_acdc[i] - dc[i] >= -bigM * det_acdc[i] - 0.001
        '''
    return optimalDispatch
'''Constrcut the microgrid devices and utility prices'''
pv1 = PV()
es1 = electricStorage()
absc1 = absorptionChiller()
bol1 = boiler()
#hs1 = heatStorage()
cs1 = coldStorage()
ac1 = airConditioner()
gt1 = gasTurbine()
ut = utility()
inv = inverter()
'''save the parameters'''
parameters = {"光伏":pv1.show(),
             "储能电池":es1.show(),
             "吸收式制冷机":absc1.show(),
             "辅助锅炉":bol1.show(),
#             "储热装置":hs1.show(),
             "冰蓄冷装置":cs1.show(),
             "中央空调":ac1.show(),
             "燃气轮机":gt1.show(),
             "变流器":inv.show(),
             "燃气价格等":ut.show()}
with open('parameters.json','w',encoding='UTF-8') as f:
    json.dump(parameters,f)

'''DATA LOADER'''
microgrid_data = pd.read_excel('input.xlsx')
acload = microgrid_data['交流负荷'].tolist()
dcload = microgrid_data['直流负荷'].tolist()
pv1.output = microgrid_data['光伏出力'].tolist()
ut.buy_price = microgrid_data['电价'].tolist()
cold_load = microgrid_data['冷负荷'].tolist()
water_heat = microgrid_data['热水负荷'].tolist()
steam_heat = microgrid_data['蒸汽负荷'].tolist()

'''Construct the OptimalDispatch linear programming model'''
optimalDispatch = LpProblem('optimalDisaptch',LpMinimize)

'''Define the variables'''
define_variables(pv1,es1,absc1,bol1,cs1,ac1,gt1,ut,inv)

'''Define the objectives'''
optimalDispatch += lpSum(om_es1) \
    + lpSum(om_absc1) \
    + lpSum(om_bol1) \
    + lpSum(om_cs1) \
    + lpSum(om_ac1) \
    + lpSum(om_gte1) \
    + lpSum(z_pwut) \
    + lpSum(aux_pwst) \
    + lpSum(power_gte1)*(ut.gas_price*0.25/gt1.efficiency) \
    + lpSum(power_bol1)*(ut.gas_price*0.25/bol1.efficiency) \
    + lpSum(high_heat)*(ut.steam_price*0.25)
    #+ lpSum(om_hs1)

'''Define the constraints'''
optimalDispatch = define_Constraints(optimalDispatch,pv1,es1,absc1,bol1,cs1,ac1,gt1,ut,inv)

'''Take a beer and wait for the result ready in the bed'''
optimalDispatch.solve(CPLEX_CMD(msg=1,mip=1))
es1.power_into = pd.Series([x.varValue for x in power_es1_into])
es1.power_outof = pd.Series([x.varValue for x in power_es1_outof])
es1.energy = pd.Series([x.varValue for x in energy_es1])
absc1.result = pd.Series([x.varValue for x in power_absc1])
bol1.result = pd.Series([x.varValue for x in power_bol1])
#hs1.result = pd.Series([x.varValue for x in  power_hs1])
#hs1.energy = pd.Series([x.varValue for x in  energy_hs1])
cs1.result_electricity = pd.Series([x.varValue for x in power_cs1])
cs1.result_cold = pd.Series([x.varValue for x in coldoutoftank]) + pd.Series([x.varValue for x in power_cs1])*cs1.EER - pd.Series([x.varValue for x in coldintotank])
cs1.result_stored = pd.Series([x.varValue for x in coldintotank]) - pd.Series([x.varValue for x in coldoutoftank])
cs1.ref = pd.Series([x.varValue for x in Q_ref]) / cs1.COP
ac1.result = pd.Series([x.varValue for x in power_ac1])
gt1.result = pd.Series([x.varValue for x in power_gte1])
ut.result = pd.Series([x.varValue for x in power_utility])
inv.result = pd.Series([x.varValue for x in dc])
ut.gas_utility = bol1.result / bol1.efficiency + gt1.result / gt1.efficiency
desiredpower = copy.deepcopy(ut.result)

om_cost = pd.Series([x.varValue for x in om_ac1])+pd.Series([x.varValue for x in om_cs1])+pd.Series([x.varValue for x in om_absc1])+ \
          pd.Series([x.varValue for x in om_bol1])+pd.Series([x.varValue for x in om_es1])+pd.Series([x.varValue for x in om_gte1]) # + pd.Series([x.varValue for x in om_hs1])
heat_cost = pd.Series([x.varValue for x in high_heat]) * ut.steam_price * 0.25

dep_cost = pd.Series([x.varValue for x in aux_pwst])
electricity_cost = 0.25 * pd.Series([x.varValue for x in power_utility]) * pd.Series(ut.buy_price)
fuel_cost = pd.Series([x.varValue for x in hourly_cost]) - om_cost - dep_cost - electricity_cost
for i in range(72,76):
    desiredpower[i] = desiredpower[i] - 3000
print(sum([x.varValue for x in hourly_cost]))
df= pd.DataFrame()
df['电网购电功率'] = ut.result
df['蒸汽购买量(单位：t)'] = pd.Series([x.varValue for x in high_heat]) / 996
df['天然气购买量（单位：立方米）'] = ut.gas_utility * 0.25 * 3600 / 35885
df['中品位热功率'] = pd.Series([x.varValue for x in medium_heat])
df['低品位热功率'] = pd.Series([x.varValue for x in low_heat])
df['电储能充电功率'] = es1.power_into
df['电储能放电功率'] = es1.power_outof
df['电储能电能'] = es1.energy
df['燃气轮机发电功率'] = gt1.result
df['空调制冷耗电功率'] = ac1.result
df['空调制冷功率'] = ac1.result*ac1.EER
df['冰蓄冷制冷机直接供冷耗电功率'] = cs1.ref
df['冰蓄冷供冷功率'] = cs1.result_cold
df['冰蓄冷耗电功率'] = cs1.result_electricity
df['冰蓄冷储冷功率'] = cs1.result_stored
df['冰蓄冷储冷量'] = pd.Series([x.varValue for x in S_ice])
df['吸收式制冷机制冷功率'] = absc1.result * absc1.COP_htc
df['余热锅炉中品位热功率'] = gt1.result*gt1.HER*gt1.heat_recycle
df['燃气锅炉高品位热功率'] = bol1.result
#df['热储能功率'] = hs1.result
#df['热储能吸收或释放的能量'] = hs1.result * 0.25
#df['热储能热量'] = hs1.energy
df['电价'] = pd.Series(ut.buy_price)
df['期望功率'] = desiredpower
df['总费用'] = pd.Series([x.varValue for x in hourly_cost])
df['电费'] = electricity_cost
df['热费'] = heat_cost
df['气费'] = fuel_cost
df['运维费用'] = om_cost
df['折旧费用'] = dep_cost
df.to_excel('output.xlsx')