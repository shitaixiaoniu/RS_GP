#-*- coding:utf-8-*
import sys
import os
import rs_utils as utils
import data_model as dm
import datetime
import numpy as np
import heapq
from item_cluster_in_cate import ICIC 
from user_cluster_in_cate import UCIC
from base_candidate_with_item_cluster import BaseCIC


class CN(BaseCIC):
    
    def candiate_with_user_nbr_cate(self,fout_str):
        print 'nbr begin '
        user_data_model = self.splite_user_model 
        ucic = UCIC(user_data_model)
        user_nbrs_dict,user_nbrs_similarity_dict  = ucic.neighbor_user(50)
        print 'nbr end'
        fout = open(fout_str,'w')
        i =0
        for user in user_nbrs_dict:
            i+=1
            if i%1000 ==0: print i
            candidate_cate_set = set()
            for user_nbr in user_nbrs_dict[user]:
                attr = user_data_model.user_score_dict[user_nbr]
                candidate_cate_set |= set(attr.get_all_cates())
    
            attr = user_data_model.user_score_dict[user]
            candidate_cate_set -= set(attr.get_all_cates())
            if len(candidate_cate_set) == 0:
                continue
            if len(user_nbrs_dict[user]) != len(user_nbrs_similarity_dict[user]):
                raise ValueError('nbrs and similarity lenghth not equal')
            candidate_item_set = self.__get_candidate_item_in_cate(user,user_nbrs_dict[user],candidate_cate_set,user_nbrs_similarity_dict[user]) 
            print >> fout,'%s,%s' %(user,'#'.join(candidate_item_set))
        fout.close()

    def __get_candidate_item_in_cate(self,user,nbrs_list,candidate_cate_set,nbrs_similarity_list):
        user_score_dict = self.splite_user_model.user_score_dict
        cate_dict  = self.ci_model.cate_dict 
        cate_score_dict = self.__compute_cate_score(user,nbrs_list,candidate_cate_set,nbrs_similarity_list)
        top_k_cate_list = heapq.nlargest(50,cate_score_dict.items(),key = lambda x: x[1])
        cate_score_dict = dict(top_k_cate_list)
        #只取top k 的cate 聚类
        total_score = sum(cate_score_dict.values())
        rs_num = 3000
        candidate_item_set = set()
        for cate in cate_score_dict:
            #candidate_item_set |= cate_dict[cate]
            need_item_num = int(rs_num*cate_score_dict[cate]/total_score)
            #need_item_num = 10
            #print need_item_num
            if need_item_num >= len(cate_dict[cate]):
                candidate_item_set |= cate_dict[cate]
            else:
                """
                #methos1: top k 的item
                item_set = cate_dict[cate]
                candidate_item_set |= self.__get_top_items_in_cate(need_item_num,item_set,nbrs_list,nbrs_similarity_list)
                """
                #method2:对cate 内聚类
                item_labels_dict = self._cluster_item_in_cate(cate)
                #根据近邻历史行为 计算对各子聚类的喜好度
                label_score_dict = dict()
                for item in cate_dict[cate]:
                    label = str(item_labels_dict[item])
                    if label  == '-1':
                        continue
                    label_score_dict.setdefault(label,0)
                    label_score_dict[label] += self.__compute_item_score(nbrs_list,item,nbrs_similarity_list)
                sorted_label_list = sorted(label_score_dict.items(), key=lambda x: x[1], reverse=True)
                label_item_dict = self.change2label(item_labels_dict)
                #根据由高到低排序的子类依次添加其对应的item 作为候选item
                for label,val in sorted_label_list:
                    if val == 0 or len(candidate_item_set) + len(label_item_dict[label]) > need_item_num:
                        break
                    candidate_item_set |= label_item_dict[label]
        return candidate_item_set
 
    def __compute_cate_score(self,user,nbrs_list,candidate_cate_set,nbrs_similarity_list):

        cate_score_dict = dict()
        for cate in candidate_cate_set:
            cate_score_dict[cate] = 0.0
            total_similarity  = 0.0
            for nbr_ix,nbr in enumerate( nbrs_list):
                score = self.splite_user_model.user_score_dict[nbr].get_cate_score(cate)
                if score != 0:
                    #cate_score_dict[cate] += (score - self.splite_user_model.user_score_dict[nbr].get_score_mean()) * nbrs_similarity_list[nbr_ix]
                    #cate_score_dict[cate] += score  * nbrs_similarity_list[nbr_ix]
                    #cate_score_dict[cate] += score
                    total_similarity += nbrs_similarity_list[nbr_ix]
                    #total_similarity += 1
            #cate_score_dict[cate] = round(cate_score_dict[cate]/total_similarity,4)
            cate_score_dict[cate] = total_similarity
            #cate_score_dict[cate] += self.splite_user_model.user_score_dict[user].get_score_mean() 
        return cate_score_dict
    
    def __compute_item_score(self,nbrs_list,item,nbrs_similarity_list):
        item_score = 0
        for nbr_ix, nbr in enumerate(nbrs_list):
            #item_score 为所有近邻对其评分的均值
            #item_score += self.splite_user_model.user_score_dict[nbr].get_item_score(item)
            #item_score 为分数不为0 的近邻的相似之和
            if self.splite_user_model.user_score_dict[nbr].get_item_score(item) != 0:
                item_score += nbrs_similarity_list[nbr_ix] 
                #item_score += self.splite_user_model.user_score_dict[nbr].get_item_score(item)
            
        #item_score /= len(nbrs_list)

        return item_score
    
    def __get_top_items_in_cate(self,need_item_num,item_set,nbrs_list,nbrs_similarity_list):
        item_score_dict = dict()
        for item in item_set:
            item_score_dict[item] = self.__compute_item_score(nbrs_list,item,nbrs_similarity_list)
        top_k_item_list = heapq.nlargest(need_item_num,item_score_dict.items(),key = lambda x: x[1])
        candidate_item_set = set()
        for item,val in top_k_item_list:
            if val == 0:
                break
            candidate_item_set.add(item)
        return candidate_item_set


        

def main():
    data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST) 
    rule_dir = utils.get_data_dir(utils.FLAG_RULE)
    fraw_str = '%s/data_%s_%s' %(data_dir,utils.DATE_BEGIN.strftime('%m%d'),utils.DATE_END.strftime('%m%d'))  
    fitem_str = '%s/item' %(data_dir)
    fres_cate_str = '%s/test_candidate_nbr_cate_%s_%s' %(rule_dir,utils.DATE_SPLIT.strftime('%m%d'),utils.DATE_END.strftime('%m%d'))
    fbuy_str = '%s/data_buy_%s'%(data_dir,utils.DATE_NEXT.strftime('%m%d'))
    cn = CN(fraw_str,utils.DATE_SPLIT,fitem_str)
    cn.candiate_with_user_nbr_cate(fres_cate_str)
    utils.evaluate_res_except_history(fres_cate_str,fbuy_str,True,fraw_str)

if __name__ == '__main__':
    main()
 
