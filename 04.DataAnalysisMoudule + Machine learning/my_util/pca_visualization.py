import numpy as np 
import pandas as pd 
import matplotlib as mpl 
import matplotlib.pyplot as plt 
# 한글폰트 사용
mpl.rc('font', family='Malgun Gothic')
mpl.rc('axes', unicode_minus=False)
def visual(marker_count, df, save):
    markers = ['s', 'o', '^', 'p','D','*','+','>','X','1']
    if marker_count < len(df['target'].unique()):
        marker_count = len(df['target'].unique())
    markers = markers[:marker_count]
    fig, asx = plt.subplots(figsize=(12,6), ncols=2, nrows=1)
    diff = ['target', 'cluster']
    for k, item in enumerate(diff):
        ax = asx[k]
        for i,marker in enumerate(markers):
            x_axis_data = df[df[item] == i]['pca_x']
            y_axis_data = df[df[item] == i]['pca_y']
            ax.scatter(x_axis_data, y_axis_data, marker=marker)

        if k == 0:
            ax.set_title('원본 데이터')
        else:
            ax.set_title('군집화한 데이터 ')
        ax.set_xlabel('PCA 1')
        ax.set_ylabel('PCA 2')
    plt.savefig(save)