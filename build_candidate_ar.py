#-*- coding:utf-8 -*-
#from fim import pfgrowth
"""
交易集构建：
userid,itemid1#itemid2#...(其购买过的item)
fin_str:data_[from date]_[to date]的文件名,[from date][ti date]间的records
fout_str:trans_[from_date]_[to_date] 文件名
"""
def build_trans_data(fin_str,fout_str):
    buy_dict = dict()
    with open(fin_str) as fin:
        for line in fin:
            #user_id,item_id,behavior_type,postion,cate,time
            cols = line.strip().split(',')
            #buy behavior
            if cols[2]=='4':
                buy_dict.setdefault(cols[0],[])
                buy_dict[cols[0]].append(cols[1])
    fout = open(fout_str,'w')
    for user_id in buy_dict:
        print >> fout,'%s,%s'%(user_id,'#'.join(buy_dict[user_id]))
    fout.close()
"""
构建 交易集的遍历
fin_str:trans_[from_data]_[to_date]
            #userid,itemid1#itemid2....
out:[item1,item2...]
"""
def iter_trans_data(fin_str):
    with open(fin_str) as fin:
        for line in fin:
            #userid,itemid1#itemid2....
            cols = line.strip().split(',')
            item_list = cols[1].split('#')
            yield item_list
"""
根据交集集，挖掘关联规则
min_supp:最小支持度 负数表示trans的绝对数量，非负数表示百分比
fin_str:交易集文件 trans_[from date]_[to date] 
"""
def mining_rule(min_supp = 2,fin_str):
    for r in fpgrowth(iter_trans_data(fin_str),target='r',supp=min_supp,zmin = 1,report='[S'):
        #r:(item_body,(item_head1,item_head2),[values])
        yield r

