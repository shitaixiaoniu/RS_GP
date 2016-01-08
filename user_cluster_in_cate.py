#-*- coding:utf-8-*
import sys
import datetime
import numpy as np
import rs_utils as utils
import os
from scipy import sparse
from scipy import io
from sklearn.preprocessing import MaxAbsScaler 
from sklearn.cluster import DBSCAN
from sklearn.cluster import MiniBatchKMeans 
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import NMF
from sklearn.decomposition import TruncatedSVD
class UCIC:
    def __init__(self,fin_str,splite_date):
        self.user_score_dict,self.user_history_dict,self.__user_ix_list,self.__user_ix_dict = utils.init_base_data(fin_str,splite_date)
        cate_set = set()
        for user in self.user_score_dict:
            attr = self.user_score_dict[user]
            cate_set |= set(attr.get_all_cates())
        cate_ix_list = list(cate_set)
        self.__cate_ix_dict = dict()
        for ix,user in enumerate(cate_ix_list):
            self.__cate_ix_dict[user]=ix
            
    def __extract_user_feature(self):
        #特征是对每个类别的分数
        print 'extract'
        feature_num = len(self.__cate_ix_dict)
        user_feature_matrix = sparse.lil_matrix((len(self.__user_ix_list),feature_num))
        for user in self.user_score_dict:
            attr = self.user_score_dict[user]
            u_ix = self.__user_ix_dict[user]
            for cate in attr.get_all_cates():
                c_ix = self.__cate_ix_dict[cate]
                user_feature_matrix[u_ix,c_ix] = attr.get_cate_score(cate)
        print user_feature_matrix.shape
        print user_feature_matrix.nnz
        return user_feature_matrix 
    def cluster_user(self):
        user_feature_matrix = self.__extract_user_feature()
        user_feature_matrix = user_feature_matrix.tocsr()
        user_feature_matrix= MaxAbsScaler().fit_transform(user_feature_matrix)
        #model = DBSCAN(eps=0.5, min_samples=100).fit(user_feature_matrix)
        model = MiniBatchKMeans(n_clusters=50,max_iter=10000).fit(user_feature_matrix.toarray())
        labels = model.labels_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        print('Estimated number of clusters: %d' % n_clusters_)
        user_label_dict = dict()
        for user in self.__user_ix_dict:
            user_label_dict[user] = labels[self.__user_ix_dict[user]]
        return user_label_dict
    def neighbor_user(self,K):
        user_feature_matrix = self.__extract_user_feature()
        #user_feature_matrix = self.__nmf(user_feature_matrix)
        user_feature_matrix = self.__svd(user_feature_matrix)
        #user_feature_matrix = self.__remove_mean_by_row(user_feature_matrix)
        #nbrs = NearestNeighbors(K,n_jobs = -1).fit(user_feature_matrix)
        nbrs = NearestNeighbors(K,n_jobs = -1,algorithm="brute", metric="cosine").fit(user_feature_matrix)
        #distance,indices = nbrs.radius_neighbors(radius = 20)
        distance,indices = nbrs.kneighbors()
        print distance
        print indices
        user_nbrs_dict = dict()
        for user in self.__user_ix_dict:
            u_ix = self.__user_ix_dict[user]
            nbrs_ix = indices[u_ix]
            nbrs_list = [self.__user_ix_list[i] for i in nbrs_ix]
            user_nbrs_dict[user]= nbrs_list
        return user_nbrs_dict
    def __remove_mean_by_row(self,user_feature_matrix):
        for r_ix in range(user_feature_matrix.shape[0]):
            if user_feature_matrix.getrow(r_ix).nnz == 0:
                continue
            mean_row = user_feature_matrix.getrow(r_ix).sum()/ user_feature_matrix.getrow(r_ix).nnz

            for c_ix in range(user_feature_matrix.shape[1]):
                if user_feature_matrix[r_ix,c_ix] == 0:
                    continue
                user_feature_matrix[r_ix,c_ix] -= mean_row
        return user_feature_matrix
    def __compute_bias(self,user_feature_matrix):
        bias_global_val = user_feature_matrix.sum()/(user_feature_matrix != 0).sum()
        bias_user_matrix = user_feature_matrix.sum(1)/(user_feature_matrix != 0).sum(1)-bias_global_val
        bias_cate_matrix = user_feature_matrix.sum(0)/(user_feature_matrix != 0).sum(0)-bias_global_val
        for r_ix in range(user_feature_matrix.shape[0]):
            for c_ix in range(user_feature_matrix.shape[1]):
                if user_feature_matrix[r_ix,c_ix] == 0:
                    continue
                user_feature_matrix[r_ix,c_ix] -= bias_global_val + bias_user_matrix[r_ix,0]+bias_cate_matrix[0,c_ix]
        return user_feature_matrix,bias_global_val,bias_user_matrix,bias_cate_matrix
        
    def __nmf(self,user_feature_matrix):
        nmf = NMF(n_components=20,init='nndsvd')
        user_distribution = nmf.fit_transform(user_feature_matrix)
        return user_distribution
    def __svd(self,user_feature_matrix):
        svd = TruncatedSVD(n_components=50)
        user_distribution = svd.fit_transform(user_feature_matrix)
        return user_distribution



def candidate_with_user_cluster(fraw_str,splite_date,fitem_str,fout_str):
    cate_dict = utils.init_item_data(fitem_str)
    ucic = UCIC(fraw_str,splite_date)
    user_label_dict = ucic.cluster_user()
    label_user_dict = user2label(user_label_dict)
    fout = open(fout_str,'w')
    user_history_dict = ucic.user_history_dict
    i =0
    for user in user_label_dict:
        i+=1
        if i%1000 ==0: print i
        candidate_item_set = set()
        label = user_label_dict[user]
        if str(label) == '-1':
            continue
        users_neighbor_set = label_user_dict[label]
        for user_gbr in users_neighbor_set:
            candidate_item_set |= user_history_dict[user_gbr]
        candidate_item_set=remove_item_with_user_history_cate(ucic.user_score_dict[user],candidate_item_set,cate_dict)
        print >> fout,'%s,%s' %(user,'#'.join(candidate_item_set))
    fout.close()
        
def candidate_with_user_nbr_history(fraw_str,splite_date,fitem_str,fout_str):
    cate_dict = utils.init_item_data(fitem_str)
    ucic = UCIC(fraw_str,splite_date)
    user_nbrs_dict = ucic.neighbor_user(500)
    fout = open(fout_str,'w')
    user_history_dict = ucic.user_history_dict
    i =0
    for user in user_nbrs_dict:
        i+=1
        if i%1000 ==0: print i
        candidate_item_set = set()
        for user_nbr in user_nbrs_dict[user]:
            candidate_item_set |= user_history_dict[user_nbr]
        candidate_item_set=remove_item_with_user_history_cate(ucic.user_score_dict[user],candidate_item_set,cate_dict)
        print >> fout,'%s,%s' %(user,'#'.join(candidate_item_set))
    fout.close()
def remove_item_with_user_history_cate(attr,candidate_item_set,cate_dict):
    for cate in attr.get_all_cates():
        candidate_item_set -= cate_dict[cate]
    return candidate_item_set
    

def candiate_with_user_nbr_cate(fraw_str,splite_date,fitem_str,fout_str):
    cate_dict = utils.init_item_data(fitem_str)
    ucic = UCIC(fraw_str,splite_date)
    user_nbrs_dict = ucic.neighbor_user(10)
    fout = open(fout_str,'w')
    i =0
    for user in user_nbrs_dict:
        i+=1
        if i%1000 ==0: print i
        candidate_cate_set = set()
        for user_nbr in user_nbrs_dict[user]:
            attr = ucic.user_score_dict[user_nbr]
            candidate_cate_set |= set(attr.get_all_cates())

        attr = ucic.user_score_dict[user]
        candidate_cate_set -= set(attr.get_all_cates())
        candidate_item_set = set()
        for cate in candidate_cate_set:
            candidate_item_set|= cate_dict[cate]
        print >> fout,'%s,%s' %(user,'#'.join(candidate_item_set))
    fout.close()
            
def user2label(user_label_dict):
    label_user_dict = dict()
    for user in user_label_dict:
        label = user_label_dict[user]
        label_user_dict.setdefault(label,set())
        label_user_dict[label].add(user)
    return label_user_dict
def cluster_user(fraw_str,splite_date,fuser_label_str):
    ucic = UCIC(fraw_str,splite_date)
    user_label_dict = ucic.cluster_user()
    fout = open(fuser_label_str,'w')
    for user in user_label_dict:
        print >>fout,'%s,%s' %(user,user_label_dict[user])
    fout.close()

def main():
    data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST) 
    rule_dir = utils.get_data_dir(utils.FLAG_RULE)
    fraw_str = '%s/data_%s_%s' %(data_dir,utils.DATE_BEGIN.strftime('%m%d'),utils.DATE_END.strftime('%m%d'))  
    fitem_str = '%s/item' %(data_dir)
    fbuy_str = '%s/data_buy_%s'%(data_dir,utils.DATE_NEXT.strftime('%m%d'))
    fcandiadate_str = '%s/candidate_user_%s_%s' %(rule_dir,utils.DATE_BEGIN.strftime('%m%d'),utils.DATE_END.strftime('%m%d'))
    fuser_label_str = '%s/user_label_%s_%s' %(rule_dir,utils.DATE_BEGIN.strftime('%m%d'),utils.DATE_END.strftime('%m%d'))
    #cluster_user(fraw_str,begin_date,fuser_label_str)
    #candidate_with_user_cluster(fraw_str,begin_date,fitem_str,fcandiadate_str)
    #candidate_with_user_nbr_history(fraw_str,utils.DATE_BEGIN,fitem_str,fcandiadate_str)
    candiate_with_user_nbr_cate(fraw_str,utils.DATE_BEGIN,fitem_str,fcandiadate_str)
    
    utils.evaluate_res_except_history(fcandiadate_str,fbuy_str,True,fraw_str)
if __name__ == '__main__':
    main()
