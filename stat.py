# -*- coding:utf-8 -*-
import sys
import datetime
import numpy as np
from scipy import sparse
from scipy import io
import build_candidate_cf as bcbf
import rs_utils as utils
import data_model as dm
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
def buy_item_in_recent_record():

    data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST) 
    fraw_str = '%s/data_%s_%s' %(data_dir,utils.DATE_BEGIN.strftime('%m%d'),utils.DATE_END.strftime('%m%d'))  
    fitem_str = '%s/item' %(data_dir)
    fbuy_str = '%s/data_buy_%s'%(data_dir,utils.DATE_NEXT.strftime('%m%d'))
    user_data_model = dm.UserHistoryDataModel(fraw_str,utils.DATE_SPLIT)
    history_item_set = set()
    for user in user_data_model.user_score_dict:
        attr = user_data_model.user_score_dict[user]
        for cate in attr.get_all_cates():
            history_item_set |= attr.get_items_by_cate(cate)
    buy_item_set =set()
    with open(fbuy_str) as fin:
        for line in fin:
            cols =  line.strip().split(',')
            buy_item_set.add(cols[1])
    overlap_item_set = history_item_set & buy_item_set
    print len(overlap_item_set)
    print float(len(overlap_item_set))/len(buy_item_set)


if __name__ =='__main__':
    buy_item_in_recent_record()
