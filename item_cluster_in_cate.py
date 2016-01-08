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
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import MiniBatchKMeans 
from sklearn import metrics
begin_date = datetime.datetime(2014,11,18)
end_date = datetime.datetime(2014,12,16)
td = datetime.timedelta(1)
split_td = datetime.timedelta(6)
splite_date = end_date - split_td
data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST) 
rule_dir = utils.get_data_dir(utils.FLAG_RULE)
class ICIC:
    def __init__(self):
        self.user_score_dict = None
    def __init_base_data(self,fitem_str,fin_str,splite_date):
        self.user_score_dict,_,_,self.user_dict = utils.init_base_data(fin_str,splite_date)
        self.cate_dict = dict()
        with open(fitem_str) as fin:
            for line in fin:
                cols = line.strip().split(',')
                #item,pos,cate
                self.cate_dict.setdefault(cols[-1],set())
                self.cate_dict[cols[-1]].add(cols[0])
    def __get_item_dict(self,cate):
        item_list = list(self.cate_dict[cate])
        item_dict = dict()
        for ix,item in enumerate(item_list):
            item_dict[item] = ix
        return item_dict
    def __extract_item_feature(self,cate):
        print 'start extract'
        item_dict = self.__get_item_dict(cate)
        #user 的四种行为频次
        #feature_num = len(user_dict)*4
        feature_num = len(self.user_dict)
        item_feature_matrix= sparse.lil_matrix((len(item_dict),feature_num))
        for user in self.user_score_dict:
            attr = self.user_score_dict[user]
            u_ix = self.user_dict[user]
            items = attr.get_items_by_cate(cate)
            if items == None:
                continue
            for item in items:
                i_ix = item_dict[item]
                item_feature_matrix[i_ix,u_ix] = attr.get_item_score(item)
        #io.mmwrite(fout_str,item_feature_matrix)
        return item_feature_matrix,item_dict
        print 'end extract'
    def __cluster_item(self,cate,fout_str):
        item_feature_matrix,item_dict  =self.__extract_item_feature(cate)
        #item_feature_matrix = io.mmread(fitem_feature_str) 
        item_feature_matrix = item_feature_matrix.tocsr()
        item_feature_matrix= MaxAbsScaler().fit_transform(item_feature_matrix)
        model = DBSCAN(eps=0.3, min_samples=10).fit(item_feature_matrix)
        #model = AgglomerativeClustering(n_clusters=50,linkage="average", affinity="cityblock").fit(item_feature_matrix.toarray())
        #model = MiniBatchKMeans(n_clusters=50,max_iter=10000).fit(item_feature_matrix.toarray())
        labels = model.labels_
        # Number of clusters in labels, ignoring noise if present.
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        print('Estimated number of clusters: %d' % n_clusters_)
        item_label_dict= dict()
        fout = open(fout_str,'w')
        for item in item_dict:
            print >> fout,'%s,%d' %(item,labels[item_dict[item]])
            item_label_dict[item] = labels[item_dict[item]]
        fout.close()
        return item_label_dict
    def cluster_item_with_cate(self,cate):
        fitem_label_str = '%s/item_label/item_label_%s_%s_%s' %(rule_dir,cate,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))
        if os.path.exists(fitem_label_str):
            print 'cate %s exists' %(cate)
            item_label_dict = dict()
            with open(fitem_label_str) as fin:
                for line in fin:
                    cols = line.strip().split(',')
                    item_label_dict[cols[0]]= cols[1]
            return item_label_dict
        else:
            if self.user_score_dict == None:
                fraw_str = '%s/data_%s_%s' %(data_dir,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))  
                fitem_str = '%s/item' %(data_dir)
                self.__init_base_data(fitem_str,fraw_str,begin_date)

                
            return self.__cluster_item(cate,fitem_label_str)

def main():
    #fraw_str = '%s/data_%s_%s' %(data_dir,splite_date.strftime('%m%d'),end_date.strftime('%m%d'))  
    fraw_str = '%s/data_%s_%s' %(data_dir,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))  
    fitem_str = '%s/item' %(data_dir)
    cate_id = '3064'
    fitem_feature_str = '%s/item_feature_%s_%s_%s' %(rule_dir,cate_id,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))
    fitem_label_str = '%s/item_label_%s_%s_%s' %(rule_dir,cate_id,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))
    #extract_item_feature(cate_id,fitem_str,fraw_str,fitem_feature_str)
    icic = ICIC()
    icic.cluster_item_with_cate(cate_id)


if __name__ == '__main__':
    main()

