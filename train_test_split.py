#coding = utf-8
from datetime import datetime as dt
from datetime import timedelta
import os
import sys
import rs_utils as utils

def filter_records_by_selected_item(fraw_str,fitem_str,fout_str):
    item_set = set()
    with open(fitem_str) as fin:
        for line in fin:
            #itemid,position,cate
            cols = line.strip().split(',')
            item_set.add(cols[0])
    fout = open(fout_str,'w')
    with open(fraw_str) as fin:
        for line in fin:
            #user_id,item_id,behavior_type,postion,cate,time
            cols = line.strip().split(',')
            if cols[1] in item_set:
                print >> fout,line.strip()
def compute_items_users_num(fraw_str):
    item_set = set()
    user_set = set()
    with open(fraw_str) as fin:
        for line in fin:
            #user_id,item_id,behavior_type,postion,cate,time
            cols = line.strip().split(',')
            user_set.add(cols[0])
            item_set.add(cols[1])
    print >> sys.stdout,'user num %d ' %(len(user_set))
    print >> sys.stdout,'item  num %d ' %(len(item_set))

            
        
def split_records_by_delta(fin_str,beg_date_str,end_date_str,file_str):
    time_format = '%Y-%m-%d %H'
    beg_date = dt.strptime(beg_date_str,time_format)
    end_date = dt.strptime(end_date_str,time_format)
    fout = open(file_str,'w')
    with open(fin_str)as fin:
        for line in fin:
            #user_id,item_id,behavior_type,postion,cate,time
            cols = line.strip().split(',')
            #print cols[-1]
            cur_date = dt.strptime(cols[-1],time_format)
            if cur_date <= end_date and cur_date >= beg_date:
                print >> fout,line.strip()
    fout.close()
def split_records_by_date(fin_str,date_str,file_str,only_buy = False):
    time_format = '%Y-%m-%d'
    base_date = dt.strptime(date_str,time_format)
    fout = open(file_str,'w')
    with open (fin_str)as fin:
        for line in fin:
            cols = line.strip().split(',')
            cur_str = cols[-1].split(' ')[0]
            cur_date = dt.strptime(cur_str,time_format)
            if cur_date == base_date:
                if only_buy :
                    if cols[2] == '4':
                        print>>fout,line.strip()
                else:
                    print >> fout,line.strip()
    fout.close()
def merge_user_purchase_cate(fin_str,fout_str):
    user_dict = dict()
    with open(fin_str) as fin:
        for line in fin:
            cols = line.strip().split(',')
            user_dict.setdefault(cols[0],set())
            user_dict[cols[0]].add(cols[-2])
    fout = open(fout_str,'w')
    for user in user_dict:
        print >> fout,'%s,%s' %(user,'#'.join(user_dict[user]))
    fout.close()

if __name__ == '__main__':
    parent_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST)
    begin_date = dt(2014,12,18)
    split_date = dt(2014,12,16)
    td = timedelta(1)
    next_date = split_date+td
    fout1 = '%s/user_behavior_filter'%(parent_dir)
    fraw_str = '/home/kliner/shitaixiaoniu/ali_rs/resource/user'
    fitem_str = '/home/kliner/shitaixiaoniu/ali_rs/resource/item'
    fout_data_delta = '%s/data_%s_%s' %(parent_dir,begin_date.strftime('%m%d'),split_date.strftime('%m%d'))
    fout_data_by_day= '%s/data_%s' %(parent_dir,next_date.strftime('%m%d'))
    fout_data_buy_by_day= '%s/data_buy_%s' %(parent_dir,next_date.strftime('%m%d'))
    #filter_records_by_selected_item(fraw_str,fitem_str,fout1)
    #compute_items_users_num(fout1)
    split_records_by_delta(fout1,'%s 00'%(begin_date.strftime('%Y-%m-%d')),'%s 23'%(split_date.strftime('%Y-%m-%d')),fout_data_delta)
    #split_records_by_date(fout1,next_date.strftime('%Y-%m-%d'),fout_data_by_day)
    
    #split_records_by_date(fout1,next_date.strftime('%Y-%m-%d'),fout_data_buy_by_day,only_buy=True)

