#-*- coding:utf-8-*
import sys
import datetime
import numpy as np
import rs_utils as utils
import matplotlib.pyplot as plt
def count_cate_item_by_recent(fin_str,fitem_str,fout_str,splite_date):

    cate_set = set()
    with open(fin_str) as fin:
        for line in fin:
            #user,item,be,pos,cate,time
            cols = line.strip().split(',')
            cur_date = datetime.datetime.strptime(cols[-1],'%Y-%m-%d %H')
            if cur_date >= splite_date:
                cate_set.add(cols[-2])
    cate_num_dict = dict()
    with open(fitem_str) as fin:
        for line in fin:
            #item,pos,cate
            cols = line.strip().split(',')
            cate_num_dict.setdefault(cols[-1],0)
            cate_num_dict[cols[-1]] += 1
    fout = open(fout_str,'w')
    for cate in cate_set:
        print >> fout,'%s,%d' %(cate,cate_num_dict[cate])
    fout.close()

def count_cate_bahavior_by_recent(fin_str,fbuy_str,fitem_str,fout_str,splite_date):

    cpair_dict = dict()
    cate_set = set()
    with open(fin_str) as fin:
        for line in fin:
            #user,item,be,pos,cate,time
            cols = line.strip().split(',')
            cur_date = datetime.datetime.strptime(cols[-1],'%Y-%m-%d %H')
            if cur_date >= splite_date:
                cate_set.add(cols[-2])
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
    cate_num_dict = dict()
    with open(fitem_str) as fin:
        for line in fin:
            #item,pos,cate
            cols = line.strip().split(',')
            cate_num_dict.setdefault(cols[-1],0)
            cate_num_dict[cols[-1]] += 1
    fout = open(fout_str,'w')
    for cpair in cpair_dict:
        flag = 0
        if cpair in buy_set :
            flag = 1
        user,cate = cpair.split('#')
        behavior = np.array(cpair_dict[cpair])
        weight = np.array([1,2,3,4])
        score = np.sum(behavior*weight)
        print >> fout,'%s,%s,%s,%d,%d,%d' %(user,cate,'#'.join(str(x) for x in cpair_dict[cpair]),score,cate_num_dict[cate],flag)
    fout.close()
class Score_attr:
    def __init__(self):
        self.score_list = list()
        self.flag = 0
def compute_user_cate_mean_var(fin_str,fout_str):
    user_dict = dict()
    with open(fin_str) as fin:
        for line in fin:
            #user,cate,behavior,score,item_num,flag
            cols = line.strip().split(',')
            user = cols[0]
            user_dict.setdefault(user,Score_attr())
            user_dict[user].score_list.append(int(cols[3]))
            if int(cols[-1] ) > user_dict[user].flag:
                    user_dict[user].flag = int(cols[-1])
    fout = open(fout_str,'w')
    for user in user_dict:
        total_score = np.sum(np.array(user_dict[user].score_list))
        mean = np.mean(np.array(user_dict[user].score_list))
        std = np.std(np.array(user_dict[user].score_list))
        print >> fout , '%s,%.4f,%.4f,%d,%d' %(user,mean,std,total_score,user_dict[user].flag)
    fout.close()
def compute_user_cate_prob(fin_str,ftotal_score_str,fout_str):
    user_dict = dict()
    with open(ftotal_score_str) as fin:
        for line in fin:
            #user,mean,std,total_score,flag
            cols = line.strip().split(',')
            user_dict[cols[0]] = int(cols[-2])
    fout = open(fout_str,'w')
    with open(fin_str) as fin:
        for line in fin:
            #user,cate,behavior,score,item_num,flag
            cols = line.strip().split(',')
            total_score = user_dict[cols[0]]
            prob = float(cols[3])/total_score
            print >> fout,'%s,%.4f,%s' %(','.join(cols[:-2]),prob,','.join(cols[-2:]))
    fout.close()

def plot_user_mean_std(fin_str):
    data_pos_list = list()
    data_neg_list = list()
    with open(fin_str) as fin:
        for line in fin:
            #user,mean,std,flag
            cols = line.strip().split(',')
            if cols[-1] == '1':
                data_pos_list.append([float(cols[1]),float(cols[2])])
            else:

                data_neg_list.append([float(cols[1]),float(cols[2])])
    print len(data_neg_list)
    print len(data_pos_list)
    data_pos_array = np.array(data_pos_list)
    data_neg_array = np.array(data_neg_list)
    plt.plot(data_neg_array[:,0],data_neg_array[:,1],'o')
    plt.plot(data_pos_array[:,0],data_pos_array[:,1],'ro')

    plt.show()

if __name__ == '__main__':
    begin_date = datetime.datetime(2014,11,18)
    end_date = datetime.datetime(2014,12,17)
    td = datetime.timedelta(1)
    split_td = datetime.timedelta(6)
    splite_date = end_date - split_td
    data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST) 
    rule_dir = utils.get_data_dir(utils.FLAG_RULE)
    fraw_str = '%s/data_%s_%s' %(data_dir,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))  
    fitem_str = '%s/item' %(data_dir)
    buy_date = end_date+td
    fbuy_str = '%s/data_buy_%s'%(data_dir,buy_date.strftime('%m%d'))
    fout_str = '%s/rule_stat_cate_%s_%s' %(rule_dir,splite_date.strftime('%m%d'),end_date.strftime('%m%d'))
    fout_item_str = '%s/rule_stat_cate_item_%s_%s' %(rule_dir,splite_date.strftime('%m%d'),end_date.strftime('%m%d'))
    fout_mean_str ='%s/rule_stat_user_cate_mean_std_%s_%s' %(rule_dir,splite_date.strftime('%m%d'),end_date.strftime('%m%d')) 
    fout_prob_str ='%s/rule_stat_user_cate_prob_%s_%s' %(rule_dir,splite_date.strftime('%m%d'),end_date.strftime('%m%d')) 
    #count_cate_bahavior_by_recent(fraw_str,fbuy_str,fitem_str,fout_str,splite_date)
    compute_user_cate_mean_var(fout_str,fout_mean_str)
    compute_user_cate_prob(fout_str,fout_mean_str,fout_prob_str)
    #plot_user_mean_std(fout_mean_str)
    #count_cate_item_by_recent(fraw_str,fitem_str,fout_item_str,splite_date)
