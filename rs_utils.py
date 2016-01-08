# -*- coding:utf-8 -*-
import sys
import os
import datetime
import numpy as np
FLAG_TRAIN_TEST = 'train_test'
FLAG_AR = 'ar'
FLAG_CANDIDATE='candidate'
FLAG_CF = 'cf'
FLAG_RULE = 'rule'
FLAG_STAT = 'stat'
DATE_BEGIN = datetime.datetime(2014,11,18)
DATE_END= datetime.datetime(2014,12,17)
td = datetime.timedelta(1)
split_td = datetime.timedelta(6)
DATE_SPLIT= DATE_END - split_td
DATE_NEXT = DATE_END+td
class UserCateAttr:
    def __init__(self):
        self.cate_dict = dict()
        self.item_dict = dict()
    def update_cate_info(self,cate,item,behavior):
        self.cate_dict.setdefault(cate,set())
        self.item_dict.setdefault(item,[0]*4)
        self.cate_dict[cate].add(item)
        self.item_dict[item][behavior] +=1
    def get_cate_score(self,cate):
        score = 0
        for item in self.cate_dict[cate]:
            score += self.get_item_score(item) 
        return score
    def get_score(self):
        score = 0
        for cate in self.cate_dict:
            score += self.get_cate_score(cate)
        return score
    def get_cate_prob(self,cate):
        if cate not in self.cate_dict:
            return 0.0
        total_score = self.get_score()
        cate_prob= self.get_cate_score(cate)/float(total_score)
        return cate_prob 
    def get_all_cates(self):
        return self.cate_dict.keys()
    def get_items_by_cate(self,cate):
        if cate not in self.cate_dict:
            return None
        return self.cate_dict[cate]
    def get_item_score(self,item):
        if item not in self.item_dict:
            return 0
        behavior = np.array(self.item_dict[item])
        #behavior 大于5的限定为5
        #behavior = np.where(behavior>5,5,behavior)
        weight = np.array([1,2,3,4])
        score = np.sum(behavior*weight)
        return score
def init_base_data(fin_str,splite_date):
    user_score_dict = dict()
    user_history_dict= dict()
    with open(fin_str) as fin:
        for line in fin:
            #user,item,be,pos,cate,time
            cols = line.strip().split(',')
            user_history_dict.setdefault(cols[0],set())
            user_history_dict[cols[0]].add(cols[1])
            cur_date = datetime.datetime.strptime(cols[-1],'%Y-%m-%d %H')
            if cur_date >= splite_date:
                user_score_dict.setdefault(cols[0],UserCateAttr())
                behavior = int(cols[2])-1
                user_score_dict[cols[0]].update_cate_info(cols[-2],cols[1],behavior)
    user_list = user_score_dict.keys()
    user_ix_dict = dict()
    for ix,user in enumerate(user_list):
        user_ix_dict[user] = ix
    return user_score_dict,user_history_dict,user_list,user_ix_dict
def init_item_data(fitem_str):
    cate_dict = dict()
    with open(fitem_str) as fin:
        for line in fin:
            #item,pos,cate
            cols = line.strip().split(',')
            cate_dict.setdefault(cols[-1],set())
            cate_dict[cols[-1]].add(cols[0])
    return cate_dict
            

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
    buy_dict = dict() 
    with open(fbuy_str) as fin:
        for line in fin:
            buy_num += 1
            cols = line.strip().split(',')
            if is_item:
                item = cols[1]
            else:
                item = cols[-2]
            pair  = '%s#%s' %(cols[0],item)
            buy_dict.setdefault(pair,0)
            buy_dict[pair]+=1
    with open(fres_str) as fin:
        for line in fin:
            user,items = line.strip().split(',')
            items = items.split('#')
            res_num += len(items)
            for item in items:
                pair  = '%s#%s' %(user,item)
                if pair in buy_dict:
                    hit_num_all+= buy_dict[pair]
                    if pair not in history_pair_set:
                        hit_num+= buy_dict[pair]
                    
    print >> sys.stdout,'hit_num_all %d' %(hit_num_all)
    print >> sys.stdout,'hit_num:%d \nres_num:%d \nbuy_num:%d'%(hit_num,res_num,buy_num)
    print >> sys.stdout,'precision:%f \nrecall:%f'%(float(hit_num)/res_num,float(hit_num)/buy_num)
