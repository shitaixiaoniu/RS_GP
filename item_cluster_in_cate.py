#-*- coding:utf-8-*
import sys
import rs_utils as utils
import data_model as dm
import os
from scipy import sparse
from scipy import io
from sklearn.preprocessing import MaxAbsScaler 
from sklearn.cluster import DBSCAN
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import MiniBatchKMeans 
from sklearn import metrics
class ICIC:
    def __init__(self):
        self.user_score_dict = None
    def init_base_data(self,uh_data_model,ci_data_model):
        self.user_score_dict= uh_data_model.user_score_dict
        self.user_dict = uh_data_model.user_ix_dict
        self.cate_dict = ci_data_model.cate_dict
        
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
    def cluster_item(self,cate,fout_str):
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
def test_icic():
    icic = ICIC() 
    cate = '3064'
    rule_dir = utils.get_data_dir(utils.FLAG_RULE)
    fitem_label_str = '%s/item_label/test_item_label_%s_%s_%s' %(rule_dir,cate,utils.DATE_BEGIN.strftime('%m%d'),utils.DATE_END.strftime('%m%d'))
    if os.path.exists(fitem_label_str):
        print 'cate %s exists' %(cate)
        item_label_dict = dict()
        with open(fitem_label_str) as fin:
            for line in fin:
                cols = line.strip().split(',')
                item_label_dict[cols[0]]= cols[1]
        return item_label_dict
    else:
        if icic.user_score_dict == None:
            data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST) 
            fraw_str = '%s/data_%s_%s' %(data_dir,utils.DATE_BEGIN.strftime('%m%d'),utils.DATE_END.strftime('%m%d'))  
            fitem_str = '%s/item' %(data_dir)
            user_data_model = dm.UserHistoryDataModel(fraw_str,utils.DATE_BEGIN)
            ci_data_model = dm.CateItemDataModel(fitem_str)
            icic.init_base_data(user_data_model,ci_data_model)
            
        return icic.cluster_item(cate,fitem_label_str)


if __name__ == '__main__':
    test_icic()

