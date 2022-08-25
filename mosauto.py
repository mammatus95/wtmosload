import pandas as pd
import numpy as np
import sys
import datetime
import random

#Funktionen

def stat_out(df_day):#,player):
    print('Value  Mean   Std   Var    Max    Min\n---------------------------------------')
    par_list=['Sd1', 'Sd24', 'dd12', 'ff12', 'PPP12', 'Tmax', 'Tmin', 'Td12','T12','RR1','fx24','RR24']
    for par in par_list:
        print('  %3s %6.1f %4.1f %5.1f %6.1f %6.1f' %(par,df_day[par].mean(),df_day[par].std(),df_day[par].var(),df_day[par].max(),df_day[par].min() ))


def calc_bet (df_sat,df_son,mos1='DWD-MOS-Mix',mos2='MSwr-MOS-Mix',player=0):
    dict_bet ={}
    par_list=['Sd1', 'Sd24', 'dd12', 'ff12', 'fx24', 'PPP12', 'Tmax', 'Tmin', 'Td12', 'RR24','RR1','T12']
    for par in par_list:
        if par == 'PPP12' or par == 'Tmax' or par ==  'Tmin' or par == 'Td12' or \
           par == 'T12' or par == 'ff12' or par == 'fx24':
            if player==0:
                value_sa = (df_sat[par][mos1] + df_sat[par][mos2])/2.0
                value_so = (df_son[par][mos1] + df_son[par][mos2])/2.0
            elif player==1:
                value_sa = (df_sat[par][mos1] + df_sat[par][mos2])/2.0
                value_so = (df_son[par][mos1] + df_son[par].mean())/2.0
            elif player==3:
                value_sa = df_sat[par].mean()
                value_so = df_son[par].mean()
                if random.randint(0, 1) == 0:
                    value_sa -= df_sat[par].std()
                    value_so -= df_son[par].std()
                else:
                    value_sa += df_sat[par].std()
                    value_so += df_son[par].std()
            elif player==10 or player==2:
                value_sa = (df_sat[par][mos1] + df_sat[par][mos2])/2.0
                value_so = (df_son[par][mos1] + df_son[par][mos2])/2.0
                if random.randint(0, 1) == 0:
                    value_sa -= df_sat[par].std()
                    value_so -= df_son[par].std()
                else:
                    value_sa += df_sat[par].std()
                    value_so += df_son[par].std()
            else:
                value_sa = (df_sat[par][mos1] + df_sat[par][mos2])/2.0
                value_so = (df_son[par][mos1] + df_son[par][mos2])/2.0
            dict_bet.update( {par : [round(value_sa,1),round(value_so,1)]} )
                                     
            
            
        elif par == 'Sd24' or par == 'Sd1':
            Sd_Sa = round((df_sat[par][mos1] + df_sat[par][mos2])/2.0)
            Sd_So = round((df_son[par][mos1] + df_son[par][mos2])/2.0)
            
            if par == 'Sd24':
                if Sd_Sa > 97:
                    Sd_Sa = 96
                if Sd_So > 97:
                    Sd_So = 96
                if Sd_Sa < 0:
                    Sd_Sa = 0
                if Sd_So < 0:
                    Sd_So = 0
            
            if par == 'Sd1':
                if Sd_Sa < 0:
                    Sd_Sa = 0
                if Sd_So < 0:
                    Sd_So = 0
                if Sd_Sa > 60:
                    Sd_Sa = 60
                if Sd_So > 60:
                    Sd_So = 60
            dict_bet.update( {par : [Sd_Sa,Sd_So]} )
            
        elif par == 'RR24':
            rr_sa = df_sat['RR24'].mean()
            if rr_sa > 1.0:
                rr_sa += df_sat['RR24'].std()*(0.5+player/10)
            elif  rr_sa > 2.0:
                rr_sa += df_sat['RR24'].std()*(0.75+player/10)
            elif  rr_sa > 5.0:
                rr_sa += df_sat['RR24'].std()*(1.0+player/10)
            elif  rr_sa >= 10.0:
                rr_sa += df_sat['RR24'].std()*(1.5+player/10)
            else:
                rr_sa = (df_sat[par]['MSwr-EZ-MOS']+ df_sat[par][mos1])/2.0

            rr_so = df_son['RR24'].mean()
            if rr_so > 1.0:
                rr_so += df_son['RR24'].std()*(0.5+player)
            elif  rr_so > 2.0:
                rr_so += df_son['RR24'].std()*(0.75+player)
            elif  rr_so > 5.0:
                rr_so += df_son['RR24'].std()*(1.0+player)
            elif  rr_so >= 10.0:
                rr_so += df_son['RR24'].std()*(1.5+player)
            else:
                if player!=10:
                    rr_so = (df_son[par]['MSwr-EZ-MOS']+ df_son[par][mos1])/2.0
                else:
                    rr_so = df_son[par][mos1]+0.1

            dict_bet.update( {par : [round(rr_sa,1),round(rr_so,1)]} )
            
        elif par == 'RR1':
            rr_sa = df_sat['RR1'].mean()
            rr_so = df_son['RR1'].mean()
            #sa
            if dict_bet['RR24'][0] == 0.0:
                rr_sa = 0.0
            else:
                if player!=10:
                    rr_sa = df_sat['RR1'].mean()
                else: 
                    rr_sa = df_sat['RR1'].max()
                    
            if rr_sa > dict_bet['RR24'][0]:
                rr_sa = dict_bet['RR24'][0]
            #so
            if dict_bet['RR24'][1] == 0.0:
                rr_so = 0.0
            else:
                if player!=10:
                    rr_so = df_son['RR1'].mean()
                else: 
                    rr_so = df_son['RR1'].max()
                    
            if rr_so > dict_bet['RR24'][1]:
                rr_so = dict_bet['RR24'][1]
            
            dict_bet.update( {par : [round(rr_sa,1),round(rr_so,1)]} )
        else:
            dict_bet.update( {par : [df_sat[par][mos1],df_son[par][mos1]] })
    return dict_bet
    
########################################################################

def check_city(city):
    if city == "Berlin":
        city_short = "BER"
        station_sel = "Schoenefeld"
    elif city == "Wien":
        city_short = "VIE"
        station_sel = "Schwechat"
    elif city == "Zuerich":
        city_short = "ZUR"
        station_sel = "Kloten"
    elif city == "Innsbruck":
        city_short = "IBK"
        station_sel = "Universitaet"
    elif city == "Leipzig":
        city_short = "LEI"
        station_sel = "Schkeuditz"  
    else:
        raise ValueError
    return city_short, station_sel
    
########################################################################

def create_bet(city,mos1='DWD-MOS-Mix',mos2='MSwr-MOS-Mix',month_sel = 4,path="./op_files/"):
    list_mos=["DWD-ICON-MOS","DWD-EZ-MOS","DWD-MOS-Mix","MSwr-EZ-MOS","MSwr-GFS-MOS","MSwr-MOS-Mix"]
    city_short, station_sel = check_city(city)
    result_linreg_sa = pd.read_csv(path + "pr_sa_m"+str(month_sel)+"_"+city+".csv")
    result_linreg_sa =result_linreg_sa.set_index('Unnamed: 0')
    result_linreg_so = pd.read_csv(path + "pr_so_m"+str(month_sel)+"_"+city+".csv")
    result_linreg_so =result_linreg_so.set_index('Unnamed: 0')
    df_sat = read_df(city + '_sa.txt') #mos sa
    df_son = read_df(city + '_so.txt') #mos so
    #bet dictionary
    dict_bet = {}
    par_list = ['Sd1', 'Sd24', 'dd12', 'ff12', 'PPP12', 'Tmax', 'Tmin', 'Td12','T12','RR1','fx24','RR24']
    var_sel  = ['Sd1', 'Sd24', 'dd12', 'ff12', 'PPP12', 'Tmax', 'Tmin', 'Td12','T12','RR1','fx24','RR24']
    for par in par_list:
        print(par)
        if par in var_sel:
            dict_bet.update(
                            {par : [predict(result_linreg_sa,df_sat,list_mos,var_sel=par),
                                    predict(result_linreg_so,df_son,list_mos,var_sel=par)
                                   ]}
                           )
        else:
            dict_bet.update( {par : [df_sat[par][mos1],df_son[par][mos1]] })
            print(df_sat[par][mos1] , "  " , df_son[par][mos1])
    return dict_bet

########################################################################
#function to create autosubmit file
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
    
##################################################################################

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

##################################################################################

def read_df(fname):
    """
    df = pd.read_csv(fname,names=['DAY','Sd1', 'Sd24', 'dd12', 'ff12', 'fx24',   'PPP12', 'Tmax', 'Tmin', 'Td12', 'RR24','T12','RR1'],sep=';')
    """
    df = pd.read_table(fname,sep='\t',
                   names=['DAY','Sd1', 'Sd24', 'dd12', 'ff12', 'fx24', 'PPP12', 'Tmax', 'Tmin', 'Td12', 'RR24','T12','RR1'])
    df = df.set_index('DAY')
    #print(df.index)
    if 'MOS ' in df.index :
        df = df.drop(index=['MOS-Max ','MOS-Min ','MOS '])
    
    df = df.rename(index={'DWD-MOS-Mix ' : 'DWD-MOS-Mix'})
    df = df.rename(index={'DWD-EZ-MOS ':'DWD-EZ-MOS'})
    df = df.rename(index={'DWD-ICON-MOS ':'DWD-ICON-MOS'})
    df = df.rename(index={'MSwr-EZ-MOS ':'MSwr-EZ-MOS'})
    df = df.rename(index={'MSwr-GFS-MOS ':'MSwr-GFS-MOS'})
    df = df.rename(index={'MSwr-MOS-Mix ':'MSwr-MOS-Mix'})

    #df['RR24'] = df['RR24'].where(df['RR24'] != -3.0, 0.0)

    return df

##################################################################################
#main

player = sys.argv[1]
city = sys.argv[2]
par_list=['Sd1', 'Sd24', 'dd12', 'ff12', 'PPP12', 'Tmax', 'Tmin', 'Td12','T12','RR1','fx24','RR24']

if city == "Berlin":
    city_short = "BER"
elif city == "Wien":
    city_short = "VIE"
elif city == "Zuerich":
    city_short = "ZUR"
elif city == "Innsbruck":
    city_short = "IBK"
elif city == "Leipzig":
    city_short = "LEI"
else:
    raise ValueError

df_sat = read_df(city+'_sa.txt')
df_son = read_df(city+'_so.txt')

print(df_sat)
print(df_son)
stat_out(df_son)
stat_out(df_sat)

if player == "MOrtuS":
    fd = open(city + ".txt", "w")
    head(fd,"MOrtuS","cb99",city_short)
    dict_bet=calc_bet (df_sat,df_son,mos1='MSwr-EZ-MOS',mos2='DWD-MOS-Mix',player=0)
    write_bet(fd,par_list,dict_bet)
    fd.close()
elif player == "Foehni":
    fd = open(city + ".txt", "w")
    head(fd,"Foehni","2468",city_short)
    dict_bet=calc_bet (df_sat,df_son,mos1='MSwr-GFS-MOS',mos2='DWD-ICON-MOS',player=10)
    write_bet(fd,par_list,dict_bet)
    fd.close()
else:
    fd = open(city + ".txt", "w")
    head(fd,player,sys.argv[3],city_short)
    dict_bet=calc_bet (df_sat,df_son,mos1='DWD-MOS-Mix',mos2='MSwr-MOS-Mix')
    write_bet(fd,par_list,dict_bet)
    fd.close()












