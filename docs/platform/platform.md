# 1. 总目录
## 1.1 文档使用说明
本文档意在向读者说明开放研究实验室里支持的python方法和调用接口，方便读者更好的上手研究。文档将重点介绍与自研API相关的调用说明，而更底层的方法包仅附上官方链接，请自行查看。



举一个简单的例子，如果学者不知道如何用进行数据处理操作，然后使用面板固定效应回归获得模型结果，则：

+ 首先应阅读pandas相关的面板数据处理方法（外部链接）
+ 然后阅读linearmodels.PanelOLS方法的使用指南（外部链接）
+ 最后阅读平台的安全打印结果说明，输出PanelOLS模型结果（本文档）



由于笔者精力有限，输入、输出章节内容仅为举例，不保证覆盖全部已支持方法，**<font style="color:#DF2A3F;">部分方法由于当前使用频次较低未纳入文档说明范围</font>**，但读者可通过python方法速查手册进行快速检索，确认是否平台已支持。

## 1.2 可用Python包清单
目前实验室的python运行版本为3.8.6，已经安装好的python包和对应版本号如下所示。如所需Python包未在列表内出现，则说明该方法无法在实验室内直接使用。



| **名称** | **版本号** | **说明** | **链接** |
| --- | --- | --- | --- |
| **CausalInference** | 0.1.3 | 用于因果推断的python库 | [causalinference包说明](https://causalinferenceinpython.org/#main-features) |
| **econml** | 0.12.0 | 通过机器学习方法进行因果推断的python库 | [econml包说明](https://econml.azurewebsites.net/)[](https://seaborn.pydata.org/index.html) |
| **lifelines** | 0.25.11 | 用于生存分析的python库 | [lifelines包说明](https://lifelines.readthedocs.io/en/latest/Survival%20Regression.html) |
| **linearmodels ** | 4.25 | linearmodels是python语言的扩展程序包，提供用户进行一些常用的线性模型的回归推断和预测，包括面板回归模型和工具变量模型等。 | [linearmodels手册](https://bashtage.github.io/linearmodels/doc/index.html) |
| **math ** | 内置 | math是python标准库，提供了各种数学运算。 | [math包说明](https://docs.python.org/3/library/math.html) |
| **numpy** | 1.23.4 | NumPy是python语言的扩展程序库，支持高阶大量的维度数组与矩阵运算，此外也针对数组运算提供大量的数学函数库。 | [numpy快速入门](https://numpy.org/doc/stable/user/quickstart.html) |
| **pandas** | 1.4.1 | pandas是python语言的用于数据操纵和分析的程序库。特别是，它提供操纵数值表格和时间序列的数据结构和运算操作。 | [pandas说明](https://www.datacamp.com/community/tutorials/pandas-tutorial-dataframe-python) |
| **pasty** | 0.5.1 | patsy是一个python库，用于描述统计模型（尤其是线性模型，或具有线性组件的模型）和构建设计矩阵。Patsy为python带来了r“formulas”的便利。它受到R和S中使用的公式迷你语言的启发并与之兼容。 | [pasty包说明](https://patsy.readthedocs.io/en/latest/) |
| **py4etrics** | 0.1.7 | This module is for Truncated Regression, Tobit Model, Heckit Model | [py4etrics说明](https://py4etrics-github-io.translate.goog/?_x_tr_sl=ja&_x_tr_tl=en&_x_tr_hl=zh-CN) |
| **scipy** | 1.5.4 | SciPy是一个开源的python算法库和数学工具包。 SciPy包含的模块有最优化、线性代数、积分、插值、特殊函数、快速傅里叶变换、信号处理和图像处理、常微分方程求解和其他科学与工程中常用的计算。 | [scipy使用文档](https://docs.scipy.org/doc/scipy/reference/) |
| **seaborn** | 0.11.1 | 基于matplotlib的图形可视化python库。提供了高度交互式界面，便于用户能够做出各种有吸引力的统计图表。 | [seaborn包说明](https://seaborn.pydata.org/index.html) |
| **sklearn** | 0.24.2 | sklearn是一个python第三方提供的非常强力的机器学习库 | [sklearn包说明](https://scikit-learn.org/stable/) |
| **statsmodels** | 0.13.2 | Statsmodels是Python语言的扩展程序包，允许用户浏览数据，估计统计模型并执行统计测试。对于不同类型的数据和每个估计量，可以使用大量的描述性统计，统计检验，绘图函数和结果统计。 | [statsmodels 用户手册](https://www.statsmodels.org/stable/user-guide.html#) |
| **igraph** | 0.11.3 | <font style="color:rgb(51, 51, 51);">用于创建和操作无向和有向图的高效Python库。用户可以快速地构建图形，计算图形的一些基本属性（例如点度，路径长度等），并实现一些图算法（如最短路径，最大流，最小生成树等），它在社会网络分析、生物信息学和其他需要图形和网络分析的领域中非常有用。</font> | [igraph包说明](https://python.igraph.org/en/stable/) |




## 1.3 python方法速查手册
速查手册里覆盖全部可输出的统计方法和模型（安全打印白名单），不在手册里的模型/方法依然可以运行，但在注册进入安全打印白名单之前无法直接输出。



安全打印支持方法调用**<font style="color:#DF2A3F;">通用格式</font>**为：

+ ant_print_all(数据或模型结果对象, model_attr=['参数1','参数2'], model_method='参数')
+ 各参数需要根据“接口类别”放入到正确的位置，model_attr支持多参数同时打印，model_method每次调用仅支持输入一个参数。

[7.python速查手册](https://www.yuque.com/ce8oxw/ngd5zk/yic0n4ct0az4gssr#VGKx)

+ 受笔者Stata与计量经济知识所限，部分模型的描述存在不准确的问题，对应Stata方法也有较多缺失。**<font style="color:#DF2A3F;">我们欢迎学者指正、补充。</font>**
+ 包括本文档在内的各类实验室说明文档，学者提供的有效建议都会被后台记录，我们会根据贡献度主动联系发放惊喜礼包，包括但不限于精美小礼品、夏令营内推特权、尖峰学术研讨会邀请函等。

# 2. 输入：引入方法与数据
## 2.1 环境配置
导入python程序包

```python
import math
import pandas as pd 
import numpy as np 
import statsmodels.api as sm 
import scipy 
import linearmodels as lm
import seaborn as sns
import lifelines
import causalinferences
import sklearn
import econml
```



由于数据可用不可见的原则，实验室禁止了“print”/“plot”函数，但是提供了特定的输出接口，来输出模型、统计、假设检验以及绘图。

```python
from marvel import AntPrint
# 或者
from marvel.AntPrint import ant_print_all
```

## 2.2 读取数据
`**ant_read_data(table_name, cols=None)**`

实验室数据读取函数

<font style="color:#1890ff;">输入参数：</font>

table_name: 表名称, str

cols: 需要读取的列名，默认None，读取全部列

<font style="color:#1890FF;">举例：</font>

<img src="https://cdn.nlark.com/yuque/0/2021/png/375425/1640661502629-5cbd2aae-8243-47d6-b20a-2ffb686f99f8.png" width="746.98291015625" title="" crop="0,0,1,1" id="u966df9c4" class="ne-image">

该项目中可以读取的数据表在左边栏，表名单击可复制。

```python
from marvel.AntPrint import ant_read_data # 读取数据模块
#读取数据
df = ant_read_data('test_data')
```

# 3. 输出：文本内容
## 3.1 通用打印说明
`**ant_print_all(model, *args, model_attr=None, model_method=None, **kwargs)**`

实验室可以用这个函数输出假设检验/模型结果，支持白名单中的函数和模型。

<font style="color:#1890ff;">输入参数：</font>

model：函数/模型

*args：模型方法/函数需要的变量

model_attr：模型属性，字符串/字符串列表

model_method: 模型方法，字符串

**kwargs：模型方法/函数需要的变量，键值对输入

<font style="color:#1890FF;">举例：</font>

```python
result = sm.Probit(y, x).fit()
ant_print_all(result, model_attr=['params','pvalues'], model_method='summary')
```

上述代码将打印出模型的系数、p值，以及summary信息。



**注意：**

model_attr输入为模型的属性，例如result.params

model_method输入为模型的方法，例如result.summary()

这两者区别是在不使用接口打印时是否需要加“()”，在下文中我们对模型支持的参数标记了是属性还是方法

对于函数的打印，不需要传入model_method与model_attr参数

## 3.2 打印统计结果 
### DataFrame
corr（方法）

**说明**

各参数的用法同pandas.DataFrame.corr

[https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.corr.html](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.corr.html)

```python
ant_print_all(df, model_method="corr")
```

nunique（方法）

**说明**

各参数的用法同pandas.DataFrame.nunique

[https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.nunique.html?highlight=nunique#pandas.DataFrame.nunique](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.nunique.html?highlight=nunique#pandas.DataFrame.nunique)

```python
ant_print_all(df, model_method="nunique")
```

describe（方法）

**说明**

<font style="color:#1890FF;">输入参数：</font>

df: python的dataframe格式的数据

des: 一个数据列表，需要做统计的参数; 如果不输入，则展示"describe"对应的结果

| **des支持的参数** | **说明** |
| --- | --- |
| shape | 数据行数列数 |
| dtypes | 每列的数据类型 |
| describe | 描述性统计 |
| mean | 平均值 |
| std | 标准差 |
| pct_1 | 1分位数 |
| pct_99 | 99分位数 |
| pct_5 | 5分位数 |
| pct_95 | 95分位数 |


```python
# 打印描述性统计
ant_print_all(df, model_method="describe")
# 打印样本量和数据类型
ant_print_all(df, model_method="describe", des=['shape', 'dtypes'])
# 打印分位数
ant_print_all(df, model_method="describe", des=["pct_5"])
```

value_counts（方法）

**说明**

[https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.value_counts.html](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.value_counts.html)



```python
ant_print_all(df, model_method="value_counts", normalize=True)
```

describe_by_discrete（方法）

**说明**

针对离散型的key进行分组统计

<font style="color:#1890FF;">输入参数：</font>

df：dataframe类型的数据

group_by_columns：用于分组的key列，为离散型（一般为分类变量）

cal_columns：用于计算的列

fun_list：需要计算的统计量，默认为 计数函数"count"

```python
ant_print_all(df, model_method="describe_by_discrete", group_by_columns=["year"], cal_columns=["passengers"], fun_list=["sum"])
```

describe_by_continuous（方法）

**说明**

针对连续型key进行分组统计再绘图

<font style="color:#1890FF;">输入参数：</font>

df：dataframe类型的数据

group_by_columns：用于分组的key列，为连续型（一般为数值型变量）

cal_columns：用于计算的列

q：int型 / list，分箱数量/切分点列表

cut_strategy："quantile" / "uniform"

"quantile"：等量分组，尽量保证分组后，每个组内的样本数相等

"uniform"：等距分组，保证分组后，组间距离相等

fun_list：需要计算的统计量，默认为 计数函数"count"

```python
ant_print_all(df, model_method="describe_by_continuous", group_by_columns=["year"], cal_columns=["passengers"], q = [0.2, 0.4, 0.7, 1], fun_list="sum")
```

### Series
unique（方法）

**说明**

[https://pandas.pydata.org/docs/reference/api/pandas.Series.unique.html](https://pandas.pydata.org/docs/reference/api/pandas.Series.unique.html)

```python
import pandas as pd
from marvel.AntPrint import ant_print_all
ss1 = pd.Series([1,2,3,4,5,67,7,7,8,5])
# 展示不同值
ant_print_all(ss1, model_method="unique")

```

value_counts（方法）

**说明**

[https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html)

```python
import pandas as pd
from marvel.AntPrint import ant_print_all
ss1 = pd.Series([1,2,3,4,5,67,7,7,8,5])
# 按照数值分组计数
ant_print_all(sr, model_method="value_counts")
```

### DescrStatsW
| **支持的方法** | **说明** |
| --- | --- |
| mean | 加权平均 |
| sum | 加权和 |
| std | 默认自由度调整的标准差 |
| std_mean | 加权平均标准差 |
| var | 默认自由度调整的方差 |
| corrcoef | 默认自由度的加权相关系数 |
| cov | 加权协方差 |


**说明**

**计算描述性统计量**

各参数用法statsmodels.stats.weightstats.DescrStatsW

[https://www.statsmodels.org/stable/generated/statsmodels.stats.weightstats.DescrStatsW.html](https://www.statsmodels.org/stable/generated/statsmodels.stats.weightstats.DescrStatsW.html)

```python
from statsmodels.stats.weightstats import DescrStatsW
x1_2d = 1.0 + np.random.randn(120, 3)
w1 = np.random.randint(3, 10, 120)
w2 = pd.DataFrame(w1)
w2 = pd.concat([w2,w2,w2], axis = 1)
d1 = DescrStatsW(pd.DataFrame(x1_2d), weights=w2)
ant_print_all(d1, model_attr=["mean"])
```

## 3.3 打印模型结果
### PanelOLS 固定效应面板回归
PanelOLS 文档 [https://bashtage.github.io/linearmodels/doc/panel/models.html#linearmodels.panel.model.PanelOLS](https://bashtage.github.io/linearmodels/doc/panel/models.html#linearmodels.panel.model.PanelOLS)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| linearmodels | PanelOLS | params | 回归结果参数（属性） |
|  |  | <font style="color:#404040;">pvalues</font> | p-值（属性） |
|  |  | tstats | t-值（属性） |
|  |  | <font style="color:#404040;">rsquared</font> | R方（属性） |
|  |  | <font style="color:#404040;">std_errors</font> | 标准误差（属性） |
|  |  | nobs | 样本量（属性） |
|  |  | <font style="color:#404040;">summary</font> | 回归结果汇总summary（属性） |
| | | conf_int | 输出置信区间 |
| | | cov | 协方差（属性）  |


**举例**

```python
import pandas as pd 
import numpy as np 
import linearmodels as lm
# define your own y in here
# define your own x in here 
model = lm.PanelOLS(y, X, entity_effects=True, time_effects=True,drop_absorbed=True)
model_result = model.fit(cov_type='clustered', cluster_entity=True, cluster_time=True)

# 下面的代码将输出模型参数、p值、R方，样本量，以及模型结果summary
ant_print_all(model_result, model_attr=['params','pvalues', 'rsquared', 'nobs', 'summary', 'cov', 'std_errors', 'tstats']) 
ant_print_all(model_result, model_method='conf_int', level=0.95) 
```

### RandomEffects 随机效应面板回归
RandomEffects 文档 

[https://bashtage.github.io/linearmodels/panel/panel/linearmodels.panel.model.RandomEffects](https://bashtage.github.io/linearmodels/panel/panel/linearmodels.panel.model.RandomEffects)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| linearmodels | RandomEffects | params | 回归结果参数（属性） |
|  |  | pvalues | p-值（属性） |
|  |  | tstats | t-值（属性） |
|  |  | rsquared | R方（属性） |
|  |  | std_errors | 标准误差（属性） |
|  |  | nobs | 样本量（属性） |
|  |  | summary | 回归结果汇总summary（属性） |


**举例**

```python
import numpy as np 
import linearmodels as lm

# define your own y in here
# define your own x in here 
model_result = lm.RandomEffects(y, X).fit()

# 下面的代码将输出模型参数、p值、R方，样本量，以及模型结果summary
ant_print_all(model_result, model_method=['params','pvalues', 'rsquared', 'nobs','summary']) 
```

### IV2SLS 工具变量法两阶段回归
IV2SLS 文档



[https://bashtage.github.io/linearmodels/iv/iv/linearmodels.iv.model.IV2SLS.html](https://bashtage.github.io/linearmodels/iv/iv/linearmodels.iv.model.IV2SLS.html)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| linearmodels | IV2SLS | params | 回归结果参数（属性） |
|  |  | pvalues | p-值（属性） |
|  |  | tstats | t-值（属性） |
|  |  | rsquared | R方（属性） |
|  |  | rsquared_adj | 调整后的R方（属性） |
|  |  | std_errors | 标准误差（属性） |
|  |  | nobs | 样本量（属性） |
|  |  | summary | 回归结果汇总summary（属性） |
| | | sargan | Sargan检验（属性） |
| | | basmann | Basmann检验（属性） |
| | | wooldridge_score | Wooldridge’s score检验（属性） |
| | | wooldridge_overid | 同上（属性） |
| | | anderson_rubin | Anderson-Rubin检验（属性） |
| | | basmann_f | Basmann’s F检验（属性） |
| | | first_stage | 一阶段信息 (属性) |
| | | durbin | Durbin's检验（方法） |
| | | wu_hausman | Wu-Hausman检验（方法） |


**举例**

```python
import numpy as np 
import linearmodels as lm


# define your own y in here
# define your own x in here 
# define your own Endogenous variable E
# define your own z (instrument variable)

model_result = lm.IV2SLS(y, x, E, z).fit()

# 下面的代码将输出模型参数、p值、R方，样本量，以及模型结果summary
ant_print_all(model_result, model_attr=['params','pvalues', 'rsquared', 'nobs','summary']) 
```

### AbsorbingLS 吸收回归（类似stata中的reghdfe）
AbsorbingLS 文档

[https://bashtage.github.io/linearmodels/iv/absorbing/linearmodels.iv.absorbing.AbsorbingLS.html](https://bashtage.github.io/linearmodels/iv/absorbing/linearmodels.iv.absorbing.AbsorbingLS.html)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| linearmodels | AbsrobingLS | summary | 回归结果汇总summary（属性） |


**举例**

```python
from linearmodels.iv.absorbing import AbsorbingLS, Interaction
df = ant_read_data("wage_panel")
y = df["lwage"]
x = df[["expersq"]]
cats = pd.DataFrame([pd.Categorical(df[name]) for name in ["year", "married"]])
model = AbsorbingLS(y, x, absorb=cats)
result = model.fit(method="lsmr", use_cache=False)
ant_print_all(result, model_attr="summary")
```

### OLS 普通线性回归
OLS 文档 [https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLS.html](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLS.html)

OLS 例子 [https://www.statsmodels.org/stable/examples/notebooks/generated/ols.html](https://www.statsmodels.org/stable/examples/notebooks/generated/ols.html)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| statsmodels | OLS  | params | 回归结果参数（属性） |
|  |  | pvalues | p-值（属性） |
|  |  | tvalues | t-值（属性） |
|  |  | rsquared | R方（属性） |
|  |  | rsquared_adj | 调整的R方（属性） |
|  |  | bse | 标准误差（属性） |
|  |  | nobs | 样本量（属性） |
| | | f_test | F测试（方法） |
|  |  | summary | 回归结果汇总summary（方法） |
|  |  | summary2 | 回归结果汇总summary2（方法） |


**举例：**

```python
import pandas as pd 
import numpy as np 
import statsmodels.api as sm 


# define your own y in here
# define your own x in here 
model_result = sm.OLS(y, X).fit()

# 下面的代码将输出模型参数、p值、调整后的R方，样本量，以及模型结果summary
ant_print_all(model_result, model_attr=['params','pvalues', 'rsquared_adj', 'nobs'], model_method='summary')
```

### Logit
Logit 文档 [https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.Logit.html](https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.Logit.html)

Logit 例子[https://www.statsmodels.org/stable/discretemod.html](https://www.statsmodels.org/stable/discretemod.html)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| statsmodels | Logit | params | 回归结果参数（属性） |
|  |  | pvalues | p-值（属性） |
|  |  | tvalues | t-值（属性） |
|  |  | prsquared | R方（属性） |
|  |  | bse | 标准误差（属性） |
|  |  | nobs | 样本量（属性） |
|  |  | summary | 回归结果汇总summary（方法） |
|  |  | summary2 | 回归结果汇总summary2（方法） |


**举例**

```python
import pandas as pd 
import numpy as np 
import statsmodels.api as sm 


# define your own y in here
# define your own x in here 
model_result = sm.Logit(y, X).fit()

# 下面的代码将输出模型参数、p值以及模型结果summary
ant_print_all(model_result, model_attr=['params', 'pvalues'], model_method="summary")
```

### MNLogit
MNLogit 文档 [https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.MNLogit.html#statsmodels.discrete.discrete_model.MNLogit](https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.MNLogit.html#statsmodels.discrete.discrete_model.MNLogit)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| statsmodels | MNLogit | params | 回归结果参数（属性） |
|  |  | pvalues | p-值（属性） |
|  |  | tvalues | t-值（属性） |
|  |  | prsquared | R方（属性） |
|  |  | bse | 标准误差（属性） |
|  |  | nobs | 样本量（属性） |
|  |  | summary | 回归结果汇总（方法） |
|  |  | summary2 | 回归结果汇总（方法） |


**举例**

```python
import pandas as pd 
import numpy as np 
import statsmodels.api as sm 


# define your own y in here
# define your own x in here 
model_result = sm.MNLogit(y, X).fit()

# 下面的代码将输出模型参数、p值、样本量，以及模型结果summary
ant_print_all(model_result, model_attr=['params', 'pvalues', 'nobs'], model_method='summary') 
```

### Probit
Probit 文档

[https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.Probit](https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.Probit) 

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| statsmodels | Probit | params | 回归结果参数（属性） |
|  |  | pvalues | p-值（属性） |
|  |  | tvalues | t-值（属性） |
|  |  | prsquared | R方（属性） |
|  |  | bse | 标准误差（属性） |
|  |  | nobs | 样本量（属性） |
|  |  | summary | 回归结果汇总（方法） |
|  |  | summary2 | 回归结果汇总（方法） |


**举例**

```python
import pandas as pd 
import numpy as np 
import statsmodels.api as sm 


# define your own y in here
# define your own x in here 

model_result = sm.Probit(y, X).fit()

# 下面的代码将输出模型参数、p值、样本量，以及模型结果summary
ant_print_all(model_result, model_attr=['params','pvalues', 'nobs'], model_method='summary')
```

### RLM
RLM 文档

[https://www.statsmodels.org/dev/generated/statsmodels.robust.robust_linear_model.RLM.html](https://www.statsmodels.org/dev/generated/statsmodels.robust.robust_linear_model.RLM.html)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| statsmodels | RLM | params | 回归结果参数（属性） |
|  |  | pvalues | p-值（属性） |
|  |  | tvalues | t-值（属性） |
|  |  | bse | 标准误差（属性） |
|  |  | nobs | 样本量（属性） |
|  |  | summary | 回归结果汇总（方法） |


**举例**

```python
import statsmodels.api as sm
from marvel.AntPrint import *
# define your own y, x here
res = sm.RLM(y, x).fit()
ant_print_all(res, model_method="summary")
```

### Poisson Model
相关文档

[https://www.statsmodels.org/dev/generated/statsmodels.discrete.discrete_model.Poisson.html](https://www.statsmodels.org/dev/generated/statsmodels.discrete.discrete_model.Poisson.html)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| statsmodels | Poisson | params | 回归结果参数（属性） |
|  |  | pvalues | p-值（属性） |
|  |  | tvalues | t-值（属性） |
|  |  | bse | 标准误差（属性） |
|  |  | nobs | 样本量（属性） |
|  |  | summary | 回归结果汇总（方法） |


**举例**

```python
from statsmodels.discrete.discrete_model import Poisson
# define your own y, x here
res = Poisson(y, x).fit()
ant_print_all(res, model_method="summary")
```

### ARIMA
ARIMA 文档

[https://www.statsmodels.org/devel/generated/statsmodels.tsa.arima.model.ARIMA.html](https://www.statsmodels.org/devel/generated/statsmodels.tsa.arima.model.ARIMA.html)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| statsmodels | ARIMA | params | 回归结果参数（属性） |
|  |  | pvalues | p-值（属性） |
|  |  | tvalues | t-值（属性） |
|  |  | bse | 标准误差（属性） |
|  |  | nobs | 样本量（属性） |
|  |  | summary | 回归结果汇总（方法） |


**举例**

```python
from statsmodels.tsa.stattools import adfuller as ADF
ant_print_all(ADF, data["lwage"])
from statsmodels.tsa.arima.model import ARIMA
result = ARIMA(data["lwage"]).fit()
ant_print_all(result, model_method="summary")
```

### 似不相关回归
| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| linearmodels | SUR | params | 回归结果参数（属性） |
|  |  | pvalues | p-值（属性） |
|  |  | rsquared | R方（属性） |
|  |  | summary | 回归结果汇总（属性） |
|  |  | system_rsquared | 标准误差（属性） |
|  |  | tstats | t-值（属性） |


**举例**

```python
import linearmodels as lm

# define formula and data
model = lm.system.model.SUR.from_formula(formula, data)
model_result = model.fit()

ant_print_all(model_result, model_attr=['params', 'pvalues', 'rsquared', 'summary', 'system_rsquared', 'tstats'])
```

### 因果推断分析(causalinference)
| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| causalinference | CausalModel | summary_stats | 结果汇总（属性） |
| | | estimates | 处理效应估计（属性） |


**举例**

```python
from causalinference import CausalModel
from marvel.AntPrint import ant_print_all
causal = CausalModel(Y, D, X)
causal.est_via_matching()
ant_print_all(causal, model_attr=['summary_stats', 'estimates'])
```

### 因果推断分析(EconML)
EconML文档

[https://econml.azurewebsites.net/spec/estimation/dml.html](https://econml.azurewebsites.net/spec/estimation/dml.html)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| econml | DML | ate | 处理效应（方法） |
| | LinearDML | score | 分数（方法） |
| | NonParamDML | ate_inference | 处理效应推断（方法） |
| | CausalForestDML | | |
| | SparseLinearDML | | |


| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| econml | XLearner | ate | 处理效应（方法） |
| | TLearner | ate_inference | 处理效应推断（方法） |


**举例**

```python
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from econml.dml import DML
from causalinference.utils import random_data
Y, D, X = random_data()
model_y = GradientBoostingRegressor(max_depth=6, n_estimators=20).fit(X, Y)
model_t = GradientBoostingClassifier(max_depth=6, n_estimators=20).fit(X, D)
model_final = GradientBoostingRegressor(max_depth=6, n_estimators=20)
est_dml = DML(model_y=model_y, model_t=model_t, model_final=model_final)
est_dml.fit(Y=Y, T=D, X=X)
ant_print_all(est_dml, X, model_method="ate")
# ant_print_all(est_dml, X, model_method="ate_inference")
```

注意：

并不是所有方法都可以得到ate_inference。如果运行ate_inference报错，可以尝试fit时添加参数inference="bootstrap"。

### 广义矩估计
| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| statsmodels | GMM | bse | 标准误差（属性） |
|  |  | pvalues | p-值（属性） |
|  |  | jval | <font style="color:rgba(0, 0, 0, 0.87);">nobs_moms attached by momcond_mean（属性）</font> |
|  |  | summary | 结果汇总（方法） |
|  |  | q | 目标函数在参数处的估计（属性） |
|  |  | tvalues | t-值（属性） |


**举例**

```python
from statsmodels.sandbox.regression.gmm import GMM

# define subclass
class GMM_subclass(GMM):
    def momcond(self, params):
        # 逻辑代码
        return np.column_stack((error1, error2,...))

# define data
model = GMM_subclass(data['y'], data[['x1', 'x2', 'x3']], data[['z1', 'z2']])
model_result = model.fit([0, 1])
ant_print_all(model_result, model_attr=['bse'], model_method='summary')
```

### 生存分析Cox比例风险模型
| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| lifelines | CoxPHFitter | print_summary | 结果汇总（方法） |


**举例**

```python
from lifelines.datasets import load_rossi
from lifelines import CoxPHFitter
from marvel.AntPrint import ant_print_all

rossi = load_rossi()
cph = CoxPHFitter()
cph.fit(rossi, 'week', 'arrest')
ant_print_all(cph, model_method='print_summary')
```

### 生存分析CoxTimeVaryingFitter模型
| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| lifelines | CoxTimeVaryingFitter | print_summary | 结果汇总（方法） |


**举例**

```python
from lifelines import CoxTimeVaryingFitter

data["id"] = data.index
ctv = CoxTimeVaryingFitter(penalizer=0.1)
ctv.fit(data, id_col="id", event_col="black", 
        start_col="married", stop_col="year")
ant_print_all(ctv, model_method="print_summary")
```

### 有序模型OrderedModel
| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| statsmodels (v0.13.0.dev0) | OrderedModel | params | 回归结果参数（属性） |
|  | | pvalues | p-值（属性） |
| | | prsquared | R方（属性） |
| | | bse | 标准差（属性） |
| | | tvalues | t-值（属性） |
| | | nobs | 样本量（属性） |
| | | summary | 结果汇总（方法） |


**举例**

```python
from marvel.AntPrint.model import OrderedModel
from marvel.AntPrint import ant_print_all

# 数据生成
df=pd.DataFrame(np.random.randint(0,3,400),columns=["y"])
df["x_1"]=np.random.randint(0,2,400)
df["x_2"]=np.random.randint(0,2,400)
df["x_3"]=np.random.random_sample(400)

# 模型拟合，以及结果输出
model = OrderedModel(df['y'], df[['x_1', 'x_2', 'x_3']],distr='logit')
result = model.fit(method="nm")
ant_print_all(result, model_attr="params", model_method="summary")
```

特殊注意事项：

+ 由于兼容性问题，当前平台使用的是本地平行开发版本，而不是statsmodels原生方法。但是产出的模型结果会与原生代码保持一致。

**关于OrderedModel的其他使用细节，请参考官方文档：**

[https://www.statsmodels.org/devel/examples/notebooks/generated/ordinal_regression.html](https://www.statsmodels.org/devel/examples/notebooks/generated/ordinal_regression.html)

### HeckmanModel
[https://github.com/statsmodels/statsmodels/blob/92ea62232fd63c7b60c60bee4517ab3711d906e3/statsmodels/regression/heckman.py](https://github.com/statsmodels/statsmodels/blob/92ea62232fd63c7b60c60bee4517ab3711d906e3/statsmodels/regression/heckman.py)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| marvel | Heckman | params | 回归结果参数（属性） |
|  | | pvalues | p-值（属性） |
| | | prsquared | R方（属性） |
| | | bse | 标准差（属性） |
| | | tvalues | t-值（属性） |
| | | nobs | 样本量（属性） |
| | | summary | 结果汇总（方法） |


**举例**

```python
from marvel.AntPrint.model import Heckman
model = Heckman(data["lwage"], data["black"], data["married"])
res = model.fit()
ant_print_all(res, model_method="summary")
```

特殊注意事项：

+ 我们使用的是statsmodels内的一个分支下实现的Heckman模型，不对其计算稳定性和正确性做保证。



### DecisionTree/RandomForest
相关文档

[https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html?highlight=decision%20tree#sklearn.tree.DecisionTreeClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html?highlight=decision%20tree#sklearn.tree.DecisionTreeClassifier)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| scikit-learn | DecisionTreeClassifier | feature_importances_ | 特征重要程度（属性） |
|  | DecisionTreeRegressor |  |  |
|  | RandomForestClassifier |  |  |
|  | RandomForestRegressor |  |  |


**举例**

```python
from sklearn.tree import DecisionTreeClassifier

# define your own y in here
# define your own x in here 
decision_tree = DecisionTreeClassifier(random_state=0, max_depth=2)
decision_tree = decision_tree.fit(x, y)

# 下面的代码将输出模型特征重要性
ant_print_all(decision_tree, model_attr=['feature_importances_'])
```

### 函数最优化结果
相关文档

[https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| scipy | <font style="color:rgb(74, 74, 74);">OptimizeResult</font> | fun | 最优化函数值 |
|  |  | message | 最优化信息 |
|  |  | status | 最优化状态 |
|  |  | success | 最优化是否成功 |
| | | x | 最优化结果 |


```python
import scipy
def f(x):
    return x**2    
res = scipy.optimize.minimize(f, 3)
ant_print_all(res, model_attr=["x", "success"])
```

### Tobit
相关文档

[https://github.com/Py4Etrics/py4etrics](https://github.com/Py4Etrics/py4etrics)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| py4etrics | <font style="color:rgb(74, 74, 74);">Tobit</font> | params | 回归结果参数（属性） |
|  |  | pvalues | p-值（属性） |
|  |  | prsquared | R方（属性） |
|  |  | bse | 标准差（属性） |
| | | tvalues | t-值（属性） |
| | | nobs | 样本量（属性） |
| | | summary | 结果汇总（方法） |


```python
from py4etrics.tobit import Tobit
res = Tobit(data["lwage"], data["black"], data["married"]).fit()
ant_print_all(res, model_method="summary")
```

备注：py4ertics是一个开源的第三方包，且使用人数目前相对较少。



### CEM
相关文档

[https://github.com/lewisbails/cem](https://github.com/lewisbails/cem)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| cem | <font style="color:rgb(74, 74, 74);">CEM</font> | outcome | 结果（属性） |
|  |  | H | H值（属性） |
|  |  | imbalance_scheme | 非平衡字段（属性） |
|  |  | imbalance | 非平衡（方法） |


```python
from cem import CEM
c = CEM(data, "black", "married")
ant_print_all(c, model_method="imbalance")
ant_print_all(c, model_attr=["outcome", "H"])
```

备注：cem是一个开源的第三方包，且使用人数目前相对较少。

### PCA
PCA 文档

[https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| sklearn | PCA | explained_variance_ | 可解释方差 |
| | | explained_variance_ratio_ | 解释方差比 |




### FixedEffectModel
FixedEffectModel文档

[https://pypi.org/project/FixedEffectModel/](https://pypi.org/project/FixedEffectModel/)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| FixedEffect | iv2sls | params | 回归结果参数（属性） |
|  | ivgmm | <font style="color:#404040;">pvalues</font> | p-值（属性） |
|  | did | bse | 标准误差（属性） |
|  | fixedeffect | <font style="color:#404040;">tvalues</font> | t-值（属性） |
|  |  | <font style="color:#404040;">nobs</font> | 样本量（属性） |
|  |  | conf_int | 输出置信区间 |
|  |  | <font style="color:#404040;">summary</font> | 回归结果汇总summary |


```python
from fem.iv import iv2sls, ivgmm
from fem.iv.ivtest import ivtest
from fem.fe import fixedeffect, did
from fem.utils.panel_dgp import gen_data
import numpy as np

N = 100
T = 10
beta = [-3, 1, 2, 3, 4]
ate = 1
exp_date = 5
exog_x = ['x_1']
endog_x = ['x_2']
iv = ['x_3', 'x_4']
y = ['y']

df = gen_data(N, T, beta, ate, exp_date)

model = ivgmm(data_df=df, dependent=y, exog_x=exog_x, endog_x=endog_x,
              category=['id', 'time'], iv=iv)
result = model.fit()
ant_print_all(result, model_attr=["params", "bse", "tvalues", "pvalues", "nobs"],
              model_method="summary")
ant_print_all(ivtest, result)
```



### ConditionalLogit 条件逻辑回归
ConditionalLogit 文档

[https://www.statsmodels.org/dev/generated/statsmodels.discrete.conditional_models.ConditionalLogit.html](https://www.statsmodels.org/dev/generated/statsmodels.discrete.conditional_models.ConditionalLogit.html)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| statsmodels | ConditionalLogit | params | 回归结果参数（属性） |
|  |  | pvalues | p-值（属性） |
|  |  | tvalues | t-值（属性） |
|  |  | bse | 标准误差（属性） |
|  |  | t_test | t检验（方法） |
|  |  | f_test | F测试（方法） |
|  |  | summary | 回归结果汇总summary（方法） |
| | | nobs | 样本量（属性） |


**举例**

```python
import numpy as np
from statsmodels.discrete.conditional_models import ConditionalLogit
from marvel.AntPrint import ant_print_all

g = np.kron(np.arange(10), np.ones(50)).astype(int)
x = np.random.normal(size=500)
pr = 1 / (1 + np.exp(-x*g))
y = (np.random.uniform(size=500) < pr).astype(int)

m = ConditionalLogit(endog=y, exog=x, groups=g).fit()
ant_print_all(m, model_method="summary")
```

### Graph 图模型
| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| igraph | Graph | summary | 回归结果汇总summary（方法） |
| | | degree | 顶点度数计算（方法） |
| | | vs | 顶点序列（属性） |
| | | es | 边序列（属性） |




**举例**

```python
import igraph as ig
import matplotlib.pyplot as plt
import pandas as pd
import random
from marvel.AntPrint import ant_print_all

num_nodes = 1000  
num_edges = 10000 

edges = [(random.randint(0, num_nodes - 1), random.randint(0, num_nodes - 1)) for _ in range(num_edges)]

df = pd.DataFrame(edges, columns=['source', 'target'])

g = ig.Graph(n=num_nodes, edges=edges, directed=True)

g.vs['name'] = [f'node-{i}' for i in range(num_nodes)]
g.vs[0]['name'] = 'node-x'
g.vs[:10]['name'] = 'node-y'

g.es['weight'] = [random.randint(1, 100) for _ in range(num_edges)]
g.es[0]['weight'] = 50
g.es[20:30]['weight'] = 100

vs = g.vs
es = g.es
ant_print_all(vs, model_method="attributes")
ant_print_all(es, model_method="attributes")

tested_nodes = random.sample(range(num_nodes), 50)
page_rank_centrality = g.pagerank(tested_nodes)
betweenness_centrality = g.betweenness(tested_nodes)
eigenvector_centrality = g.evcent(tested_nodes)

ant_print_all(g, model_method="summary")
ant_print_all(g, tested_nodes, model_method="degree", mode="in")
ant_print_all(g, tested_nodes, model_method="degree", mode="out")

vs_select = g.vs.select(_degree=g.maxdegree())[0]
ant_print_all(vs_select, model_attr=["index"])

vs_select_dgt = g.vs.select(_degree_gt=1)[0]
ant_print_all(vs_select_dgt, model_attr=["index"])
ant_print_all(es, model_method="select", _source=0)
```



### WganModel
[https://github.com/gsbDBI/ds-wgan/blob/master/wgan/wgan.py](https://github.com/gsbDBI/ds-wgan/blob/master/wgan/wgan.py)

| **所属的包** | **模型** | **模型结果的属性/方法** | **变量说明** |
| --- | --- | --- | --- |
| marvel | WganModel | compare_dfs | 模型结果对比（方法） |


```plain
from marvel.AntPrint import ant_read_data, ant_print_all 
from marvel.AntPrint.model.WganModel import compare_dfs

df = ant_read_data("wgan_data")
df_balanced = df.sample(2*len(df), weights=(1-df.t.mean())*df.t+df.t.mean()*(1-df.t), replace=True)

# X | t
continuous_vars_0 = ["age", "education", "re74", "re75"]
continuous_lower_bounds_0 = {"re74": 0, "re75": 0}
categorical_vars_0 = ["black", "hispanic", "married", "nodegree"]
context_vars_0 = ["t"]

# Y | X, t
continuous_vars_1 = ["re78"]
continuous_lower_bounds_1 = {"re78": 0}
categorical_vars_1 = []
context_vars_1 = ["t", "age", "education", "re74", "re75", "black", "hispanic", "married", "nodegree"]

# Initialize objects
from marvel.AntPrint.model import WganModel as wgan
data_wrappers = [wgan.DataWrapper(df_balanced, continuous_vars_0, categorical_vars_0,
                                  context_vars_0, continuous_lower_bounds_0),
                 wgan.DataWrapper(df_balanced, continuous_vars_1, categorical_vars_1,
                                  context_vars_1, continuous_lower_bounds_1)]
specs = [wgan.Specifications(dw, batch_size=4096, max_epochs=1000, critic_lr=1e-3, generator_lr=1e-3,
                             print_every=100, device = "cpu") for dw in data_wrappers]
generators = [wgan.Generator(spec) for spec in specs]
critics = [wgan.Critic(spec) for spec in specs]

# train X | t
x, context = data_wrappers[0].preprocess(df_balanced)
wgan.train(generators[0], critics[0], x, context, specs[0])

# train Y | X, t
x, context = data_wrappers[1].preprocess(df_balanced)
wgan.train(generators[1], critics[1], x, context, specs[1])

# simulate data with conditional WGANs
df_generated = data_wrappers[0].apply_generator(generators[0], df.sample(int(1e6), replace=True))
df_generated = data_wrappers[1].apply_generator(generators[1], df_generated)

dd_test = ((df_generated.re78-df_generated.re78_cf) * (2*df_generated.t - 1))[df_generated.t==1]
ant_print_all(dd_test, model_method="describe")

ant_print_all(compare_dfs, df, df_generated,
                 scatterplot=dict(x=["re74", "age", "education"], y=["re78", "re75"], samples=400, smooth=0),
                 table_groupby=["t"],
                 histogram=dict(variables=["re78", "re74", "age", "education"], nrow=2, ncol=2),
                 figsize=3)
```



## 3.4 打印函数（假设检验）的结果
### ztest z-检验
**说明**

各参数的用法同 statsmodels.stats.weightstatas.ztest, 见如下文档

[https://www.statsmodels.org/stable/generated/statsmodels.stats.weightstats.ztest.html#statsmodels.stats.weightstats.ztest](https://www.statsmodels.org/stable/generated/statsmodels.stats.weightstats.ztest.html#statsmodels.stats.weightstats.ztest)

**举例**

```python
from statsmodels.stats.weightstats import ztest
ant_print_all(ztest, x1=df['user_age'])
```

### ttest_1samp 单样本T-检验
**说明**

各参数用法同scipy.stats.ttest_1samp， 见如下文档

[https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_1samp.html](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_1samp.html)

**举例**

```python
import scipy.stats as sci_s
ant_print_all(sci_s.ttest_1samp, df['user_age'], 0)
```

### ttest_ind 双样本T-检验
**说明**

各参数用法同scipy.stats.ttest_ind，见如下文档

[https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html)

**举例**

```python
ant_print_all(sci_s.ttest_ind, df[['user_gender']],df['user_age'])
```

### ranksums 秩和检验
**说明**

各参数用法同scipy.stats.ranksums，见如下文档

[https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ranksums.html](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html)

```python
ant_print_all(sci_s.ranksums, df['user_gender'], df['user_age'])
```

### median_test 中位数检验
**说明**

各参数用法同scipy.stats.median_test，见如下文档

[https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.median_test.html](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.median_test.html)

**举例**

```python
ant_print_all(sci_s.median_test, g1, g2, g3)
```

### wilcoxon检验
**说明**

各参数用法同scipy.stats.wilcoxon，见如下文档

[https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.median_test.html)

**举例**

```python
d = [6, 8, 14, 16, 23, 24, 28, 29, 41, -48, 49, 56, 60, -67, 75]
ant_print_all(sci_s.wilcoxon, d, mod='appeox')
```

### adfuller 平稳性检验
**说明**

各参数用法同statsmodels.tsa.stattools.adfuller，见如下文档

[https://www.statsmodels.org/devel/generated/statsmodels.tsa.stattools.adfuller.html#statsmodels.tsa.stattools.adfuller](https://www.statsmodels.org/devel/generated/statsmodels.tsa.stattools.adfuller.html#statsmodels.tsa.stattools.adfuller)

**举例**

```python
import statsmodels.tsa.stattools as stats_tool
ant_print_all(stats_tool.adfuller, df['user_age'])
```

### coint 协整检验
**说明**

各参数用法同 statsmodels.tsa.stattools.coint，见如下文档

[https://www.statsmodels.org/devel/generated/statsmodels.tsa.stattools.coint.html#statsmodels.tsa.stattools.coint](https://www.statsmodels.org/devel/generated/statsmodels.tsa.stattools.coint.html#statsmodels.tsa.stattools.coint)

**举例**

```python
ant_print_all(stats_tool.coint, df[['user_gender']],df['user_age'])
```

### grangercausalitytests 因果检验
**说明**

各参数用法同statsmodels.tsa.stattools.grangercausalitytests

[https://www.statsmodels.org/devel/generated/statsmodels.tsa.stattools.grangercausalitytests.html#statsmodels.tsa.stattools.grangercausalitytests](https://www.statsmodels.org/devel/generated/statsmodels.tsa.stattools.grangercausalitytests.html#statsmodels.tsa.stattools.grangercausalitytests)

**举例**

```python
ant_print_all(stats_tool.grangercausalitytests, df[['user_net_position_all','user_age']],1)
```

### pearsonr 相关性检验
**说明**

各参数同scipy.stats.pearsonr

[https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html)

**举例**

```python
ant_print_all(sci_s.pearsonr, df[['user_net_position_all']], df['user_age'])
```

### export_tree_structure 树模型结构输出
**说明**

各参数用法同   sklearn.tree.export_text  (出于数据安全考虑，max_depth最大支持5)

[https://scikit-learn.org/stable/modules/generated/sklearn.tree.export_text.html](https://scikit-learn.org/stable/modules/generated/sklearn.tree.export_text.html)

**举例**

```python
from sklearn.tree import DecisionTreeRegressor
dtr = DecisionTreeRegressor(random_state=0, max_depth=2)
dtr = dtr.fit(data[["year", "black"]], data["lwage"])
from sklearn.tree import export_text
ant_print_all(export_text, dtr)
```

### check_df_singularity 奇异矩阵判断
**说明**

参数是pandas DataFrame数据类型

**举例**

```python
from marvel.AntPrint.sandbox.util_func import check_df_singularity
import pandas as pd
import numpy as np
from marvel.AntPrint import ant_print_all
mt1 = np.array([[1,2,3], [2,2,1], [2,np.nan,6]])
df1 = pd.DataFrame(mt1)
if check_df_singularity(df1):
    ant_print_all(df1, model_method="value_counts")
```

### envir/print_envir 环境判断函数
**说明**

判断/打印当前环境状态（仿真环境、真实环境）

**举例**

```python
from marvel.AntPrint.sandbox.global_constant import envir, print_envir
# 判断当前环境状态
if envir() == '仿真环境':
    # 只在仿真环境运行的代码

# 打印当前环境状态
print_envir()
```

### chowtest 邹检验
**说明**

各参数用法同chow_test.chowtest，见如下文档[https://pypi.org/project/chowtest/](https://pypi.org/project/chowtest/)

**举例**

```python
from marvel.AntPrint import *
from marvel.AntPrint.function.ChowTest import chow_test
import numpy as np
import pandas as pd

data = pd.DataFrame({"x": np.random.randint(0, 100, 100), "y": np.random.randint(0, 100, 100)})
ant_print_all(chow_test, data["x"], data["y"], 1, 2, .05)
```



### permutation_test 置换检验
**说明**

各参数的用法同 scipy.stats.permutation_test，见如下文档

[https://docs.scipy.org/doc/scipy-1.8.1/reference/generated/scipy.stats.permutation_test.html](https://docs.scipy.org/doc/scipy-1.8.1/reference/generated/scipy.stats.permutation_test.html)

**举例**

```python
def statistic(x, y, axis):
    return np.mean(x, axis=axis) - np.mean(y, axis=axis)

from scipy.stats import norm
rng = np.random.default_rng()
x = norm.rvs(size=5, random_state=rng)
y = norm.rvs(size=6, loc = 3, random_state=rng)

from scipy.stats import permutation_test
ant_print_all(permutation_test, (x, y), statistic, vectorized=True, n_resamples=np.inf,
              alternative='less')
```

## 
## 3.5 注意事项
+ 打印输出的量限制50kb/代码块，500kb/文件
+ 打印数据的描述性统计等，要求输入数据行数大于等于100行



# 4. 输出：图片内容
平台绘图功能基于第三方包seaborn和matplotlib开发，语法和底层逻辑均与这两个包基本一致。

相关文档：

[https://matplotlib.org/](https://matplotlib.org/)

[https://seaborn.pydata.org/index.html](https://seaborn.pydata.org/index.html)

## 4.1 绘图接口说明
### ant_plot 通用绘图说明
**Attributes**

**<font style="color:rgba(0, 0, 0, 0.87);">axes_list : </font>**<font style="color:#40A9FF;">List</font>

<font style="color:rgba(0, 0, 0, 0.87);">A list of matplotlib axes </font>



**Methods**

| re_init() | <font style="color:rgb(33, 37, 41);">Reinitialize the figure.</font> |
| --- | --- |
| add_subplot(nrows, ncols, index) | <font style="color:rgb(33, 37, 41);">Add subplot into the figure.</font> |
| plot(df, method, kind, index=0, **kwargs) | Plot api. |
| plt_set(method, **kwargs) | <font style="color:rgb(33, 37, 41);">Plot set.</font> |
| figure_set(method, **kwargs) | <font style="color:rgb(33, 37, 41);">Figure set.</font> |
| axes_set(method, index, **kwargs) | <font style="color:rgb(33, 37, 41);">Axes set.</font> |
| <font style="color:rgb(33, 37, 41);">set_theme(context, style, palette, font, font_scale, color_codes, rc)</font> | <font style="color:rgb(33, 37, 41);">Set theme of the plot.</font> |
| show() | Show the plot. |


```python
from marvel.AntPrint import ant_plot
```

### `re_init()`初始化
重新初始化，会创建一个空的画布

**Parameters** **:**

No Parameters

**Returns :**

No Return

```python
ant_plot.re_init()
```

### add_subplot 添加绘图区域
`add_subplot(nrows=1, ncols=1, index=1)`

向画布中添加绘图区域(axes), for details, see [matplotlib.figure.Figure.add_subplot](https://matplotlib.org/stable/api/figure_api.html?highlight=add_subplot#matplotlib.figure.Figure.add_subplot), 

**Parameters** **:**

**nrows** **:** <font style="color:#40A9FF;">int, 1 by default</font>

绘图区域行数

**ncols** **:** <font style="color:#40A9FF;">int, 1 by default</font>

绘图区域列数

**index: **<font style="color:#40A9FF;">int/tuple, 1 by default</font>

取绘图区域的哪一部分

**Returns :**

int, 返回该子图在axes_list中的位置

```python
ant_plot.add_subplot()
```

### plot 绘图
`plot(df, method, kind, axindex=0, **kwargs)`

在指定的subplot上绘图

**Parameters** **:**

**df** **:** <font style="color:#40A9FF;">DataFrame</font>

DataFrame contains the data to plot.

**method :** <font style="color:#40A9FF;">string</font>

用于处理数据的函数，支持 "ant_plot_df", "ant_plot_df_groupby_discrete", "ant_plot_df_groupby_continuous"，各方法详细见下.

**kind **: <font style="color:#40A9FF;">string</font>

图片类型，支持 "box", "hist", "ecdf", "kde", "scatter", "line", "heatmap"

**axindex : **<font style="color:#40A9FF;">int, 0 by default</font>

需要绘制的子图在axes_list中的位置，如果只有一张子图，那么一定是0

****kwargs :**

Other <font style="color:rgb(51, 51, 51);">keyword arguments for method and plot</font>

**Returns :**

No Return



### DataFrame数据绘图 ant_plot_df
针对dataframe数据绘图 ant_plot_df(df, kind，**kwargs)

<font style="color:#1890FF;">输入参数：</font>

df：dataframe类型的数据

kind：str，代表图片类型，支持"box", "hist", "ecdf", "kde", "scatter", "line", "heatmap", "bar"

**kwargs：绘图相关参数，详见各图片类型参数列表

```python
from marvel.AntPrint import ant_plot
ant_plot.re_init()
ant_plot.add_subplot()
ant_plot.plot(df=data, method="ant_plot_df", kind="scatter", x="x", y="y")
ant_plot.show()
```



### 分组统计绘图 ant_plot_df_groupby_discrete
针对离散型的key进行分组统计再绘图 ant_plot_df_groupby_discrete(df, kind, group_by_columns, cal_columns, fun_list=None, **kwargs)

<font style="color:#1890FF;">输入参数：</font>

df：dataframe类型的数据

kind：str，代表图片类型，支持"box", "hist", "ecdf", "kde", "scatter", "line", "heatmap", "bar"

group_by_columns：用于分组的key列，为离散型（一般为分类变量）

cal_columns：用于计算的列

fun_list：需要计算的统计量，默认为 计数函数"count"

**kwargs：绘图相关参数，详见各图片类型参数列表

```python
import seaborn as sns
from marvel.AntPrint import ant_plot
flights = sns.load_dataset("flights")
ant_plot.re_init()
ant_plot.add_subplot()
ant_plot.plot(df=flights, method="ant_plot_df_groupby_discrete", kind="line",
              group_by_columns=["year"], cal_columns=["passengers"], fun_list=["sum"])
ant_plot.show()
```

### 分组统计绘图 ant_plot_df_groupby_continuous
针对连续型key进行分组统计绘图 ant_plot_df_groupby_continuous(df, kind, group_by_columns, cal_columns, q, cut_strategy="quantile", fun_list=None, **kwargs)

针对连续型key进行分组统计再绘图

<font style="color:#1890FF;">输入参数：</font>

df：dataframe类型的数据

kind：str，代表图片类型，支持"box", "hist", "ecdf", "kde", "scatter", "line", "heatmap", "bar"

group_by_columns：用于分组的key列，为连续型（一般为数值型变量）

cal_columns：用于计算的列

q：int型 / list，分箱数量/切分点列表

cut_strategy："quantile" / "uniform"

"quantile"：等量分组，尽量保证分组后，每个组内的样本数相等

"uniform"：等距分组，保证分组后，组间距离相等

fun_list：需要计算的统计量，默认为 计数函数"count"

**kwargs：绘图相关参数，详见各图片类型参数列表

```python
import seaborn as sns
from marvel.AntPrint import ant_plot
flights = sns.load_dataset("flights")
ant_plot.re_init()
ant_plot.add_subplot()
ant_plot.plot(df=flights, method="ant_plot_df_groupby_discrete", kind="line",
              group_by_columns=["year"], cal_columns=["passengers"], 
              q = [0.2, 0.4, 0.7, 1], fun_list="sum")
ant_plot.show()
```

### plt_set 绘图层设置
`**plt_set(method, **kwargs)**`

plt层图片设置函数, for detail, see [https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.html](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.html)

**Parameters** **:**

**method** **:** <font style="color:#40A9FF;">string</font>

plt设置相关的方法名，运行白名单支持的plt.method

****kwargs : **

Other <font style="color:rgb(51, 51, 51);">keyword arguments for method</font>

**Returns :**

No Return

| **所支持的method** | **描述** |
| --- | --- |
| axline | 添加无限长直线 |
| axvline | 添加竖线 |
| legend | 放置legend |
| suptitle | 添加suptitle |
| xlabel | 对x-axis设置label |
| xlim | 设置x的范围限制 |
| xticks | 设置x-axis的tick位置和标签 |
| ylabel | 对y-axis设置label |
| ylim | 设置y的范围限制 |
| yticks | 设置y-axis的tick位置和标签 |


```python
ant_plot.plt_set(method="axvline", x=0.5)
```

### figure_set 图像层设置
`**figure_set(method, **kwargs)**`

figure层图片设置函数, for detail, see [https://matplotlib.org/stable/api/figure_api.html](https://matplotlib.org/stable/api/figure_api.html)

**Parameters** **:**

**method** **:** <font style="color:#40A9FF;">string</font>

figure设置相关的方法名，运行白名单支持的figure.method

****kwargs : **

Other <font style="color:rgb(51, 51, 51);">keyword arguments for method</font>

**Returns :**

No Return

| **所支持的method** | **描述** |
| --- | --- |
| suptitle | 添加suptitle |
| set_size_inches | 设置图片大小 |
| set_dpi | 设置图片dpi |


```python
ant_plot.figure_set(method="set_size_inches", w=6, h=4)
```

### axes_set 坐标设置
`**axes_set(method, axindex=0, **kwargs)**`

axes层图片设置函数, for detail, see [https://matplotlib.org/stable/api/axes_api.html](https://matplotlib.org/stable/api/axes_api.html)

**Parameters** **:**

**method** **:** <font style="color:#40A9FF;">string</font>

axes设置相关的方法名，运行白名单支持的axes.method

****kwargs : **

Other <font style="color:rgb(51, 51, 51);">keyword arguments for method</font>

**Returns :**

No Return

| **所支持的method** | **描述** |
| --- | --- |
| vlines | 添加竖线 |
| hlines | 添加横线 |
| set_xlim | 设置x的范围限制 |
| set_ylim | 设置y的范围限制 |
| set_xlabel | 对x-axis设置label |
| set_ylabel | 对y-axis设置label |
| set_title | 设置title |
| legend | 设置legend |
| set_xticks | 设置x-axis的tick位置和标签 |
| set_xticklabels | 设置x-axis的tick标签 |
| set_yticks | 设置y-axis的tick位置和标签 |
| set_yticklabels | 设置y-axis的tick标签 |


```python
ant_plot.axes_set(method="vlines", x=0.5, ymin=-2, ymax=2)
```

### set_theme主题设置
`**set_theme(context='notebook', style='white', palette='deep', font='SimHei', font_scale=1, color_codes=True, rc=None)**`

设置图片主题，for details，see [https://seaborn.pydata.org/generated/seaborn.set_theme.html](https://seaborn.pydata.org/generated/seaborn.set_theme.html)

**Parameters** **:**

**method** **:** <font style="color:#40A9FF;">string</font>

axes设置相关的方法名，运行白名单支持的axes.method

****kwargs : **

Other <font style="color:rgb(51, 51, 51);">keyword arguments for method</font>

**Returns :**

No Return

| **所支持的参数** | **参数描述** | **参数示例** |
| --- | --- | --- |
| context | <font style="color:#404040;">放缩参数</font> | sting or dict, e.g. "notebook" |
| style | axes类型 | string or dict, e.g. "white" |
| palette | 颜色调色板 | string or sequence, e.g. "deep" |
| font | 字体 | string, e.g. 'SimHei' |
| font_scale | <font style="color:#404040;">字体大小放缩参数</font> | float, e.g. 1.0 |
| color_codes | <font style="color:#404040;">如果True且palette参数为seaborn palette，将短颜色代码重映射到来自于这个调色板的颜色</font> | bool, e.g. True |
| rc | <font style="color:#404040;">rc参数映射的字典</font> | dict or None |


```python
ant_plot.set_theme(font_scale=0.2, rc={'font.sans-serif': ['SimHei']})
```

**<font style="color:rgb(68, 68, 68);">ant_plot使用注意</font>**

1. 每次开启绘图前需要向画布中添加绘图区域，即运行add_subplot
2. 每次图片展示后，画布会被初始化
3. 除平台提供能力外的绘图被严格禁止，ant_plot会做监控



## 4.2 图片类型说明
支持的图片类型及参数

### 散点图 (scatter)
相关文档

[https://seaborn.pydata.org/generated/seaborn.scatterplot.html?highlight=scatter#seaborn.scatterplot](https://seaborn.pydata.org/generated/seaborn.scatterplot.html?highlight=scatter#seaborn.scatterplot)

| **所支持的参数** | **参数描述** | **参数示例** |
| --- | --- | --- |
| data | 绘图相关数据 | pandas.DataFrame, numpy.ndarray, mapping, or sequence |
| x, y | x, y轴使用的数据 | vectors or keys in data |
| hue | 分组变量，将生成具有不同颜色点的变量 | vector or key in data |
| style | 分组变量，将生成具有不同标记点的变量 | vector or key in data |
| palette | 用于不同 level 的 hue 变量的颜色 | string, list, dict, or matplotlib.colors.Colormap,<br/>e.g. "deep", "dark", ...<br/> 详见使用注意 |
| hue_order | 指定hue变量各级别的出现顺序 | vector of strings |
| hue_norm | 当 hue 变量是数字的时候，应用于 hue 变量的色彩映射的数据单元中的标准化 | tuple or matplotlib.colors.Normalize,<br/>e.g. (0, 7) |
| markers | 决定如何绘制不同级别 style 的标志符号 | boolean, list, or dictionary,<br/>e.g. "+", "s" |
| style_order | 指定style 变量级别的出现顺序 | list |
| units | 分组特定的样本单元 | vector or key in data |
| estimator | 聚类同一个 x 上多个观察值 y | pandas方法名称/callable/None |
| ci | 与estimator聚合时绘制的置信区间的大小 | int/"sd"/None, e.g. 95 |
| n_boot | 自举法的数量，用于计算区间的置信度 | int, e.g. 1000 |
| alpha | 设置点的不透明度 | float, 0-1之间, e.g. 0.8  |
| legend | 绘制图例的方式 | "auto", "brief", "full", or False |


输出示例：

<img src="https://cdn.nlark.com/yuque/0/2021/png/375425/1630300726245-e722b50e-eb4e-4769-ad27-0e7973073e2b.png" width="296" title="" crop="0,0,1,1" id="wXwiZ" class="ne-image">

### 折线图 (line)
相关文档

[https://seaborn.pydata.org/generated/seaborn.lineplot.html?highlight=lineplot#seaborn.lineplot](https://seaborn.pydata.org/generated/seaborn.lineplot.html?highlight=lineplot#seaborn.lineplot)

| **所支持的参数** | **参数描述** | **参数示例** |
| --- | --- | --- |
| data | 绘图相关数据 | pandas.DataFrame, numpy.ndarray, mapping, or sequence |
| x, y | x, y轴使用的数据 | vectors or keys in data |
| hue | 分组变量，将生成具有不同颜色的线条的变量 | vector or key in data |
| size | 分组变量，将生成具有不同粗细的线条的变量 | vector or key in data |
| style | 分组变量，将生成具有不同样式和/或标记的线条的变量 | vector or key in data |
| palette | 用于不同 level 的 hue 变量的颜色 | string, list, dict, or matplotlib.colors.Colormap,<br/>e.g. "deep", "dark", ...<br/> 详见使用注意 |
| hue_order | 指定hue变量各级别的出现顺序 | vector of strings |
| hue_norm | 当 hue 变量是数字的时候，应用于 hue 变量的色彩映射的数据单元中的标准化 | tuple or matplotlib.colors.Normalize,<br/>e.g. (0, 7) |
| sizes | 确定在使用size时如何选择大小的对象 | list, dict, or tuple |
| size_order | 确定size变量各级别的出现顺序 | list |
| size_norm | 当size变量是数字时，用于缩放绘图对象的数据单元中的归一化 | tuple or Normalize object<br/> |
| dashes | 决定如何绘制不同级别 style 的线条对象 | boolean, list, or dictionary |
| markers | 决定如何绘制不同级别 style 的标志符号 | boolean, list, or dictionary,<br/>e.g. "+", "s" |
| style_order | 指定style 变量级别的出现顺序 | list |
| units | 分组特定的样本单元 | vector or key in data |
| estimator | 聚类同一个 x 上多个观察值 y | pandas方法名称/callable/None |
| ci | 与estimator聚合时绘制的置信区间的大小 | int/“sd”/None, e.g. 95 |
| n_boot | 自举法的数量，用于计算区间的置信度 | int, e.g. 1000 |
| seed |  seed, 用于复现bootstrap结果 | int |
| sort | 如果为真，则数据将按 x 与 y 变量排序，否则行将按照它们在数据集中出现的顺序连接点 | boolean, e.g. True |
| err_style | 是否用半透明误差带或离散误差棒绘制置信区间 | “band” or “bars” |
| err_kws | 用于控制误差线美观的附加参数 | dict of keyword arguments |
| legend | 绘制图例的方式 | “auto”, “brief”, “full”, or False |


输出示例：

<img src="https://cdn.nlark.com/yuque/0/2021/png/375425/1630300763227-21cacb47-3299-4305-b4cf-fc127b7fc17a.png" width="296" title="" crop="0,0,1,1" id="yrDrs" class="ne-image">

### 直方图 (hist) 
相关文档

[https://seaborn.pydata.org/generated/seaborn.histplot.html?highlight=histplot#seaborn.histplot](https://seaborn.pydata.org/generated/seaborn.histplot.html?highlight=histplot#seaborn.histplot)

| **所支持的参数** | **参数描述** | **参数示例** |
| --- | --- | --- |
| data | 绘图相关数据 | pandas.DataFrame, numpy.ndarray, mapping, or sequence |
| x, y | x, y轴使用的数据 | vectors or keys in data |
| hue | 分组变量，将生成具有不同颜色的柱子 | vector or key in data |
| weights | 对相应数据点做加权 | vector or key in data |
| stat | 每个桶的加总统计量 | str, e.g. "count", "frequency" |
| discrete | 如果为真，每个桶的宽度为1 | bool, e.g. True |
| cumulative | 如果为真，绘制累计计数 | bool, e.g. True |
| common_bins | 如果为真，当semantic变量产生多个图时使用相同的桶 | bool, e.g. True |
| common_norm | 如果为真，使用标准化统计量 | bool, e.g. True |
| multiple | 当分组映射产生子集时处理多元素 | {“layer”, “dodge”, “stack”, “fill”} |
| element | 直方统计量呈现方式 | {“bars”, “step”, “poly”} |
| fill | 如果为真，填充柱状图中空间 | bool, e.g. True<br/> |
| kde | 如果为真，绘制核密度估计结果 | bool, e.g. True |
| kde_kws | kde计算相关参数 | dict |
| line_kws | kde呈现方式相关参数 | dict |
| pmax | [0,1], 对colormap设定饱和点 | number or None, e.g. 0.9 |
| cbar | 如果为真，添加颜色条 | bool, e.g. True |
| cbar_ax | 颜色条对应的坐标轴 | matplotlib.axes.Axes |
| cabr_kws | 传入颜色条的其他参数 | boolean, e.g. True |
| palette | 用于不同 level 的 hue 变量的颜色 | string, list, dict, or matplotlib.colors.Colormap,<br/>e.g. "deep", "dark", ...<br/> 详见使用注意 |
| hue_order | 指定hue变量各级别的出现顺序 | vector of strings |
| hue_norm | 当 hue 变量是数字的时候，应用于 hue 变量的色彩映射的数据单元中的标准化 | tuple or matplotlib.colors.Normalize |
| color | 当hue映射未被使用时，单色彩设定 | matplotlibcolor |
| log_scale | 设置坐标尺度为对数，数字格式为底 | bool or number, or pair of bools or numbers e.g. False |
| legend | 如果不为真，压缩分组变量的legend | bool, e.g. False |


输出示例：

<img src="https://cdn.nlark.com/yuque/0/2021/png/375425/1630300784934-e0b650c8-9646-4e56-9e81-f1a6772fe41a.png" width="296" title="" crop="0,0,1,1" id="pYaxu" class="ne-image">

### <font style="color:rgb(51, 51, 51);">箱形图</font> (box)
相关文档

[https://seaborn.pydata.org/generated/seaborn.boxplot.html?highlight=boxplot#seaborn.boxplot](https://seaborn.pydata.org/generated/seaborn.boxplot.html?highlight=boxplot#seaborn.boxplot)

| **所支持的参数** | **参数描述** | **参数示例** |
| --- | --- | --- |
| data | 绘图相关数据 | pandas.DataFrame, numpy.ndarray, mapping, or sequence |
| x, y, hue | 用于绘制长格式数据的输入 | names of variables in data or vector data, optional |
| order, hue_order | 控制分组变量（对应的条形图）的绘制顺序 | lists of strings, optional |
| orient | 控制绘图的方向（垂直或水平） | "v" | "h" |
| color | 所有元素的颜色，或渐变调色板的种子颜色 | matplotlib color |
| palette | 用于hue变量的不同级别的颜色 | string, list, dict, or matplotlib.colors.Colormap,<br/>e.g. "deep", "dark", ...<br/> 详见使用注意 |
| saturation | 控制用于绘制颜色的原始饱和度的比例 | float |
| width | 不使用色调嵌套时完整元素的宽度，或主要分组变量一个级别的所有元素的宽度 | float |
| dodge | 使用色调嵌套时，元素是否应沿分组轴移动 | bool |
| linewidth | 构图元素的灰线宽度 | float |


输出示例：

<img src="https://cdn.nlark.com/yuque/0/2021/png/375425/1630300814117-4dd18eea-7285-464c-876d-40e1252e3e0f.png" width="296" title="" crop="0,0,1,1" id="wnzNG" class="ne-image">

### <font style="color:rgb(51, 51, 51);"></font>线性回归图 (reg) 
相关文档

[https://seaborn.pydata.org/generated/seaborn.regplot.html?highlight=regplot#seaborn.regplot](https://seaborn.pydata.org/generated/seaborn.regplot.html?highlight=regplot#seaborn.regplot)

| **所支持的参数** | **参数描述** | **参数示例** |
| --- | --- | --- |
| data | 绘图相关数据 | pandas.DataFrame |
| x, y | x，y轴使用的数据 | names of variables in data |
| x_estimator | 映射向量 -> 标量的可调用函数 | callable that maps vector -> scalar, optional |
| x_bins | 分箱数 | int or vector, optional |
| x_ci | 绘制“x”离散值的集中趋势时使用的置信区间的大小 | "ci", "sd", int in [0, 100] or None, optional |
| scatter | 是否绘制带有观测值的散点图 | bool, e.g. True |
| fit_reg | 是否绘制拟合线性回归图 | bool, e.g. True |
| ci | 回归估计的置信区间大小 | int in [0, 100] or None, optional |
| n_boot | 用于估计ci的自助法 (bootstrap)重采样数 | int, optional |
| units | 如果 x 和 y 观测值嵌套在 data 中，可在此处指定 | variable name in data, optional |
| seed | 随机数发生器 | int, numpy.random.Generator, or numpy.random.RandomState, optional |
| order | 如果 order 大于1，使用 numpy.polyfit 估计多项式回归。 | int, optional |
| logistic | 如果 True，假设 y 是一个二进制变量，使用 statsmodels 估计logistic回归模型 | bool, optional |
| lowess | 如果 True，使用 statsmodels 估计非参数lowess模型（局部加权线性回归） | bool, optional |
| robust | 如果 True，使用 statsmodels 稳健回归 | bool, optional |
| logx | 如果 True，以 y~log(x) 的形式拟合线性回归，但在输入空间绘制散点图和回归模型 | bool, optional |
| label | 图例标签 | string |
| color | 图片元素颜色设置 | matplotlib color |
| marker | 散点图图示符标记 | matplotlib marker code |
| ax | 轴对象 | matplotlib Axes, optional |


输出示例：

<img src="https://cdn.nlark.com/yuque/0/2023/png/375425/1688459301031-5372122f-8d17-4ed5-ace7-709e3368db05.png" width="548.8" title="" crop="0,0,1,1" id="uc109eb09" class="ne-image">

### 经验累计分布函数图 (ecdf) 
相关文档

[https://seaborn.pydata.org/generated/seaborn.ecdfplot.html?highlight=ecdf#seaborn.ecdfplot](https://seaborn.pydata.org/generated/seaborn.ecdfplot.html?highlight=ecdf#seaborn.ecdfplot)

| **所支持的参数** | **参数描述** | **参数示例** |
| --- | --- | --- |
| data | 绘图相关数据 | pandas.DataFrame, numpy.ndarray, mapping, or sequence |
| x, y | x, y轴使用的数据 | vectors or keys in data |
| hue | 分组变量，将生成具有不同颜色图片元素的变量 | vector or key in data |
| weights | 对相应数据点做加权 | vector or key in data |
| stat | 计算的分布统计量 | str, e.g. "count", "proportion" |
| complementary | 如果为真，使用补充cdf (1-cdf) | bool, e.g. True |
| palette | 用于hue变量的不同级别的颜色 | string, list, dict, or matplotlib.colors.Colormap,<br/>e.g. "deep", "dark", ...<br/> 详见使用注意 |
| hue_order | 指定hue变量各级别的出现顺序 | vector of strings |
| hue_norm | 当 hue 变量是数字的时候，应用于 hue 变量的色彩映射的数据单元中的标准化 | tuple or matplotlib.colors.Normalize |
| log_scale | 设置坐标尺度为对数，数字格式为底 | bool or number, or pair of bools or numbers e.g. False |
| legend | 如果不为真，压缩分组变量的legend | bool, e.g. False |


输出示例：

<img src="https://cdn.nlark.com/yuque/0/2021/png/375425/1630300853178-9cb9f5c8-53ec-4377-9666-e112263f5747.png" width="296" title="" crop="0,0,1,1" id="y0XJN" class="ne-image">

### <font style="color:rgb(51, 51, 51);">经验密度分布函数图/核密度估计图 (kde)  </font>
<font style="color:rgb(51, 51, 51);">相关文档</font>

[https://seaborn.pydata.org/generated/seaborn.kdeplot.html?highlight=kdeplot#seaborn.kdeplot](https://seaborn.pydata.org/generated/seaborn.kdeplot.html?highlight=kdeplot#seaborn.kdeplot)

| **所支持的参数** | **参数描述** | **参数示例** |
| --- | --- | --- |
| data | 绘图相关数据 | pandas.DataFrame, numpy.ndarray, mapping, or sequence |
| x, y | x, y 轴使用的数据 | vectors or keys in data |
| shade  | 如果为真，则在 KDE 曲线下方的区域中增加阴影 | bool |
| vertical | 如果为真，密度图将显示在 x 轴 | bool |
| kernel | 要拟合的核的形状代码 | str |
| bw | 用于确定双变量图的每个维的核大小、标量因子或标量的参考方法的名称 | str, number, or callable |
| gridsize | 评估网格中的离散点数 | int |
| cut | 绘制估计值以从极端数据点切割 | number |
| clip | 用于拟合 KDE 图的数据点的上下限值 | pair of numbers or None, or a pair of such pairs |
| legend | 如果为真，为绘制的图像添加图例或者标记坐标轴 | bool |
| cumulative | 如果为真，则绘制 kde 估计图的累积分布 | bool |
| shade_lowest | 如果为真，则屏蔽双变量 KDE 图的最低轮廓。绘制单变量图或"shade = False"时无影响。当你想要在同一轴上绘制多个密度时，可将此参数设置为"False" | bool |
| cbar | 如果为真并绘制双变量 KDE 图，为绘制的图像添加颜色条。 | bool, e.g. True |
| cbar_ax | 用于绘制颜色条的坐标轴，若为空，就在主轴绘制颜色条。 | matplotlib.axes.Axes |
| cabr_kws | fig.colorbar()的关键字参数 | dict |
| hue | 分组变量，将生成具有不同颜色的图片元素 | vector or key in data |
| palette | 用于不同 level 的hue变量的颜色 | string, list, dict, or matplotlib.colors.Colormap |
| hue_order | 指定hue变量各级别的出现顺序 | vector of strings |
| hue_norm | 当hue变量是数字的时候，应用于hue变量的色彩映射的数据单元中的标准化 | tuple or matplotlib.colors.Normalize |
| multiple | 当分组映射产生子集时处理多元素 | {“layer”, “stack”, “fill”} |
| common_norm | 如果为真，使用观测数量scale每个条件密度，使得所有密度函数下区域总和为1 | bool, e.g. True |
| common_grid | 如果为真，对每个核密度估计使用相同的评估网格 | bool |
| levels | 等高线等级个数或者绘制等高线的数值，[0,1]之间的递增vector | int or vector |
| thresh | 绘制等高线时最低的iso比例 [0,1]之间的数字 | number in [0, 1] |
| bw_method | 决定使用的平滑带 | string, scalar, or callable, |
| bw_adjust | 变大会增加平滑度 | number |
| log_scale | 设置坐标尺度为对数，数字格式为底 | bool or number, or pair of bools or numbers e.g. False |
| color | 当hue映射未被使用时，单色彩设定 | matplotlibcolor |
| fill | 如果为真，填充密度曲线下的区域 | bool or None |


输出示例：

<img src="https://cdn.nlark.com/yuque/0/2021/png/375425/1630300673980-0c09e8c9-2c69-4a80-a979-aa915498564d.png" width="296" title="" crop="0,0,1,1" id="Ajglg" class="ne-image">

### <font style="color:rgb(51, 51, 51);">热图 (heatmap)  </font>
<font style="color:rgb(51, 51, 51);">相关文档</font>

[https://seaborn.pydata.org/generated/seaborn.heatmap.html?highlight=heatmap#seaborn.heatmap](https://seaborn.pydata.org/generated/seaborn.heatmap.html?highlight=heatmap#seaborn.heatmap)

| **所支持的参数** | **参数描述** | **参数示例** |
| --- | --- | --- |
| data | 绘图相关数据 | pandas.DataFrame, numpy.ndarray, mapping, or sequence |
| vmin, vmax | color_map使用的anchor | floats |
| cmap | 从数据值到颜色空间的映射 | matplotlib colormap name or object, or list of colors |
| center | 用于中心化colormap的数值 | float |
| robust | 如果为真，colormap的范围使用稳健分位数 | bool |
| line_width | 划分格子的线条宽度 | float |
| line_color | 划分格子的线条颜色 | color |
| cbar | 是否绘制颜色条 | bool |
| cbar_kws | 颜色条参数 | dict of key, value mappings, |
| cbar_ax | 颜色条绘制的axes | matplotlib Axes |
| square | 如果为真，每个格子都是方形 | bool |
| xticklabels, yticklabels | x, y坐标轴设置 | “auto”, bool, list-like, or int |
| mask | mask为真的格子，数据不会展示 | bool array or DataFrame |


输出示例：

<img src="https://cdn.nlark.com/yuque/0/2022/png/375425/1643423942127-6d8fe2ea-c475-4ad4-9a3e-77c02b29027b.png" width="315.710205078125" title="" crop="0,0,1,1" id="u17c1172a" class="ne-image">

### 柱状图（kde)
<font style="color:rgb(51, 51, 51);">相关文档</font>

[https://seaborn.pydata.org/generated/seaborn.kdeplot.html?highlight=kdeplot#seaborn.kdeplot](https://seaborn.pydata.org/generated/seaborn.kdeplot.html?highlight=kdeplot#seaborn.kdeplot)

| **所支持的参数** | **参数描述** | **参数示例** |
| --- | --- | --- |
| data | 绘图相关数据 | pandas.DataFrame, numpy.ndarray, mapping, or sequence |
| x, y, hue | 变量名称 | vectors or keys in data |
| order, hue_order | 绘制分类层级的数据 | list of strings |
| estimator | 每个类别下用于估计的函数 | callable |
| ci | 置信区间的大小 | _**<font style="color:rgb(68, 68, 68);">float or “sd” or None</font>**_ |
| n_boot | 计算置信区间时bootstrap次数 | int |
| units | 采样单元标志 | name of variable in data |
| seed | 随机数的种子 | int |
| orient | 图片方向 | "v" | "h" |
| color | 所有元素的颜色 | matplotlib color |
| palette | 针对hue变量的不同层级的颜色 | palette name, list, or dict |
| saturation | 饱和度 | float |
| errcolor | 代表置信区间线条的颜色 | matplotlib color |
| errwidth | 误差条的线条宽度 | float |
| capsize | 误差条上方“caps”的宽度 | float |
| dodge | 元素是否沿着分类轴移动当使用hue nesting时 | bool |


输出示例：

<img src="https://cdn.nlark.com/yuque/0/2022/png/375425/1646740498061-6f988ed8-d502-4c97-99d0-76617fd24152.png" width="311.1818084716797" title="" crop="0,0,1,1" id="u8b55f1f0" class="ne-image">

使用注意：

+ 关于palette参数，相关文档：[https://seaborn.pydata.org/tutorial/color_palettes.html?highlight=palette](https://seaborn.pydata.org/tutorial/color_palettes.html?highlight=palette) 输入的参数支持str，"deep", "muted", "pastel", "bright", "dark", "colorblind"。也可以输入list, 形如[(0, 0, 1), (0, 0.2, 0.3), ...]的列表, 列表长度对应hue参数分组数量。其中的每一个元素都是一个RGBA的三元组，元组中元素数值0-1之间。



## 4.3 高级绘图功能
### 多图排列
通过ant_plot.add_subplot接口，可以实现将多个图片排列并放置在同一个画布上输出。

关于add_subplot的详细内容，可参考文档：

[https://matplotlib.org/stable/api/figure_api.html?highlight=add_subplot#matplotlib.figure.Figure.add_subplot](https://matplotlib.org/stable/api/figure_api.html?highlight=add_subplot#matplotlib.figure.Figure.add_subplot)

**样例代码**

```python
import pandas as pd
import numpy as np
from marvel.AntPrint import ant_plot

data = pd.DataFrame(np.random.rand(200, 3), columns=["x", "y", "z"])
ant_plot.re_init()
ant_plot.figure_set(method="set_size_inches", w=10, h=4)
ant_plot.figure_set(method="set_dpi", val=100)
# 多图排列 2行1列 绘制第一张图
ant_plot.add_subplot(2, 1, 1)
ant_plot.plot(df=data, method="ant_plot_df", kind="scatter", axindex=0, x="x", y="y")
# 多图排列 2行1列 绘制第二张图
ant_plot.add_subplot(2, 1 ,2)
ant_plot.plot(df=data, method="ant_plot_df", kind="ecdf", axindex=1, x="z")
ant_plot.show()
```

**输出示例**

<img src="https://cdn.nlark.com/yuque/0/2022/png/375425/1644206408610-91568b83-b04b-4d9f-a7d2-11599011bf88.png?x-oss-process=image%2Fcrop%2Cx_18%2Cy_2%2Cw_1694%2Ch_722" width="733" title="" crop="0.0107,0.0032,0.9919,1" id="u3174d62f" class="ne-image">

### 多图叠加
ant_plot绘图接口支持在同一图片上连续绘制，以达到图片叠加的目的。

**样例代码**

```python
import pandas as pd
import numpy as np
from marvel.AntPrint import ant_plot

data = pd.DataFrame(np.random.rand(200, 2), columns=["x", "y"])
data["x2"] = 2 * data["x"]
ant_plot.re_init()
ant_plot.add_subplot(1, 1, 1)
# 散点+折线
ant_plot.plot(df=data, method="ant_plot_df", kind="scatter", axindex=0, x="x", y="y", color=(0.2, 0.6, 0.2))
# 通过twinx达到双y轴的目的
ant_plot.axes_set(method="twinx", axindex=0)
# twinx会生成一个新的axes, axindex此时需要加1
ant_plot.plot(df=data, method="ant_plot_df", kind="line", axindex=1, x="x", y="x2", linewidth=2, color=(0.4, 0.3, 0.2))
ant_plot.plt_set(method="xticks", ticks=[0.0, 0.5, 1.0], labels=[0.0, 0.5, 1.0])
ant_plot.show()
```

**输出示例**

<img src="https://cdn.nlark.com/yuque/0/2022/png/375425/1644222033051-bd18a7c3-0195-4c74-8d4f-e8a41e7fc83c.png?x-oss-process=image%2Fcrop%2Cx_10%2Cy_0%2Cw_839%2Ch_513" width="443" title="" crop="0.0121,0,0.9897,0.979" id="u5c6ffdd1" class="ne-image">

## 4.4 注意事项
### 画布限制
出于数据安全考虑，对画布的设置做了以下限制

+ figure设置尺寸，长宽必须大于等于3，小于等于12
+ figure设置dpi，数值必须大于等于50，小于等于150

### 输入数据行数限制
出于数据安全考虑，对绘图输入的数据量做了以下限制

+ 输入数据的行数必须大于等于100（heatmap除外）

### matplotlib使用限制
平台所有绘图相关的操作均需要通过接口ant_plot, 使用接口以外的能力对图片进行改动是被禁止的。如果检测到ant_plot接口外的任何图片操作，系统会自动将图片初始化。

### 其他使用注意事项
+ 绘图前建议运行以下命令，用于生成空白画布和添加绘图区域。

```python
ant_plot.re_init()
ant_plot.add_subplot(1, 1, 1)
```





# <font style="color:rgb(38, 38, 38);">5.中间表使用文档</font>
## 5.1中间表功能介绍
打开量化分析台能够看到中间表功能模块，中间表能目前只能进行新增和删除，不支持覆盖

<img src="https://cdn.nlark.com/yuque/0/2025/png/375425/1749005611249-c891c061-7954-4a28-a114-7437c97bdf0e.png" width="1381" title="" crop="0,0,1,1" id="iaWqe" class="ne-image">

## 5.2 写入中间表数据
在marvel中使用ant_write_data来保存中间表数据，ant_write_data有两个参数，如下面示例代码所示，df指的是用户需要保存的中间表数据，而mid_table_test是用户要保存的中间表名称。

```python
from marvel.AntPrint import ant_write_data, ant_read_data

df = ant_read_data('mid_table')
ant_write_data(df, 'mid_table_test')
```

## 5.3 读取中间表数据
在marvel中使用ant_read_data来读取中间表数据，读取中间表的时候需要传给ant_read_data两个参数，mid_table_test指的是用户保存的中间表表名，mid_table是标识读取的表是否为中间表。

```python
from marvel.AntPrint import ant_read_data, ant_print_all
import pandas as pd

df = ant_read_data('mid_table_test', mid_table=True)
ant_print_all(df, model_method="nunique")
```

## 5.4可信任务
### 写入中间表数据
在实验室写完数据之后，需要将模型脚本提交可信执行，等待可信执行成功之后，才能在线上可信任务中使用中间表数据。

<img src="https://cdn.nlark.com/yuque/0/2025/png/375425/1749005611242-f2eae8b9-1947-4d24-871b-707be26cea9d.png" width="680.8" title="" crop="0,0,1,1" id="GA5KH" class="ne-image">

### 读取中间表数据
在可信执行记录中，确认提交的写入中间表任务执行成功之后，才能在线上可信任务中使用中间表数据。

## 5.5中间表列名规范
中间表列名中只能使用 "_" 下划线作为分隔字符，其他如 "*"  、"-"、"/"等特殊字符都是不能使用的，会导致ODPS存储的ParseError报错。报错信息如下：

<img src="https://cdn.nlark.com/yuque/0/2025/png/375425/1749005611208-ae5ead3c-de2b-4d7e-bee1-3fc63014a5e6.png" width="1251" title="" crop="0,0,1,1" id="u52e970c7" class="ne-image">

<img src="https://cdn.nlark.com/yuque/0/2025/png/375425/1749005611407-e46c8bd4-c7ae-4855-809f-5fbca9ab99d0.png" width="1350" title="" crop="0,0,1,1" id="ue2ed8bd6" class="ne-image">
