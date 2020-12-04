import csv

a= [['test1','201906011200','login'],['test2','20190601300','login'],['test1','201906011300','logout'],['test2','201906011400','logout'],['test1','201905030100','login'],['test1','201905030200','logout']\
    ,['test1','201905311100','login'],['test1','201905311200','logout'],['test1','201905011200','login'],['test1','201905011200','logout']]
with open("test1.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(a)



