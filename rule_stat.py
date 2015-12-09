#-*- coding:utf-8-*
import sys
import datetime
import rs_utils as utils
def count_cate_bahavior_by_recent(fin_str,fbuy_str):

    splite_date = datetime.datetime(2014,12,11)
    cpair_dict = dict()
    with open(fin_str) as fin:
        for line in fin:
            #user,item,be,pos,cate,time
            cols = line.strip().split(',')
            cur_date = datetime.datetime.strptime(cols[-1],'%Y-%m-%d %H')
            if cur_date >= splite_date:
                cpair = cols[0]+'#'+cols[-2]
                cpair_dict.setdefault(cpair,[0,0,0,0])
                behavior = int(cols[2])-1
                cpair_dict[cpair][behavior] += 1
        
    buy_set= set()
    with open (fbuy_str) as fin:
        for line in fin:
            cols = line.strip().split(',')
            cpair = cols[0] + '#'+cols[-2]
            buy_set.add(cpair)
    for cpair in cpair_dict:
        flag = 0
        if cpair in buy_set :
            flag = 1
        print >> sys.stdout,'%s,%s,%d' %(','.join(cpair.split('#')),'#'.join(str(x) for x in cpair_dict[cpair]),flag)



if __name__ == '__main__':
    begin_date = datetime.datetime(2014,11,18)
    end_date = datetime.datetime(2014,12,17)
    data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST) 
    rule_dir = utils.get_data_dir(utils.FLAG_RULE)
    fraw_str = '%s/data_%s_%s' %(data_dir,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))  
    buy_date = datetime.datetime(2014,12,18)
    fbuy_str = '%s/data_buy_%s'%(data_dir,buy_date.strftime('%m%d'))
    count_cate_bahavior_by_recent(fraw_str,fbuy_str)
