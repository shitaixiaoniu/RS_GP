# -*- coding:utf-8 -*-
import sys
import datetime
import numpy as np
from scipy import sparse
from scipy import io
import build_candidate_cf as bcbf
import rs_utils as utils
def check_buy():
    begin_date = datetime.datetime(2014,11,18)
    end_date = datetime.datetime(2014,12,17)
    data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST) 
    
    cf_dir = utils.get_data_dir(utils.FLAG_CF)
    frate_str = '%s/rate_%s_%s' %(cf_dir,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))  
    user_ids_list,item_ids_list,user_ids_dict,item_ids_dict = bcbf. compute_user_item_list(frate_str)
    rate_matrix = io.mmread('data')
    rate_matrix = rate_matrix.tolil()
    buy_date = datetime.datetime(2014,12,18)
    fbuy_str = '%s/data_buy_%s'%(data_dir,buy_date.strftime('%m%d'))
    count = 0
    
    with open(fbuy_str) as fin:
        for line in fin:
            cols= line.strip().split(',')
            user = cols[0]
            item = cols[1]
            if item in item_ids_dict and user in user_ids_dict:
                u_ix = user_ids_dict[user]

                i_ix = item_ids_dict[item]
                print >> sys.stdout,'%s,%s,%d' %(user,item,rate_matrix[(u_ix,i_ix)])
            else:
                count += 1
if __name__ =='__main__':
    check_buy()
