#-*- coding:utf-8 -*-
import sys
import os
import datetime
import math
import heapq
import numpy as np
from sklearn.decomposition import NMF
from sklearn.utils.extmath import fast_dot
from sklearn.neighbors import NearestNeighbors
import rs_utils as utils
from scipy import sparse
from scipy import io
class PairAttri(object):
    def __init__(self):
        self.cate = ''
        self.rate = 0
        self.lastime = '2014-11-18 00'
    def update_by_list(self,cols):
        self.cate= cols[-2]
        #点击行为
        if cols[2]=='1'and self.rate<2:
            self.rate+= 1
        elif cols[2] != '1' and self.rate< int(cols[2])+1:
            self.rate = int(cols[2])+1
        #cur_date = datetime.datetime.strptime(cols[-1],'%Y-%m-%d %H')
        if cols[-1] > self.lastime:
            self.lastime= cols[-1] 
    #只用购买数据评分 购买次数为分数
    def update_by_purchase_list(self,cols):
        self.cate = cols[-2]
        if cols[-1] > self.lastime:
            self.lastime= cols[-1] 
        self.rate += 1


    def to_str(self):
        return '%s,%d,%s' %(self.cate,self.rate,self.lastime)


def dict2str(attr_dict):
    attr_list = [str(attr_dict[key]) for key in ['cate','rate','lasttime']]
    return ','.join(attr_list)
"""
构建物品评分数据
点击一次：1
点击>=2:2
收藏：3
加购物车：4
购买：5
取最高分item的分数
输入：data_[beg_date]_[end_date]
输出：rate_[beg_date]_[end_date]:userid,itemid,cate,rate,last_time(最后一次item的行为时间)
"""
def build_item_rate_data(fin_str,fout_str,only_buy ):
    pair_dict = dict()
    i = 0
    with open(fin_str) as fin:
        for line in fin:
            i += 1
            if i % 10000 == 0:
                print i
            #user_id,item_id,behavior_type,postion,cate,time
            cols = line.strip().split(',')
            pair = '%s#%s' %(cols[0],cols[1])
            #更新attr
            if only_buy :
                if cols[2] == '4':
                    pair_dict.setdefault(pair,PairAttri())
                    pair_dict[pair].update_by_purchase_list(cols)
            else:
                pair_dict.setdefault(pair,PairAttri())
                pair_dict[pair].update_by_list(cols)
    print 'one'
    fout = open(fout_str,'w')
    for pair in pair_dict:
        user,item = pair.split('#')
        print >> fout,'%s,%s,%s' %(user,item, pair_dict[pair].to_str())
    fout.close()

def compute_user_item_list(fin):
    user_ids_set= set()
    item_ids_set= set()
    with open(fin) as fin:
        for line in fin:
            cols = line.strip().split(',')
            if cols[0] not in user_ids_set:
                user_ids_set.add(cols[0])
            if cols[1] not in item_ids_set:
                item_ids_set.add(cols[1])
    user_ids_list = list(user_ids_set)
    item_ids_list = list(item_ids_set)
    user_ids_dict = dict()
    item_ids_dict = dict()
    for u_ix,user in enumerate(user_ids_list):
        user_ids_dict[user] = u_ix
    for i_ix,item in enumerate(item_ids_list):
        item_ids_dict[item] = i_ix
    return user_ids_list,item_ids_list,user_ids_dict,item_ids_dict



"""
input :fin_str:
    userid,itemid,cate,rate,last_time(最后一次item的行为时间) 
    theta: 时间衰减函数 rate = rate * exp(-theta * t) t为到特定时间【12.17】的天数
output:
    'data', the full data in the shape:
        {user_id: { item_id: (rating, timestamp),
            item_id2: (rating2, timestamp2) }, ...} and
    'user_ids_list': the user labels  [user_id1, user_id2...} and
    'item_ids_list': the item labels 
             [item_id, item_id2 ...] 
"""

def load_rate_data(fin_str,user_ids_dict,item_ids_dict,theta = 0.0):
    #设为2014-12-17 23
    """
    split_date = datetime.datetime(2014,12,17,23)
    rate_matrix = sparse.lil_matrix((len(user_ids_dict),len(item_ids_dict)))
    i = 0
    with open(fin_str) as fin:
        for line in fin:
            #userid,itemid,cate,rate,lasttime
            i +=1
            '''
            if i%100 == 0:
                print i
            '''
            cols = line.strip().split(',')

            #cur_date = datetime.datetime.strptime(cols[-1],'%Y-%m-%s %H:%M:%S')
            cur_date = datetime.datetime.strptime(cols[-1],'%Y-%m-%d %H')
            days_delta = (split_date-cur_date).days
            #带时间衰减的分数
            rate = int(cols[-2]) * math.exp(-theta * days_delta)
            u_ix = user_ids_dict[cols[0]]
            i_ix = item_ids_dict[cols[1]]
            rate_matrix[u_ix,i_ix] = rate
    io.mmwrite('rate_data_buy',rate_matrix)
    print >> sys.stdout,rate_matrix.nnz
    """
    rate_matrix = io.mmread('rate_data_buy')
    rate_matrix = rate_matrix.tolil()
    print rate_matrix.shape
    print rate_matrix[1,[1,2]].toarray()
    return rate_matrix

"""
input: user_num * item_num 的矩阵 a[i][j] 表示user i 对 item j的评分
output: user_num * item_num 的预测评分矩阵
"""
def model_and_predict(rate_matrix,user_ids_list,item_ids_list,top_n,fout_str):
    direct_predict_item_base(rate_matrix,user_ids_list,item_ids_list,top_n,fout_str)
    """
    nmf = NMF(n_components=100,init='nndsvd')
    user_distribution = nmf.fit_transform(rate_matrix)
    item_distribution = nmf.components_
    np.save('user_dis_buy_100',user_distribution)
    np.save('item_dis_buy_100',item_distribution)
    user_distribution = np.load('user_dis_buy_50.npy')
    item_distribution = np.load('item_dis_buy_50.npy')
    """
    """
    print  user_distribution.shape
    print  item_distribution.shape
    nmf_predict_item_base(rate_matrix,item_distribution,user_ids_list,item_ids_list,top_n,fout_str)
    #nmf_predict_user_base(rate_matrix,user_distribution,user_ids_list,item_ids_list,top_n,fout_str)
    #nmf_predict_direct(rate_matrix,user_distribution,item_distribution,user_ids_list,item_ids_list,top_n,fout_str)
    """
def direct_predict_item_base(rate_matrix,user_ids_list,item_ids_list,top_n,fout_str):
    print '%s begin' %(str(datetime.datetime.now()))
    item_distribution = rate_matrix.T
    nbrs = NearestNeighbors(top_n,n_jobs = -1,algorithm="brute", metric="cosine").fit(item_distribution)
    print '%s begin' %(str(datetime.datetime.now()))
    distance,indices = nbrs.kneighbors()
    print '%s begin' %(str(datetime.datetime.now()))

    fout = open(fout_str,'w')

    for u_ix,user in enumerate(user_ids_list):
        if u_ix %100 ==0:
            print u_ix
        candidate_item_list = [] 
        for i_ix,item in enumerate(item_ids_list): 
            #print 'one',str(datetime.datetime.now())
            if rate_matrix[(u_ix,i_ix)] != 0: 
                continue
            i_nbs = indices[i_ix]
            #print 'two',str(datetime.datetime.now())
            #print i_nbs
            rate_nbs = rate_matrix[u_ix,i_nbs]
            #print 'three',str(datetime.datetime.now())
            #print rate_nbs.toarray()
            #print 1-distance[i_ix]
            if rate_nbs.nnz==0 or np.sum(1-distance[i_ix]) == 0:
                continue
            #print 'four',str(datetime.datetime.now())
            rate_predict = np.sum(np.multiply(rate_nbs,1-distance[i_ix]))/np.sum(1-distance[i_ix])
            #print rate_predict
            #print 'five',str(datetime.datetime.now())
            if rate_predict != 0:
                candidate_item_list.append((item,rate_predict))
        
        candiadte_items = heapq.nlargest(10,candidate_item_list,key = lambda x:x[1])
        if  not candiadte_items:
            continue
        items,vals = zip(*candiadte_items)
        print >> fout,'%s,%s' %(user,'#'.join(items))
    fout.close()

def nmf_predict_item_base(rate_matrix,item_distribution,user_ids_list,item_ids_list,top_n,fout_str):
    print '%s begin' %(str(datetime.datetime.now()))
    item_distribution = item_distribution.T
    nbrs = NearestNeighbors(top_n,n_jobs = -1,algorithm="brute", metric="cosine").fit(item_distribution)
    u_ixs,i_ixs = np.nonzero(rate_matrix>0)
    print '%s nbrs knn begin' %(str(datetime.datetime.now()))
    indices = nbrs.kneighbors(item_distribution[i_ixs],return_distance=False)
    print '%s nbrs end' %(str(datetime.datetime.now()))
    candidate_dict = dict()
    for i,u_ix in enumerate(u_ixs):
        if i%1000 == 0:
            print u_ix
        user = user_ids_list[u_ix]
        candidate_dict.setdefault(user,set())
        items_list = [item_ids_list[i_ix] for i_ix in indices[i]]
        item_buy = item_ids_list[i_ixs[i]]

        candidate_dict[user] |= set(items_list)-set(item_buy)
    fout = open(fout_str,'w')
    for user in candidate_dict:
        print >> fout,'%s,%s' %(user,'#'.join(candidate_dict[user]))
    fout.close()


def nmf_predict_user_base(rate_matrix,user_distribution,user_ids_list,item_ids_list,top_n,fout_str):
    fout = open(fout_str,'w')
    #method 2 knn
    nbrs = NearestNeighbors(top_n).fit(user_distribution)
    distance,indices = nbrs.kneighbors()
    for u_ix, nbs  in enumerate(indices) :
        if u_ix %1000 ==0:
            print u_ix
        user = user_ids_list[u_ix]
        #user buy item
        u_i_ix = np.argwhere(rate_matrix[u_ix]>0)[:,1]
        # nbs buy or cart item index
        nb_i_ix = np.argwhere(rate_matrix[nbs]>0)[:,1]
        if  nb_i_ix.size == 0:
            continue
        candidate_i_ix = np.setdiff1d(nb_i_ix,u_i_ix)
        if  candidate_i_ix.size==0:
            continue
        candidate_item_list = [item_ids_list[i_ix] for i_ix in candidate_i_ix]
        print >> fout,'%s,%s' %(user,'#'.join(candidate_item_list))
    fout.close()
def nmf_predict_direct(rate_matrix,user_distribution,item_distribution,user_ids_list,item_ids_list,top_n,fout_str):
    fout = open(fout_str,'w')
    #method 1 : w*h
    for u_ix,u in enumerate(user_distribution):
        predict_vec = fast_dot(u,item_distribution)
        filter_vec = np.where(rate_matrix.getrow(u_ix).toarray()>0,0,1)
        predict_vec = predict_vec * filter_vec
        sort_ix_vec = np.argpartition(-predict_vec[0],top_n)[:top_n]
        candidate_item_list = list()
        for i_ix in sort_ix_vec:
            item_id = item_ids_list[i_ix]
            candidate_item_list.append(item_id)
        user_id = user_ids_list[u_ix]
        print >> fout,'%s,%s' %(user_id,'#'.join(candidate_item_list))
    fout.close()
    
    

"""
根据预测 推荐
input:
    predict_matrix:user_num * item_num 预测评分矩阵（只有用户没有行为的item有值）
    user_ids_list:真正用户idlist
    item_ids_list:正在itemidlist
    top_n:推荐的前n

fout： 结果输出文件  userid,itemid#
"""
def recommend(predict_matrix,user_ids_list,item_ids_list,top_n,fout):
    print >> sys.stdout,predict_matrix
    #统计该评分矩阵的分布情况
    # 升序 返回的为index
    sorted_ix_matrix = predict_matrix.argsort()
    print >> sys.stdout,"排序的index"
    print >> sys.stdout,sorted_ix_matrix
    sorted_ix_matrix = sorted_ix_matrix[:,-top_n:]
    print >> sys.stout,'截取top  %d 后的排序index 矩阵 '%(top_n)
    print >> sys.stdout,sorted_ix_matrix
    rs_dict = dict()
    for x,y in np.ndindex(sorted_ix_matrix):
        u_ix = x
        i_ix = predict_matrix[x][y]
        # 找到user_id  item_id 保存 推荐结果
        user_id = user_ids_list[u_ix]
        item_id = item_ids_list[i_ix]
        rs_dict.setdefault(user_id,list())
        rs_dict[user_id].append(item_id)
    fout = open(fout_str,'w')
    for user in rs_dict:
        print >> fout,'%s,%s' %(user,'#'.join(rs_dict[user]))
    fout.close()

def main():
    begin_date = datetime.datetime(2014,11,18)
    end_date = datetime.datetime(2014,12,17)
    data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST) 
    fraw_str = '%s/data_%s_%s' %(data_dir,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))
    cf_dir = utils.get_data_dir(utils.FLAG_CF)
    frate_str = '%s/rate_buy_%s_%s' %(cf_dir,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))  
    theta = 0.0
    top_n =10 
    frs_str = '%s/cf_%s_%s_%.1f_%d' %(cf_dir,begin_date.strftime('%m%d'),end_date.strftime('%m%d'),theta,top_n)
    """
    print >> sys.stdout,'[build_item_rate_data] doing...'
    build_item_rate_data(fraw_str,frate_str,only_buy = True)
    print >> sys.stdout,'[build_item_rate_data] done'
    """
    user_ids_list,item_ids_list,user_ids_dict,item_ids_dict = compute_user_item_list(frate_str)
    print >> sys.stdout,'user num %d' %(len(user_ids_list))
    print >> sys.stdout,'item num %d' %(len(item_ids_list))
    print >> sys.stdout,'[compute_user_item_list] done '
    print >> sys.stdout,'[load_rate_data] doing...'
    rate_matrix = load_rate_data(frate_str,user_ids_dict,item_ids_dict,theta)
    print >> sys.stdout,'[load_rate_data] done...'
    print >> sys.stdout,'[model_and_predict] doing...'
    predict_matrix = model_and_predict(rate_matrix,user_ids_list,item_ids_list,top_n,frs_str)
    print >> sys.stdout,'[model_and_predict] done...'
    buy_date = datetime.datetime(2014,12,18)
    fbuy_str = '%s/data_buy_%s'%(data_dir,buy_date.strftime('%m%d'))
    utils.evaluate_res_except_history(frs_str,fbuy_str,True,fraw_str)
    #utils.evaluate_res(frs_str,fbuy_str,True)
if __name__ =='__main__':
    main()
