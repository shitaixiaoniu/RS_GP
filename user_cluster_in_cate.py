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
        feature_num = len(self.__cate_ix_dict)
        user_feature_matrix = sparse.lil_matrix((len(self.__user_ix_list),feature_num))
        for user in self.user_score_dict:
            attr = self.user_score_dict[user]
            u_ix = self.__user_ix_dict[user]
            for cate in attr.get_all_cates():
                c_ix = self.__cate_ix_dict[cate]
                user_feature_matrix[u_ix,c_ix] = attr.get_cate_score(cate)
        return user_feature_matrix 
    def cluster_user(self):
        user_feature_matrix = self.__extract_user_feature()
        user_feature_matrix = user_feature_matrix.tocsr()
        user_feature_matrix= MaxAbsScaler().fit_transform(user_feature_matrix)
        model = DBSCAN(eps=0.3, min_samples=10).fit(user_feature_matrix)
        labels = model.labels_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        user_label_dict = dict()
        for user in self.__user_ix_dict:
            user_label_dict[user] = labels[self.__user_ix_dict[user]]
        return user_label_dict

def candidate_with_user_cluster(fraw_str,splite_date,fout_str):

    ucic = UCIC(fraw_str,splite_date)
    user_label_dict = ucic.cluster_user()
    label_user_dict = user2label(user_label_dict)
    fout = open(fout_str,'w')
    user_history_dict = ucic.user_history_dict
    for user in user_label_dict:
        candidate_item_set = set()
        label = user_label_dict[user]
        if str(label) == '-1':
            continue
        users_neighbor_set = label_user_dict[label]
        for user_gbr in users_neighbor_set:
            candidate_item_set |= user_history_dict[user_gbr]
        print >> fout,'%s,%s' %(user,'#'.join(candidate_item_set))
    fout.close()
        
            
def user2label(user_label_dict):
    label_user_dict = dict()
    for user in user_label_dict:
        label = user_label_dict[user]
        label_user_dict.setdefault(label,set())
        label_user_dict[label].add(user)
    return label_user_dict
def main():
    begin_date = datetime.datetime(2014,11,18)
    end_date = datetime.datetime(2014,12,17)
    td = datetime.timedelta(1)
    split_td = datetime.timedelta(6)
    splite_date = end_date - split_td
    data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST) 
    rule_dir = utils.get_data_dir(utils.FLAG_RULE)
    fraw_str = '%s/data_%s_%s' %(data_dir,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))  
    buy_date = datetime.datetime(2014,12,18)
    fbuy_str = '%s/data_buy_%s'%(data_dir,buy_date.strftime('%m%d'))
    fcandiadate_str = '%s/candidate_user_%s_%s' %(rule_dir,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))
    candidate_with_user_cluster(fraw_str,begin_date,fcandiadate_str)
    
    utils.evaluate_res_except_history(fcandiadate_str,fbuy_str,True,fraw_str)
if __name__ == '__main__':
    main()
