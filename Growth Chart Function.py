import os
import numpy as np
import pandas as pd
from scipy import interpolate
import matplotlib.pyplot as plt

data_dir = r"C:\Fantasy\faWAR Disag\2016"
season_dir = r"C:\Fantasy\faWAR Disag\2017"
csv_name_temp = "Week_{0}_Stats_{1}.csv"
cur_wk = 6

def grab_player_data(pos_of_int, in_stat, in_player):
    # Set Range of Weeks For Data Dev
    wk_range = range(1,cur_wk+1)
    # Import Data for Each Week in Range
    for wk in wk_range:
        file_name = os.path.join(season_dir, csv_name_temp.format(wk, pos_of_int))
        if wk==1:
            df = pd.read_csv(file_name)
            df = df[['Player', '{0}'.format(in_stat)]]
            df.columns = ['Player', '{0} 1'.format(in_stat)]
        else:
            df1 = pd.read_csv(file_name)
            df1 = df1[['Player', '{0}'.format(in_stat)]]
            df1.columns = ['Player', '{0} {1}'.format(in_stat, wk)]
            df = df.merge(df1, how = 'outer', on = 'Player')
            df = df.fillna(0)
            df['{0} {1}'.format(in_stat, wk)] = df['{0} {1}'.format(in_stat, wk)]+df['{0} {1}'.format(in_stat, wk-1)]
    # Query Player
    new_df = df.loc[df['Player'] == in_player]
    temp_list = list(new_df.iloc[0])
    # Transpose
    out_xy_list = []
    for wk in wk_range:
        out_xy_list.append([wk, temp_list[wk]])
    out_df = pd.DataFrame(out_xy_list, columns=['Week', in_stat])
    return out_df  
    

def dev_growth_chart(pos_of_int, in_stat, in_player):
    # Create Empty Lists for Data Import
    file_list = []
    long_data = []
    # Set Range of Weeks For Data Dev
    wk_range = range(1,19)
    # Import Data for Each Week in Range
    for wk in wk_range:
        file_name = os.path.join(data_dir, csv_name_temp.format(wk, pos_of_int))
        file_list.append(file_name)
        if wk==1:
            df = pd.read_csv(file_name)
            df = df[['Player', '{0}'.format(in_stat)]]
            df.columns = ['Player', '{0} 1'.format(in_stat)]
        else:
            df1 = pd.read_csv(file_name)
            df1 = df1[['Player', '{0}'.format(in_stat)]]
            df1.columns = ['Player', '{0} {1}'.format(in_stat, wk)]
            df = df.merge(df1, how = 'outer', on = 'Player')
            df = df.fillna(0)
            df['{0} {1}'.format(in_stat, wk)] = df['{0} {1}'.format(in_stat, wk)]+df['{0} {1}'.format(in_stat, wk-1)]
        if wk%4 == 0 or wk == 1 or wk ==18:
            long_data.append([wk, 
                              df['{0} {1}'.format(in_stat, wk)].quantile(.05), 
                              df['{0} {1}'.format(in_stat, wk)].quantile(.10),
                              df['{0} {1}'.format(in_stat, wk)].quantile(.25), 
                              df['{0} {1}'.format(in_stat, wk)].quantile(.5), 
                              df['{0} {1}'.format(in_stat, wk)].quantile(.75), 
                              df['{0} {1}'.format(in_stat, wk)].quantile(.90),
                              df['{0} {1}'.format(in_stat, wk)].quantile(.95)])
    
    # Develop DataFrame for Spline     
    quartile_df = pd.DataFrame(long_data, columns=['Week', '0.05','0.10', '0.25', '0.50', '0.75','0.90','0.95'])
    # Create Spline Functions for Percentile Lines
    f3 = interpolate.interp1d(quartile_df['Week'], quartile_df['0.50'])
    f4 = interpolate.interp1d(quartile_df['Week'], quartile_df['0.75'])
    f5 = interpolate.interp1d(quartile_df['Week'], quartile_df['0.90'])
    f6 = interpolate.interp1d(quartile_df['Week'], quartile_df['0.95'])
    # Calaculate Spline Curves
    xnew = np.arange(1, 18, .1)  
    ynew3 = f3(xnew)
    ynew4 = f4(xnew)
    ynew5 = f5(xnew)
    ynew6 = f6(xnew)
    # Draw Out Percentiles
    fig = plt.figure()
    plt.plot(xnew, ynew3, '-', color= 'b', alpha = 0.4)
    plt.plot(xnew, ynew4, '-', color= 'g', alpha = 0.4)
    plt.plot(xnew, ynew5, '-', color= 'c', alpha = 0.4)
    plt.plot(xnew, ynew6, '-', color= 'm', alpha = 0.4)
    # Adjust the images
    plt.text(16.5,f3(16.5),'50%', color= 'b', backgroundcolor= 'w', horizontalalignment = 'center', verticalalignment = 'center')
    plt.text(16.5,f4(16.5),'75%', color= 'g', backgroundcolor= 'w', horizontalalignment = 'center', verticalalignment = 'center')
    plt.text(16.5,f5(16.5),'90%', color= 'c', backgroundcolor= 'w', horizontalalignment = 'center', verticalalignment = 'center')
    plt.text(16.5,f6(16.5),'95%', color= 'm', backgroundcolor= 'w', horizontalalignment = 'center', verticalalignment = 'center')
    plt.tick_params(
            axis='x',
            which='both',
            bottom='off',
            top='off')
    plt.xlabel("Week")
    plt.tick_params(
            axis='y',
            which='both',
            left='off',
            right='off')
    # Grab Player Data
    playerDF = grab_player_data(pos_of_int, in_stat, in_player)
    plt.plot(playerDF['Week'], playerDF[in_stat], 'x', color= 'k')
    plt.title('{0} - {1}'.format(in_player, in_stat))
    return fig

# Pass through some samples
dev_growth_chart('OF', 'R', 'Charlie Blackmon CF ')
dev_growth_chart('OF', 'R', 'Corey Dickerson LF ')
dev_growth_chart('OF', 'R', 'Kole Calhoun RF ')
dev_growth_chart('OF', 'R', 'Jose Bautista RF ')
dev_growth_chart('1B', 'RBI', 'Mark Reynolds 1B ')
dev_growth_chart('1B', 'RBI', 'Albert Pujols DH ')
dev_growth_chart('1B', 'RBI', 'Freddie Freeman 1B ')
dev_growth_chart('1B', 'RBI', 'Edwin Encarnacion DH ')

dev_growth_chart('3B', 'RBI', 'Miguel Sano 3B ')
dev_growth_chart('3B', 'HR', 'Miguel Sano 3B ')
