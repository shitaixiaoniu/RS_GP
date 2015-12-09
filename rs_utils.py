# -*- coding:utf-8 -*-
import sys
import os
FLAG_TRAIN_TEST = 'train_test'
FLAG_AR = 'ar'
FLAG_CANDIDATE='candidate'
FLAG_CF = 'cf'
FLAG_RULE = 'rule'
def evaluate_res(fres_str,fbuy_str,is_item):
    res_dict = dict()
    res_num = 0
    hit_num = 0
    buy_num = 0
    with open(fres_str) as fin:
        for line in fin:
            user,items = line.strip().split(',')
            items = items.split('#')
            res_dict[user] = items
            res_num += len(items)
    with open(fbuy_str) as fin:
        for line in fin:
            buy_num += 1
            cols = line.strip().split(',')
            if cols[0] in res_dict:
                if is_item:
                    item = cols[1]
                else:
                    item = cols[-2]
                if item in res_dict[cols[0]]:
                    hit_num +=1
    print >> sys.stdout,'hit_num:%d \nres_num:%d \nbuy_num:%d'%(hit_num,res_num,buy_num)
    print >> sys.stdout,'precision:%f \nrecall:%f'%(float(hit_num)/res_num,float(hit_num)/buy_num)

def get_data_dir(flag ):
    parent_dir = os.path.abspath('..')
    target_dir = '%s/data_filter/%s' %(parent_dir,flag)
    return target_dir
     

def evaluate_res_except_history(fres_str,fbuy_str,is_item,fbefore_str):
    history_pair_set = set()
    with open(fbefore_str) as fin:
        for line in fin:
            cols = line.strip().split(',')
            if is_item:

                pair = '%s#%s' %(cols[0],cols[1])
            else:
                pair = '%s#%s' %(cols[0],cols[-2])
                
            history_pair_set.add(pair)

    res_dict = dict()
    res_num = 0
    hit_num_all = 0
    hit_num = 0
    buy_num = 0
    with open(fres_str) as fin:
        for line in fin:
            user,items = line.strip().split(',')
            items = items.split('#')
            res_dict[user] = items
            res_num += len(items)
    with open(fbuy_str) as fin:
        for line in fin:
            buy_num += 1
            cols = line.strip().split(',')
            if cols[0] in res_dict:
                if is_item:
                    item = cols[1]
                else:
                    item = cols[-2]
                if item in res_dict[cols[0]]:
                    hit_num_all+=1
                    pair = '%s#%s' %(cols[0],cols[1])
                    if pair not in history_pair_set:
                        hit_num+=1
                    
    print >> sys.stdout,'hit_num_all %d' %(hit_num_all)
    print >> sys.stdout,'hit_num:%d \nres_num:%d \nbuy_num:%d'%(hit_num,res_num,buy_num)
    print >> sys.stdout,'precision:%f \nrecall:%f'%(float(hit_num)/res_num,float(hit_num)/buy_num)
