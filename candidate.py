#-*- coding:utf-8 -*-
import os
import datetime
import sys
#from fim import pfgrowth
"""
交易集构建：
userid,itemid1#itemid2#...(其购买过的item)
fin_str:data_[from date]_[to date]的文件名
fout_str:tras_[from_date]_[to_date] 文件名
"""
def build_trans_data(fin_str,fout_str):
    buy_dict = dict()
    with open(fin_str) as fin:
        for line in fin:
            #user_id,item_id,behavior_type,postion,cate,time
            cols = line.strip().split(',')
            #buy behavior
            if cols[2]=='4':
                buy_dict.setdefault(cols[0],[])
                buy_dict[cols[0]].append(cols[1])
    fout = open(fout_str,'w')
    for user_id in buy_dict:
        print >> fout,'%s,%s'%(user_id,'#'.join(buy_dict[user_id]))
    fout.close()
def iter_trans_data(fin_str):
    with open(fin_str) as fin:
        for line in fin:
            #userid,itemid1#itemid2....
            cols = line.strip().split(',')
            item_list = cols[1].split('#')
            yield item_list
"""
计算在交易集trans中的item的一个分布情况
"""
'''
def compute_item_distribution_in_trans(fin_str):
    item_distribution_dict = dict()
    for fre_item in fpgrowth(iter_trans_data(fin_str),supp=0,zmax = 1,report='[S'):
        print fre_item[0][0],fre_item[1][0]
        key = int(fre_item[1][0])/10
        item_distribution_dict.setdefault(key,0)
        item_distribution_dict[key] +=1
    for key in item_distribution_dict:
        print >> sys.out,'[%d,%d) itemnums is %d' %(key*10 , (key+1) *10, item_distribution_dict[key])
'''
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

"""
fbuy_str:某一天的购买记录
fbefore_str：这天之前的行为记录
fout_str:输出结果 日期,buy:num,cart:num:...none:num
(cart :num 表示历史行为最高为加购物车行为的pair的数量)
is_append:是否以追加的形式打开fout
"""
def compute_purchase_compose(fbuy_str,fbefore_str,fout_str,is_append=False):
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
    #fbuy_str的为data_xxx_buy
    date = fbuy_str.strip().split('_')[-2]
    print >> sys.out,"去重后%s的购买对:%d" %(date,len(buy_dict))
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
if __name__=='__main__':
    parent_dir = os.path.abspath('..')
    split_date = datetime.datetime(2014,12,17)
    td = datetime.timedelta(1)
    next_date = split_date+td
    is_filter = True
    if is_filter:
        fbuy_str = "%s/data/train_test/data_%s_buy_filter"%(parent_dir,next_date.strftime('%m%d'))
        fout= "%s/data/candidate/purchase_compose_filter"%(parent_dir)
        filter_buy_records_by_selected_item("%s/data/train_test/data_%s_buy"%(parent_dir,next_date.strftime('%m%d')),"%s/resource/item"%(parent_dir),fbuy_str)
    else:
        fbuy_str = "%s/data/train_test/data_%s_buy"%(parent_dir,next_date.strftime('%m%d'))
        fout= "%s/data/candidate/purchase_compose"%(parent_dir)
    compute_purchase_compose(fbuy_str,'%s/data/train_test/data_1118_%s'%(parent_dir,split_date.strftime('%m%d')),fout,True)
