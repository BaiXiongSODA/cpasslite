import re

import pandas as pd
import pdfplumber


def read(path):
    # 文件路径
    pdf = pdfplumber.open(path)
    classArray = []
    dfArray = []

    # 数据读取
    for item in range(len(pdf.pages)):
        # 页数读取
        page = pdf.pages[item]
        table = page.extract_table()
        if table is not None:
            dfArray = dfArray + table

    # 转换成dataframe
    dfArray = pd.DataFrame(dfArray)

    userInfoLine = dfArray[0][0]
    dfArray[2] = dfArray[2].fillna('#####')
    drop_line = dfArray[(dfArray[2] == '#####')].index.tolist()
    dfArray.drop(drop_line, inplace=True)

    # 空值替换
    dfArray[dfArray == ""] = None  # 先将空转化为空值
    dfArray = dfArray.fillna(value=None, method='ffill', axis=0, limit=None)
    newDf = pd.DataFrame()

    # 提取课程名称
    newDf['className'] = dfArray[2].str.extract('教学班(.*?)教学班组成').astype('string')
    newDf['className'].replace(regex=True, inplace=True, to_replace='-[0-9a-zA-Z]*', value=r'')
    dfArray[2].replace(regex=True, inplace=True, to_replace='\\n.*?[◇◆]', value=r'')
    dfArray[2].replace(regex=True, inplace=True, to_replace='\\n', value=r'')
    newDf['weekList'] = dfArray[2].str.extract('周数(.*?)地点').astype('string')
    newDf['whichWeek'] = dfArray[0]
    newDf['classNum'] = dfArray[1]
    newDf['classroom'] = dfArray[2].str.extract('地点(.*?)教师').astype('string')
    newDf['teacher'] = dfArray[2].str.extract('教师(.*?)教学班').astype('string')
    newDf['credit'] = dfArray[2].str.extract('学分(.*)').astype('string')
    newDf.replace(regex=True, inplace=True, to_replace='[: ]', value=r'')
    newDf.replace(regex=True, inplace=True, to_replace='星期⼀', value=r'星期一')
    newDf.replace(regex=True, inplace=True, to_replace='星期⼆', value=r'星期二')
    newDf.head(2)

    try:
        dfJson = newDf.to_dict(orient="records")
    except:
        return 'err'

    userInfo = {
        'name': re.findall(r"(.*?)课表", userInfoLine)[0],
        'year': re.findall(r"([0-9]{4}-)", userInfoLine)[0] + re.findall(r"第([12])学期", userInfoLine)[0],
        'studentNum': re.findall(r"学号.*?([0-9]{15})", userInfoLine)[0],
    }
    output = {
        'userInfo': userInfo,
        'classData': dfJson,
    }
    return output
