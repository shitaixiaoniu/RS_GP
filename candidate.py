#-*- coding:utf-8 -*-
import os
import datetime
import sys
from fim import fpgrowth
import build_candidate_ar as bca
import rs_utils as utils
from scipy import sparse
from scipy import io
import numpy as np
import build_candidate_cf as bccf

"""
计算在交易集trans中的item的一个分布情况
"""
def compute_item_distribution_in_trans(fin_str):
    item_distribution_dict = dict()
    print fin_str
    for fre_item in fpgrowth(bca.iter_trans_data(fin_str).values(),supp=0,zmax=1,report='[a'):
        print fre_item[0][0],fre_item[1][0]
        base = 5
        key = int(fre_item[1][0])/base
        item_distribution_dict.setdefault(key,0)
        item_distribution_dict[key] +=1
    for key in item_distribution_dict:
        print >> sys.stdout,'[%d,%d) itemnums is %d' %(key*base , (key+1) *base, item_distribution_dict[key])
"""
每天的购买记录 与 resource/item 求交集
fbuy_str:某一天的购买记录
fitem_str:resource/item 给定的item集合
fout_str:过滤之后的输出文件data_xxxx_buy_filter
"""
def filter_buy_records_by_selected_item(fbuy_str,fitem_str,fout_str):
    item_dict = dict()
    with open(fitem_str) as fin:
        for line in fin:
            #itemid,position,cate
            cols = line.strip().split(',')
            if cols[0] not in item_dict:
                item_dict[cols[0]] = 0
    fout = open(fout_str,'w')
    with open(fbuy_str) as fin:
        for line in fin:
            #user_id,item_id,behavior_type,postion,cate,time
            cols = line.strip().split(',')
            if cols[1] in item_dict:
                print >> fout,line.strip()
    fout.close()

def build_buy_dict(fbuy_str,fbefore_str):
    buy_dict=dict()
    with open(fbuy_str) as fin:
        for line in fin:
            #user_id,item_id,behavior_type,postion,cate,time
            cols = line.strip().split(',')
            key = "%s#%s"%(cols[0],cols[1])
            if key not in buy_dict:
                buy_dict[key] = 0
    with open(fbefore_str) as fin:
        for line in fin:
            #user_id,item_id,behavior_type,postion,cate,time
            cols = line.strip().split(',')
            pair = "%s#%s"%(cols[0],cols[1])
            if pair in buy_dict and int(cols[2]) > buy_dict[pair]:
                buy_dict[pair] = int(cols[2])
    return buy_dict

"""
fbuy_str:某一天的购买记录
fbefore_str：这天之前的行为记录
fout_str:输出结果 日期,buy:num,cart:num:...none:num
(cart :num 表示历史行为最高为加购物车行为的pair的数量)
is_append:是否以追加的形式打开fout
"""
def compute_purchase_compose(fbuy_str,fbefore_str,fout_str,is_append=False):
    buy_dict = build_buy_dict(fbuy_str,fbefore_str)
    #fbuy_str的为data_xxx_buy
    date = fbuy_str.strip().split('_')[-2]
    print >> sys.stdout,"去重后%s的购买对:%d" %(date,len(buy_dict))
    #统计各种行为的总次数
    num_dict=dict()
    for val in buy_dict.itervalues():
        num_dict.setdefault(val,0)
        num_dict[val] += 1
    #输出
    if is_append:
        fout = open(fout_str,'a')
    else:
        fout = open(fout_str,'w')
    num_list = ["%s:%s"%(k,v) for k,v in num_dict.iteritems()]
    print >> fout,"%s,%s"%(date,','.join(num_list))
    fout.close()
"""
在一天的购买记录中，购买的物品用户之前完全对其没有行为的user 
并非是新用户(以前完全没行为的user，而且对其购买的item 完全没行为的user 
"""
def user_no_history_in_purchase(fbuy_str,fbefore_str,fout):
    buy_dict = build_buy_dict(fbuy_str,fbefore_str)
    user_dict = dict()
    for key in buy_dict:
        user,item = key.split('#')
        user_dict.setdefault(user,[0,0])
        if buy_dict[key] == 0:
            user_dict[user][0] +=1
        else:
            user_dict[user][1] +=1
    user_history_dict = get_user_history(fbefore_str)
    fout = open(fout_str,'w')
    num_dict = dict()
    base = 1000
    for user in user_dict:
        sum_0,sum_else = user_dict[user]
        if sum_0 > 0 and sum_else == 0 and user in user_history_dict: 
            print >> fout,'%s,%d,%s' %(user,len(user_history_dict[user]),'\002'.join(user_history_dict[user]))
            key = len(user_history_dict[user])/base
            num_dict.setdefault(key,0)
            num_dict[key] +=1
    for num in num_dict:
        print >> sys.stdout,'[%d,%d] %d' %(num*base,(num+1)*base,num_dict[num])
    fout.close()
"""
购买记录里，在以前从没有过行为的item 冷启动的item
"""
def get_new_items_in_purchase(frate_str,fbuy_str):
    rate_matrix = io.mmread('data')
    rate_matrix = rate_matrix.tocsc()
    user_ids_list,item_ids_list,user_ids_dict,item_ids_dict = bccf.compute_user_item_list(frate_str)
    item_set = set()
    new_item_num = 0
    new_item_n = 0
    with open(fbuy_str) as fin:
        for line in fin:
            cols = line.strip().split(',')
            item_set.add(cols[1])
    count = 0
    print item_set
    for item in item_set:
        count += 1
        """
        print 'count'+str(count)
        print item
        """
        if item not in item_ids_dict:
            new_item_n +=1
        else:
            i_ix = item_ids_dict[item]
            """
            print i_ix
            print np.count_nonzero(rate_matrix[:,i_ix]) 
            """
            """
            if np.count_nonzero(rate_matrix[:,i_ix]) == 0:
                new_item_num+=1
            """
    print 'hah'
    print >> sys.stdout, 'new items is %d ' %(new_item_num)
    print >> sys.stdout, 'new items is %d ' %(new_item_n)
    print >> sys.stdout, 'total items (rm dup) %d' %(len(item_set))



def compute_user_bhr_dis(fbefore_str):
    user_history_dict = get_user_history(fbefore_str)
    num_dict = dict()
    base = 1000 
    for user in user_history_dict:
        num = len(user_history_dict[user])
        key = num/base
        num_dict.setdefault(key,0)
        num_dict[key] +=1
    for num in num_dict:
        print >> sys.stdout,'[%d,%d] %d' %(num*base, (num+1)*base, num_dict[num])
        
        
            
def get_user_history(fbefore_str):
    user_dict=dict()
    with open(fbefore_str) as fin:
        for line in fin:
            cols = line.strip().split(',')
            user_dict.setdefault(cols[0],[])
            user_dict[cols[0]].append('\001'.join(cols[1:]))
    return user_dict

if __name__=='__main__':
    begin_date = datetime.datetime(2014,11,18)
    split_date = datetime.datetime(2014,12,17)
    td = datetime.timedelta(1)
    next_date = split_date+td
    data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST)
    cf_dir = utils.get_data_dir(utils.FLAG_CF)
    frate_str = '%s/rate_%s_%s' %(cf_dir,begin_date.strftime('%m%d'),split_date.strftime('%m%d'))  
    fbefore_str = '%s/data_%s_%s' %(data_dir,begin_date.strftime('%m%d'),split_date.strftime('%m%d'))
    fbuy_str = '%s/data_buy_%s' %(data_dir,next_date.strftime('%m%d'))
    candidate_dir = utils.get_data_dir(utils.FLAG_CANDIDATE)
    fout_str = '%s/user_no_behavior_in_buy_%s' %(candidate_dir,next_date.strftime('%m%d'))
    get_new_items_in_purchase(frate_str,fbuy_str)

    #user_no_history_in_purchase(fbuy_str,fbefore_str,fout_str)
    #compute_user_bhr_dis(fbefore_str)
    """
    is_filter = False
    if is_filter:
        fbuy_str = "%s/data/train_test/data_%s_buy_filter"%(parent_dir,next_date.strftime('%m%d'))
        fout= "%s/data/candidate/purchase_compose_filter"%(parent_dir)
        filter_buy_records_by_selected_item("%s/data/train_test/data_%s_buy"%(parent_dir,next_date.strftime('%m%d')),"%s/resource/item"%(parent_dir),fbuy_str)
    else:
        fbuy_str = "%s/data/train_test/data_%s_buy"%(parent_dir,next_date.strftime('%m%d'))
        fout= "%s/data/candidate/purchase_compose"%(parent_dir)
    compute_purchase_compose(fbuy_str,'%s/data/train_test/data_1118_%s'%(parent_dir,split_date.strftime('%m%d')),fout,True)
    compute_item_distribution_in_trans('%s/data/ar/ar_cate/trans_1208_%s'%(parent_dir,split_date.strftime('%m%d')))
    #item_distribution('%s/data/ar/trans_1118_%s'%(parent_dir,split_date.strftime('%m%d')))
    """
