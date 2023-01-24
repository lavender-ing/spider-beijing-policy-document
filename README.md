# spider-beijing-policy-document
使用python结合selenium获取北京市政策信息并保存为txt文件  

### 本地配置信息
python 3.10  
selenium 4.1.3  
chromedriver 109.0.5414.25  
(chromedriver-download-url: http://chromedriver.storage.googleapis.com/index.html)  

### 关键问题以及解决
* 1、选择一个条件处理完之后，发现发文机构列表会变，比如第二个图里面的“中关村科技园区管理委员会”，在第一个图里是没有的，所以这些索引是不全的。
![image](https://user-images.githubusercontent.com/101500450/214244257-d08343e3-0169-47c1-93dc-a7bec4ac415b.jpeg)  
![image](https://user-images.githubusercontent.com/101500450/214244285-750ff914-7612-490c-8640-143d35900361.jpeg)  
为了保证获取全部机构含有“京”的数据，我的方案是不在这里选，而是针对搜索到的所有15221条结果逐个判断发文机构。

* 2、每次检索后，该网站虽然显示的相关结果可能是15221条，但是每一页只有20条，一共只有25页，即每次检索最多可以查看到500条结果。
我的方案是在不改变其他检索条件的前提下，按照时间分别检索，判断每次检索的结果是否小于500，如果不是，程序exit退出；如果是就继续执行，这样可以获取全部文件。

* 3、爬虫获取的WebElement随时会超时不可用，代码可能在任意使用到网页元素的一行产生报错。
我的方案是捕获由于页面重新渲染导致的StaleException，然后递归调用处理过程，从而规避超时产生的错误。
这个过程还可以优化，比如记录产生Exception时的位置，调用时传入位置，从而不必重新循环，提高效率。

* 4、将每一页的处理过程封装成一个函数，while循环，判断是否有下一页，有就点击，没有代表已经到最后一页。

* 5、提供输入年份，自动分成月份循环处理的接口；也提供按照输入时间段进行检索（单次检索结果数量<500才可继续执行）的接口。

* 6、借助于os库函数，实现文件的高效整理。
