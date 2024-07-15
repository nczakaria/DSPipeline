import scipy.io
import numpy as np
from datetime import datetime, timezone, timedelta
from collections import defaultdict

############# FUNCTIONS
# time zone conversion
def convert_time(time_data):
    dt_utc = datetime.fromtimestamp(time_data, timezone.utc)
    singapore_tz = timezone(timedelta(hours=8))
    dt_singapore = dt_utc.astimezone(singapore_tz)
    return dt_singapore

# time conversion for display purpose
def convert_time(time_data):
    dt_utc = datetime.fromtimestamp(time_data, timezone.utc)
    singapore_tz = timezone(timedelta(hours=8))
    dt_singapore = dt_utc.astimezone(singapore_tz)
    return dt_singapore

# user info
def process_user_info(user_info):
    users = []
    num_withdrawn_users = 0
    for i in range(len(user_info)):
        # user_info[i][0][0] could be 'b1.1' (np string) or [] (np darray)
        # the name does not matter, it is whether they have time stamps though
        # assume the list of users are the same as they are in the bin dataset
        if (bins[i][1].size > 0 or bins[i][2].size > 0 or bins[i][3].size > 0):
            elm = user_info[i][0][0]
            if isinstance(elm, np.ndarray):
                users.append('[]')
            elif isinstance(elm, np.str_):
                users.append(user_info[i][0][0])
        else:
            num_withdrawn_users += 1
    return users, num_withdrawn_users

# 1_min bin
def process_1_30_min_info(bin_info, bin_indicator):
    num_bin = 0 # the number of 1-min bins
    num_both = 0 # both missing
    num_na_bin_date = 0
    num_na_bin_tapnum = 0
    res_bin = []
    user_1_min = []

    if bin_indicator == '1-min':
        bin_ind = 1
    elif bin_indicator == '30-min':
        bin_ind = 2
    
    for i in range(bin_info.shape[0]):
        dict_bin = []
        user_date = set()
        num_bin += len(bin_info[i][1])
        dict_1_min = defaultdict(list)
        for j in range(bin_info[i][bin_ind].shape[0]):
            elm = bin_info[i][bin_ind][j]
            if elm.size == 0:
                num_both += 1
                num_na_bin_date += 1
                num_na_bin_tapnum += 1
                # the purpose is to checking missing values: per day; per user
                # might simulate them later, so do not remove them right now
                # date_bin = ''

                #####################
                # record indices
                #####################
            else:
                # already count the number, so just visualize non NA part
                date_bin_dict = {}
                if np.isnan(elm[0]):
                    num_na_bin_date += 1
                    #####################
                    # record indices
                    #####################
                else:
                    date_obj_bin = convert_time(elm[0]/1000).strftime('%Y-%m-%d %H:%M:%S')
                    date_bin, time_bin = date_obj_bin.split()
                    user_date.add(date_bin)
                    if np.isnan(elm[1]):
                        num_na_bin_tapnum += 1
                    #####################
                    # record indices
                    #####################
                    date_bin_dict[time_bin] = elm[1]
                    dict_1_min[date_bin].append(date_bin_dict)
                    # nested list of dates
                    dict_bin.append(date_bin)
        # time_range.append(list(sorted(user_date)))
        # for each user, {'date': [{time stamp 1, tapnum}, ...]}
        res_bin.append(dict_bin)
        user_1_min.append(dict_1_min)
    return res_bin, user_1_min, num_bin, num_both, num_na_bin_date, num_na_bin_tapnum

def extract_bt_wt(sleepsum_bt_wt):
    res_dt = []
    num_dt = 0
    num_na_sleepnum = 0
    for i in range(sleepsum_bt_wt.shape[0]):
        time_list = []
        for j in range(sleepsum_bt_wt.shape[1]):
            num_dt += 1
            elm = sleepsum_bt_wt[i][j]
            if np.isnan(elm):
                num_na_sleepnum += 1
            else:
                date_obj= convert_time(elm)
                time_list.append(date_obj)
        res_dt.append(time_list)    
    return res_dt, num_dt, num_na_sleepnum

def extract_tib(sleepsum_tib):
    res_tib = []
    num_tib = 0
    num_na_tib = 0
    for i in range(sleepsum_tib.shape[0]):
        tib_dt = []
        for j in range(sleepsum_tib.shape[1]):
            elm = sleepsum_tib[i][j]
            num_tib += 1
            if np.isnan(elm):
                num_na_tib += 1
            tib_dt.append(elm)
        res_tib.append(tib_dt)
    return res_tib, num_tib, num_na_tib

# concatenate 1_min, bt, and wt info together
def concatenate_dt(bt_1_min, bt_dt, wt_dt, users):
    con_res = defaultdict(list)
    # assume bt_dt and wt_dt have the same number of users
    for i in range(len(bt_dt)):
        bt_user = [item.strftime('%Y-%m-%d %H:%M:%S') for item in bt_dt[i]]
        wt_user = [item.strftime('%Y-%m-%d %H:%M:%S') for item in wt_dt[i]]
        dict_name = str(users[i])
        time_keys = bt_1_min[i].keys()
        for item in bt_user:
            con_user = {}
            bt_date, bt_time = item.split()
            # need to consider the cases that either BT or WT is missing
            if bt_date in time_keys:
                con_user[bt_date] = [bt_time, bt_1_min[i][bt_date]]
                for elm in wt_user:
                    wt_date, wt_time = elm.split()
                    if wt_date == bt_date:
                        con_user[bt_date].insert(1, wt_time)
                con_res[dict_name].append(con_user)
    return con_res

############# DATA PREPROSESSING
# import the tap data
tap_mat = scipy.io.loadmat('./Data/Tap_data/TapData.mat')
# BT, WT, TIB: (76, 70)
users = tap_mat['TapData']['Users'][0][0]
bins = tap_mat['TapData']['bins'][0][0]  
sleep_sum = tap_mat['TapData']['SleepSum'][0][0] 

# user in the dataset after removing NA
dt_users, dt_withdrawn = process_user_info(users)
##### might be unncessary: user in the bin dataset after removing NA
bin_user, bin_withdrawn = process_user_info(bins)
# 1-min bin
res_1_min, user_1_min, num_1_min, num_1_min_both, num_na_bin_date, num_na_bin_tapnum = process_1_30_min_info(bins, '1-min')
# BT, WT, TIB
bt_res, num_bt, num_na_bt = extract_bt_wt(sleep_sum['BT'][0][0])
wt_res, num_wt, num_na_wt = extract_bt_wt(sleep_sum['WT'][0][0])
res_tib, num_tib, num_na_tib = extract_tib(sleep_sum['TIB'][0][0])

############# CONCATENATING 
con_dt = concatenate_dt(user_1_min, bt_res, wt_res, dt_users)

# print(len(con_dt))