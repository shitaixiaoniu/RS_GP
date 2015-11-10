#coding = utf-8
from datetime import datetime as dt
from datetime import timedelta
import os

def split_records_by_delta(beg_date_str,end_date_str,file_str):
    time_format = '%Y-%m-%d %H'
    beg_date = dt.strptime(beg_date_str,time_format)
    end_date = dt.strptime(end_date_str,time_format)
    fout = open(file_str,'w')
    with open('/home/xuejiewu/workspace/python/ali_rs/resource/user') as fin:
        for line in fin:
            #user_id,item_id,behavior_type,postion,cate,time
            cols = line.strip().split(',')
            #print cols[-1]
            cur_date = dt.strptime(cols[-1],time_format)
            if cur_date <= end_date and cur_date >= beg_date:
                print >> fout,line.strip()
    fout.close()
def split_records_by_date(date_str,file_str,only_buy = False):
    time_format = '%Y-%m-%d'
    base_date = dt.strptime(date_str,time_format)
    fout = open(file_str,'w')
    with open ('/home/xuejiewu/workspace/python/ali_rs/resource/user') as fin:
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
if __name__ == '__main__':
    parent_dir = os.path.abspath('..')
    split_date = dt(2014,12,3)
    td = timedelta(1)
    next_date = split_date+td
    fout1 = '%s/data/train_test/data_1118_%s'%(parent_dir,split_date.strftime('%m%d'))
    print fout1
    split_records_by_delta('2014-11-18 00','%s 23'%(split_date.strftime('%Y-%m-%d')),fout1)
    """
    fout2= '%s/data/train_test/data_1218'%(parent_dir)
    split_records_by_date('2014-12-18',fout2)
    """

    fout3= '%s/data/train_test/data_%s_buy'%(parent_dir,next_date.strftime('%m%d'))
    split_records_by_date('%s'%(next_date.strftime('%Y-%m-%d')),fout3,True)

    

