#!/usr/bin/python3

import numpy as np
import warnings

#import netCDF4 
from netCDF4 import Dataset

#wrf python package
import wrf

import pandas as pd

import math
import os
import datetime
from datetime import date, timedelta
import sys

#sql
import sqlite3
#import sqlite3 as sql

#----------------------------------------------------------------------------------------------------------------------------------------

def head(fd_out,username,password,city):
    """   
    [general settings]

    #url       =  https://www.wetterturnier.de/autosubmit/
    url       = http://85.214.230.47/autosubmit/
    logfile   =  autosubmit_%%city%%_%%user%%_%%tdate%%.log
    user      = MOrtuS
    password  = cb99
    city      =  BER
    #tdate     =  2022-08-12
    
    [parameters]
    """
    wt_url = "http://85.214.230.47/autosubmit/" #"https://www.wetterturnier.de/autosubmit/"
    fd_out.write("[general settings]\n\n")
    fd_out.write("url       =  {}\nlogfile   =  autosubmit_%%city%%_%%user%%.txt\n".format(wt_url))
    fd_out.write("user      =  {}\npassword  =  {}\ncity      =  {}\n\n[parameters]\n\n\n".format(username,password,city))

def write_bet(fd_out,parameter,dict_bet):
    day=0
    for par in parameter:
        fd_out.write("{}_{}={}\n".format(par,day+1,dict_bet[par][day]) )
    fd_out.write("\n\n")
    day=1
    for par in parameter:
        print
        fd_out.write("{}_{}={}\n".format(par,day+1,dict_bet[par][day]) )
    fd_out.close()

def theta(p, t, p2=1000.):
    '''
    Returns the potential temperature (C) of a parcel.
    Parameters
    ----------
    p : number, numpy array
        The pressure of the parcel (hPa)
    t : number, numpy array
        Temperature of the parcel (K)
    p2 : number, numpy array (default 1000.)
        Reference pressure level (hPa)
    Returns
    -------
    Potential temperature (K)
    '''
    ROCP = 0.28571426       # R over Cp
    return ((t) * np.power((p2 / p),ROCP))

def thetae(p,t,q,p2=1000.):
    """
    Calculates the equlivalent potential temperature (K) for the given parcel
    Parameters
    ----------
    p : number
        Pressure of parcel (hPa)
    t : number
        Temperature of parcel (K)
    q : number
        specific humidity (kg/kg)
    Returns
    -------
    qulivalent potential temperature (K)
    """
    ROCP = 0.28571426       # R over Cp
    return ((t)+((2.501*1000000)/1004)*q)* np.power((p2/p),ROCP)
    
    
def barometrischehoehenformel(h,ps,T):

    M=0.02896 #kg/mol
    g=9.807 #m/s2
    R=8.314 #J/K 1/mol
    
    #hs=M*g/R*T
    #dh=h
    #return ps*np.exp(-hs*dh)
    dh=h*(-1)
    a = - 0.562/100 #K/m
    return ps*np.power(1 - (a*dh)/(T),(M*g)/(R*a))

#barometrischehoehenformel(hsurf,ps,T)


def maxsun(todaydate):
    df = pd.read_table("./astral.txt",sep=";")
    
    sadate = todaydate+timedelta(days=1)
    sodate = todaydate+timedelta(days=2)
    
    df2 = df[df['month'] == int(sadate.strftime('%m'))]
    kp = df2[df2['day'] == int(sadate.strftime('%d'))]
    
    sunsah = float(kp["10381"])
    
    df2 = df[df['month'] == int(sodate.strftime('%m'))]
    kp = df2[df2['day'] == int(sodate.strftime('%d'))]
    
    sunsoh = float(kp["10381"])
    
    return sunsah,sunsoh
#----------------------------------------------------------------------------------------------------------------------------------------


##########################################################################

#today date
todaydate = date.today()

#icon
path_icon_archiv = "/daten/model/work/ingokir/devel-pure/dwd-data/icon-eu/{}00/".format(todaydate.strftime("%Y%m%d"))
icon_file="icon-eu_europe_regular_preproc4LE_{}00_000_allvars.nc".format(todaydate.strftime("%Y%m%d"))


#icon meta data
south_lim = 300
north_lim = 400
west_lim = 500
east_lim = 700


with Dataset(path_icon_archiv+icon_file, 'r') as data_all :
    hsurf = data_all["HSURF"][0,south_lim:north_lim,west_lim:east_lim]
    hhl   = data_all["HHL"][0,:,south_lim:north_lim,west_lim:east_lim]
    lat = data_all["lat"][south_lim:north_lim]
    lon = data_all["lon"][west_lim:east_lim]

h_agl = hhl[:,:,:]-hsurf[:,:]


#dahlem coordinates
lon_cor = 592
lat_cor = 370
loc = 10381


with Dataset(path_icon_archiv+icon_file, 'r') as data_all :
    hsurf = data_all["HSURF"][0,lat_cor,lon_cor]
    hhl   = data_all["HHL"][0,:,lat_cor,lon_cor]

h_agl = hhl[:]-hsurf
print(hsurf)
print(h_agl[1])


#paths
path_script = "/home/mammatus95/Dokumente/Programmierung/dahlem_mos/wt"

os.chdir(path_script)

print(os.getcwd())


day_exist=os.path.exists(path_icon_archiv+icon_file)
    
if day_exist == False:
    print("missing ")
    #start_date += delta
    #continue
    
#CLC P QC QI QV T U V W ALHFL_S ASHFL_S ASOB_S ASWDIR_S CAPE_ML CLCH CLCL CLCM CLCT H_SNOW MH PS RAIN_CON RAIN_GSP RELHUM_2M TD_2M TOT_PREC T_2M U_10M V_10M Z0 SOILM1 SOILM2 SOILM3 SOILM4 FR_LAND HHL HSURF SOILTYP

#CLC P QV T U V W ALHFL_S ASHFL_S ASOB_S ASWDIR_S CLCH CLCL CLCM CLCT H_SNOW MH PS RAIN_CON RAIN_GSP RELHUM_2M TD_2M TOT_PREC T_2M U_10M V_10M Z0 SOILM1 SOILM2 SOILM3 SOILM4 FR_LAND HHL HSURF SOILTYP


con = sqlite3.connect('dahlem.db')
cursor = con.cursor()
loc="10381"
debug_flag = False
#wt names
pds=['t_2m','sd1h','td_2m','Tx1h','Tn1h','fx1h','rr1h','rr1hsqrt','rr1hlog','pmsl','uwind','vwind']
lt=78
result_dict={'t_2m':np.zeros(lt),
             'sd1h':np.zeros(lt),
             'td_2m':np.zeros(lt),
             'Tx1h':np.zeros(lt),
             'Tn1h':np.zeros(lt),
             'fx1h':np.zeros(lt),
             'rr1h':np.zeros(lt),
             'rr1hsqrt':np.zeros(lt),
             'rr1hlog':np.zeros(lt),
             'pmsl':np.zeros(lt),
             'uwind':np.zeros(lt),
             'vwind':np.zeros(lt)}

for fp in range(1,79):
    icon_file="icon-eu_europe_regular_preproc4LE_{}00_{:03d}_allvars.nc".format(todaydate.strftime("%Y%m%d"),fp)


    with Dataset(path_icon_archiv+icon_file, 'r') as data_all :
        vars_name=["CLCH","CLCL","CLCM","RAIN_CON","TOT_PREC","RAIN_GSP","T_2M","TD_2M","U_10M","V_10M"]
        multi_lvl=["U","V"]
        levels=["12","25"] #18 = 700 hPa


        icon_dict={}

        old_totprec=0.0
        old_totprec_con=0.0
        old_totprec_gsp=0.0
        for var in vars_name:
            if debug_flag == True:
                print(var)
            if var == "TOT_PREC":
                rr1h = float(data_all[var][0,lat_cor,lon_cor])-old_totprec
                icon_dict.update({f"{var.lower()}": rr1h})
                icon_dict.update({f"{var.lower()}sqrt": np.sqrt(rr1h)})
                icon_dict.update({f"{var.lower()}log": np.log(1+rr1h)})
            elif var == "RAIN_GSP":
                rr1h = float(data_all[var][0,lat_cor,lon_cor])-old_totprec_gsp
                icon_dict.update({f"{var.lower()}": rr1h})
                icon_dict.update({f"{var.lower()}sqrt": np.sqrt(rr1h)})
                icon_dict.update({f"{var.lower()}log": np.log(1+rr1h)})
            elif var == "RAIN_CON":
                rr1h = float(data_all[var][0,lat_cor,lon_cor])-old_totprec_con
                icon_dict.update({f"{var.lower()}": rr1h})
                icon_dict.update({f"{var.lower()}sqrt": np.sqrt(rr1h)})
                icon_dict.update({f"{var.lower()}log": np.log(1+rr1h)})
            else:
                icon_dict.update({f"{var.lower()}": float(data_all[var][0,lat_cor,lon_cor])})



        #pw
        pw_fld=np.sum(((data_all['QV'][0,:-1,lat_cor,lon_cor]+data_all['QV'][0,1:,lat_cor,lon_cor])/2 * (data_all['P'][0,:-1,lat_cor,lon_cor]-data_all['P'][0,1:,lat_cor,lon_cor])))*0.10203942
        icon_dict.update({"pw": pw_fld})

        #ko-index
        ko = thetae(data_all['P'][0,18,lat_cor,lon_cor]/100,data_all['T'][0,18,lat_cor,lon_cor],data_all['QV'][0,18,lat_cor,lon_cor],p2=1000.) #700
        ko+= thetae(data_all['P'][0,25,lat_cor,lon_cor]/100,data_all['T'][0,25,lat_cor,lon_cor],data_all['QV'][0,25,lat_cor,lon_cor],p2=1000.) #500
        ko-= thetae(data_all['P'][0,12,lat_cor,lon_cor]/100,data_all['T'][0,12,lat_cor,lon_cor],data_all['QV'][0,12,lat_cor,lon_cor],p2=1000.) #850
        ko-= thetae(data_all['P'][0,1,lat_cor,lon_cor]/100,data_all['T'][0,1,lat_cor,lon_cor],data_all['QV'][0,1,lat_cor,lon_cor],p2=1000.) #1000
        icon_dict.update({"ko": ko*0.5})

        #llaps
        llaps = theta(data_all['P'][0,8,lat_cor,lon_cor]/100,data_all['T'][0,8,lat_cor,lon_cor],p2=1000.) - theta(data_all['P'][0,1,lat_cor,lon_cor]/100,data_all['T'][0,1,lat_cor,lon_cor],p2=1000.)
        icon_dict.update({"llaps": llaps})

        #850pot
        pot850 = theta(data_all['P'][0,12,lat_cor,lon_cor]/100,data_all['T'][0,12,lat_cor,lon_cor],p2=data_all['PS'][0,lat_cor,lon_cor])
        icon_dict.update({"pot850": pot850})

        #pot925
        pot925 = theta(data_all['P'][0,8,lat_cor,lon_cor]/100,data_all['T'][0,8,lat_cor,lon_cor],p2=data_all['PS'][0,lat_cor,lon_cor])
        icon_dict.update({"pot925": pot925})

        #laps
        laps = theta(data_all['P'][0,21,lat_cor,lon_cor]/100,data_all['T'][0,21,lat_cor,lon_cor],p2=1000.) - theta(data_all['P'][0,14,lat_cor,lon_cor]/100,data_all['T'][0,14,lat_cor,lon_cor],p2=1000.)
        icon_dict.update({"laps": laps})

        #shr1
        du = data_all['U'][0,8,lat_cor,lon_cor] - data_all['U'][0,1,lat_cor,lon_cor]
        dv = data_all['V'][0,8,lat_cor,lon_cor] - data_all['V'][0,1,lat_cor,lon_cor]
        shr1 = np.sqrt(du*du+dv*dv)
        icon_dict.update({"shr1": shr1})

        #shr6
        du = data_all['U'][0,26,lat_cor,lon_cor] - data_all['U'][0,1,lat_cor,lon_cor]
        dv = data_all['V'][0,26,lat_cor,lon_cor] - data_all['V'][0,1,lat_cor,lon_cor]
        shr6 = np.sqrt(du*du+dv*dv)
        icon_dict.update({"shr6": shr6})

        #speed950
        du = data_all['U'][0,6,lat_cor,lon_cor]
        dv = data_all['V'][0,6,lat_cor,lon_cor]
        speed950 = np.sqrt(du*du+dv*dv)
        icon_dict.update({"speed950": speed950})

        #psred
        psred = barometrischehoehenformel(hsurf,data_all['PS'][0,lat_cor,lon_cor],data_all['T_2M'][0,lat_cor,lon_cor])
        icon_dict.update({"psred": psred/100})


        for lvl in levels:
            for var in multi_lvl:
                icon_dict.update({f"{var.lower()}_lvl{lvl}": float(data_all[var][0,int(lvl),lat_cor,lon_cor])})
    if debug_flag == True:
        print(fp,icon_dict)
        
        
    for pd_name in pds:

        cof_table=f"{pd_name}_all_2005_{loc}_cof"
    
          
        #get cofs
        exe_string=f"select Pr,coefficient from {cof_table} where location='{loc}' and Pd='{pd_name}' and fp='{fp}'"
        cursor.execute(exe_string)
        #print(exe_string)
        cof=cursor.fetchall()
        if debug_flag == True:
            print(cof)
        
        if cof[1][0] == "nosun":
            result_dict[pd_name][fp-1] = 0 
        else:
            result = cof[0][1]
            for idx in range(1,len(cof)):
                if debug_flag == True:
                    print(cof[idx][0])
                if cof[idx][0] == "y-intersect":
                    break


                result += icon_dict[cof[idx][0]]*cof[idx][1]

            result_dict[pd_name][fp-1] = result
        
print(result_dict)

max_sun_sa, max_sun_so = maxsun(todaydate)

#bet dictionary
dict_bet = {}
idxsa=35
idxso=59


par='ff12'
ff_sa = round(np.sqrt(result_dict['uwind'][idxsa]*result_dict['uwind'][idxsa] + result_dict['vwind'][idxsa]*result_dict['vwind'][idxsa]),1)
ff_so = round(np.sqrt(result_dict['uwind'][idxso]*result_dict['uwind'][idxso] + result_dict['vwind'][idxso]*result_dict['vwind'][idxso]),1)

dict_bet.update( {par : [ff_sa,ff_so]} )

par='dd12'
val = 180 / np.pi
dd_sa = np.arctan2(-result_dict['uwind'][idx],-result_dict['vwind'][idx]) * val
if dd_sa < 0:
    dd_sa += 360
dd_sa = round(direction/10)*10

dict_bet.update( {par : [dd_sa,dd_so]} )


par='PPP12'
pp_sa = round(result_dict['pmsl'][idxsa],1)
pp_so = round(result_dict['pmsl'][idxso],1)

dict_bet.update( {par : [pp_sa,pp_so]} )


par='Td12'
t_sa = round(result_dict['td_2m'][idxsa]-273.15,1)
t_so = round(result_dict['td_2m'][idxso]-273.15,1)
dict_bet.update( {par : [t_sa,t_so]} )

par='T12'
t_sa = round(result_dict['t_2m'][idxsa]-273.15,1)
t_so = round(result_dict['t_2m'][idxso]-273.15,1)
dict_bet.update( {par : [t_sa,t_so]} )


par='Sd1'
sd_sa = round(result_dict['sd1h'][idxsa])
sd_so = round(result_dict['sd1h'][idxso])

if sd_sa < 0.0:
    sd_sa =0.0
if sd_so < 0.0:
    sd_so =0.0

if sd_sa > 60.0:
    sd_sa = 60.0
if sd_so > 60.0:
    sd_so =60.0
dict_bet.update( {par : [sd_sa,sd_so]} )

par='Sd24'
sd_sa = round((np.sum(result_dict['sd1h'][idxsa-12:idxsa+12])/60)/max_sun_sa)
sd_so = round((np.sum(result_dict['sd1h'][idxso-12:idxso+12])/60)/max_sun_so)

if sd_sa < 0.0:
    sd_sa =0.0
if sd_so < 0.0:
    sd_so =0.0

if sd_sa > 99.0:
    sd_sa = 98.0
if sd_so > 99.0:
    sd_so =98.0

dict_bet.update( {par : [sd_sa,sd_so]} )
par='RR24'
rr_sa = round(np.sum(np.exp(result_dict['rr1h'][idxsa-12:idxsa+12])-1),1)
rr_so = round(np.sum(np.exp(result_dict['rr1h'][idxso-12:idxso+12])-1),1)

if rr_sa < 0.0:
    rr_sa =0.0
if rr_so < 0.0:
    rr_so =0.0

dict_bet.update( {par : [rr_sa,rr_so]} )
par='RR1'
rr_sa = round(np.max(np.exp(result_dict['rr1h'][idxsa-12:idxsa+12])-1),1)
rr_so = round(np.max(np.exp(result_dict['rr1h'][idxso-12:idxso+12])-1),1)

if rr_sa < 0.0:
    rr_sa =0.0
if rr_so < 0.0:
    rr_so =0.0
dict_bet.update( {par : [rr_sa,rr_so]} )

par='fx24'
fx_sa = round(np.max(result_dict['fx1h'][idxsa-12:idxsa+12]),1)
fx_sa = round(np.max(result_dict['fx1h'][idxso-12:idxso+12]),1)
if fx_sa < 0.2:
    fx_sa =0.2
if fx_so < 0.2:
    fx_so =0.2
dict_bet.update( {par : [fx_sa,fx_so]} )


par='Tmax'
t_sa = round(np.max(result_dict['Tx1h'][idxsa-6:idxsa+6])-273.15,1)
t_so = round(np.max(result_dict['Tx1h'][idxso-6:idxso+6])-273.15,1)
dict_bet.update( {par : [t_sa,t_so]} )

par='Tmin'
idxx=idxso-12
t_sa = round(np.min(result_dict['Tn1h'][idxx-6:idxx+6])-273.15,1)
idxx=idxsa-12
t_so = round(np.min(result_dict['Tn1h'][idxx-6:idxx+6])-273.15,1)
dict_bet.update( {par : [t_sa,t_so]} )


print(dict_bet)
par_list=['Sd1', 'Sd24', 'dd12', 'ff12', 'PPP12', 'Tmax', 'Tmin', 'Td12','T12','RR1','fx24','RR24']
fd = open("Berlin.txt", "w")
head(fd,"MOrtuS","cb99","BER")
write_bet(fd,par_list,dict_bet)
fd.close()
