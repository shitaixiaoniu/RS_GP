#-*- coding:utf-8-*
import sys
import os
import rs_utils as utils
import data_model as dm
import datetime
import numpy as np
from item_cluster_in_cate import ICIC 
from user_cluster_in_cate import UCIC


class BaseCIC:
    def __init__(self,fin_str,splite_date,fitem_str):
        self.splite_date = splite_date
        self.fin_str = fin_str
        self.splite_user_model = dm.UserHistoryDataModel(fin_str,splite_date)
        self.ci_model = dm.CateItemDataModel(fitem_str)
        self.icic = ICIC()
        self.rule_dir = utils.get_data_dir(utils.FLAG_RULE)
        self.full_user_model = None

    def __init_base_data(self):
        if self.splite_date == utils.DATE_BEGIN:
            self.full_user_model = self.splite_user_model
        else:
            self.full_user_model = dm.UserHistoryDataModel(fin_str,utils.DATE_BEGIN)

    def _cluster_item_in_cate(self,cate):
        fitem_label_str = '%s/item_label/item_label_%s_%s_%s' %(self.rule_dir,cate,utils.DATE_BEGIN.strftime('%m%d'),utils.DATE_END.strftime('%m%d'))
        if os.path.exists(fitem_label_str):
            print 'cate %s exists' %(cate)
            item_label_dict = dict()
            with open(fitem_label_str) as fin:
                for line in fin:
                    cols = line.strip().split(',')
                    item_label_dict[cols[0]]= cols[1]
            return item_label_dict
        else:
            #icic 的data 未初始化
            if self.icic.user_score_dict is None:
                if self.full_user_model is  None:
                    self.__init_base_data()
                self.icic.init_base_data(self.full_user_model,self.ci_model)
                
            return self.icic.cluster_item(cate,fitem_label_str)
    def change2label(self,user_label_dict):
        label_user_dict = dict()
        for user in user_label_dict:
            label = str(user_label_dict[user])
            label_user_dict.setdefault(label,set())
            label_user_dict[label].add(user)
        return label_user_dict
