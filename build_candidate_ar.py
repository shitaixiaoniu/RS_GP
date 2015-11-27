#-*- coding:utf-8 -*-
import datetime
import sys
import os
from fim import fpgrowth
import rs_utils

"""
交易集构建：
userid,itemid1#itemid2#...(其购买过的item)
fin_str:data_[from date]_[to date]的文件名,[from date][ti date]间的records
fout_str:trans_[from_date]_[to_date] 文件名
"""
def build_trans_data(fin_str,fout_str,is_item = True):
    buy_dict = dict()
    with open(fin_str) as fin:
        for line in fin:
            #user_id,item_id,behavior_type,postion,cate,time
            cols = line.strip().split(',')
            #buy behavior
            if cols[2]=='4':
                buy_dict.setdefault(cols[0],set())
                if is_item :
                    # item 粒度
                    buy_dict[cols[0]].add(cols[1])
                else:
                    # cate粒度
                    buy_dict[cols[0]].add(cols[4])
    fout = open(fout_str,'w')
    for user_id in buy_dict:
        print >> fout,'%s,%s'%(user_id,'#'.join(buy_dict[user_id]))
    fout.close()
"""
构建 交易集的遍历
fin_str:trans_[from_data]_[to_date]
            #userid,itemid1#itemid2....
out:[item1,item2...]
"""
def iter_trans_data(fin_str):
    data_dict = dict()
    with open(fin_str) as fin:
        for line in fin:
            #userid,itemid1#itemid2....
            cols = line.strip().split(',')
            item_list = cols[1].split('#')
            data_dict[cols[0]]= item_list
            #yield item_list
    return data_dict
"""
挖掘关联规则
"""
def minging_rule(trans_dict,fout_str,min_supp= -5):
    fout = open(fout_str,'w')
    for r in fpgrowth(trans_dict.values(),target='r',supp=-5,conf=50,zmin = 2,report='[ac'):
        print >> fout,'%s,%s,%d#%.2f' %(r[0],'#'.join(r[1]),r[2][0],r[2][1])
    fout.close()
"""
根据关键规则增加候选对
trans_dict:交易数据
f_rule_str:规则的文件
fout:结果
"""
def add_candidate(trans_dict,f_rule_str,fout_str):
    candidate_dict = dict()
    with open(f_rule_str) as fin:
        for line in fin:
            cols = line.strip().split(',')
            item_heads_set =set( cols[1].split('#'))
            for user in trans_dict:
                buy_items_set = set(trans_dict[user])
                if item_heads_set.issubset(buy_items_set):
                    if cols[0] not in buy_items_set:
                        candidate_dict.setdefault(user,set())
                        candidate_dict[user].add(cols[0])
    fout = open(fout_str,'w')
    for user in candidate_dict:
        print >> fout ,'%s,%s' %(user,'#'.join(candidate_dict[user]))



"""
根据交集集，挖掘关联规则
min_supp:最小支持度 负数表示trans的绝对数量，非负数表示百分比
trans_dict:交易集 trans_[from date]_[to date] 
"""
def mining_rule_and_add_candidate(trans_dict,fout_str,min_supp = -5):
    candidate_dict = dict()
    for r in fpgrowth(trans_dict.values(),target='r',supp=-5,zmin = 2,report='[ac'):
    #for r in fpgrowth(trans_dict.values(),supp=-5,zmin = 1,report='[a'):
        #r:(item_body,(item_head1,item_head2),[values])
        print >> sys.stdout,r
        item_heads_set =set( r[1])
        for user in trans_dict:
            buy_items_set = set(trans_dict[user])
            if item_heads_set.issubset(buy_items_set):
                if r[0] not in buy_items_set:
                    candidate_dict.setdefault(user,set())
                    candidate_dict[user].add(r[0])
    fout = open(fout_str,'w')
    for user in candidate_dict:
        print >> fout ,'%s,%s' %(user,'#'.join(candidate_dict[user]))
    fout.close()



def main():
    parent_dir = os.path.abspath('..')
    is_item =False
    if is_item:
        trans_dir ='%s/data/ar/ar_item'%(parent_dir)
    else:
        trans_dir ='%s/data/ar/ar_cate'%(parent_dir)
    begin_date = datetime.datetime(2014,12,8)
    split_date = datetime.datetime(2014,12,11)
    begin_date_str = begin_date.strftime('%m%d')
    split_date_str = split_date.strftime('%m%d')
    
    build_trans_data('%s/data/train_test/data_%s_%s'%(parent_dir,begin_date_str,split_date_str),'%s/trans_%s_%s'%(trans_dir,begin_date_str,split_date_str),is_item)
    trans_dict = iter_trans_data('%s/trans_%s_%s'%(trans_dir,begin_date_str,split_date_str))
    
    f_rule_str = '%s/rule_%s_%s'%(trans_dir,begin_date_str,split_date_str)
    
    minging_rule(trans_dict,f_rule_str)
    

    begin_date = datetime.datetime(2014,12,15)
    split_date = datetime.datetime(2014,12,17)
    begin_date_str = begin_date.strftime('%m%d')
    split_date_str = split_date.strftime('%m%d')
    #验证规则的交易集
    build_trans_data('%s/data/train_test/data_%s_%s'%(parent_dir,begin_date_str,split_date_str),'%s/trans_%s_%s'%(trans_dir,begin_date_str,split_date_str),is_item)
    verify_dict = iter_trans_data('%s/trans_%s_%s'%(trans_dir,begin_date_str,split_date_str))
    
    fres_str = '%s/candidate_ar_%s_%s'%(trans_dir,begin_date_str,split_date_str)
    add_candidate(verify_dict,f_rule_str,fres_str)
    
    td = datetime.timedelta(1)
    next_date = split_date+td
    fbuy_str = '%s/data/train_test/data_buy_%s' %(parent_dir,next_date.strftime('%m%d'))
    rs_utils.evaluate_res(fres_str,fbuy_str,is_item)
if __name__ == '__main__':
    main()
