# 该文件针对关键字“创新”进行处理
from time import sleep
from selenium import webdriver
import selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import file_control

time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(time)

print("正在执行，请稍等……")
# 不打开浏览器界面运行
option = webdriver.ChromeOptions()
option.add_argument('headless')
wd = webdriver.Chrome(service=Service('./chromedriver'), options=option)

# 打开浏览器界面运行
# wd = webdriver.Chrome(service=Service('./chromedriver'))

wd.implicitly_wait(5)#隐式等待，设置等待元素的最长时间，每隔半秒寻找一次
# wait = WebDriverWait(wd, 20) # 显式等待容易StaleException


def search_keyword(keyword):
    wd.get('http://www.beijing.gov.cn/so/s?advancedSearchType=2&tab=zcfg') # SearchType=1对应政策文件，2对应高级搜索
    input = wd.find_element(By.CSS_SELECTOR, ".search-bigDiv .search-small-right input") # CSS选择
    input.clear() # 先清空之前的
    input.send_keys(keyword)

    search = wd.find_element(By.CSS_SELECTOR, ".search-btn-div .search-btn")
    search.click()

# 网站最多每次检索显示25页，每页20条结果，需要分多次按照时间检索来获取所有结果
# 选取检索时间
def select_time(startTime, endTime):
    sleep(1) # 加载
    searchWindow = wd.find_element(By.LINK_TEXT, "高级搜索")
    searchWindow.click()
    timeRangeList = wd.find_elements(By.CSS_SELECTOR, ".draw-main .draw-time .draw-right label")
    timeRangeList[-1].click()
    startTimeInput = wd.find_element(By.CSS_SELECTOR, ".time-search-div .start-input")
    endTimeInput = wd.find_element(By.CSS_SELECTOR, ".time-search-div .end-input")
    startTimeInput.clear() # 一定要先清空，否则下一个月份的数据无法重新写入
    endTimeInput.clear()
    startTimeInput.send_keys(startTime) # 格式：2021-01-01
    endTimeInput.send_keys(endTime)
    # 填完第二个再点击第一个input，获取悬浮窗口，需要单击确定
    startTimeInput.click()
    confirm = wd.find_element(By.CSS_SELECTOR, ".laydate-footer-btns .laydate-btns-confirm")
    confirm.click()
    # 再确定第二个时间
    endTimeInput.click()
    confirm = wd.find_element(By.CSS_SELECTOR, ".laydate-footer-btns .laydate-btns-confirm")
    confirm.click()
    # 最后搜索
    search = wd.find_element(By.CSS_SELECTOR, ".search-btn-div .search-btn")
    search.click()
    
    # 判断检索到的结果是否大于等于500
    sleep(3) # 等待检索结果数量重新加载
    resultNum = int(wd.find_element(By.CSS_SELECTOR, ".middle-con-left-top .total-div em").text)
    print(resultNum)
    if (resultNum < 500):
        print("检索数量小于500，结果显示完全")
    else:
        print("检索数量大于500，停止处理")
        wd.quit()

# 获取政策title
def find_title():
    try:
        title = wd.find_element(By.CLASS_NAME, 'header').text
    except NoSuchElementException:
        title = wd.find_element(By.CLASS_NAME, 'm-header').text
    except:
        print("寻找标题错误，使用默认标题")
        title = "null"
    finally:
        return title

# 处理这一页的数据
# 网页动态加载元素id随时变化，多次调用方法，变化时候重新调用，保证正确处理
# 可以优化：exception时候记录当前序号，重新调用时候传入序号，不必从头
# 同时，内部用到元素List时候应该重新获取，减少重新循环的可能性
def solve_this_page():
    searchResultList = wd.find_elements(By.CSS_SELECTOR, ".middle-con-left-top .search-result") # 仅用到元素长度
    try:
        for i in range(0, len(searchResultList)): # 每次循环重新获取list，并且每次要用到resultList时候要重新获取，防止动态网页变化
            # 获取所有结果
            fileType = wd.find_elements(By.CSS_SELECTOR, ".middle-con-left-top .search-result")[i].find_element(By.CSS_SELECTOR, ".search-result-header .result-header-lable").text
            # 判断是否是政策文件
            if ('政策文件' in fileType):
                print('---------------------------------')
                print("第{}个结果是政策文件".format(i+1))
                searchResultList = wd.find_elements(By.CSS_SELECTOR, ".middle-con-left-top .search-result")
                # fileName作为文件名称，后续拼接上机构和字符串
                fileName = wd.find_elements(By.CSS_SELECTOR, ".middle-con-left-top .search-result")[i].find_element(By.CSS_SELECTOR, ".result-header-title a").get_attribute("title")
                content_url = wd.find_elements(By.CSS_SELECTOR, ".middle-con-left-top .search-result")[i].find_element(By.CSS_SELECTOR, ".result-header-title a").get_attribute("href")
                # print(fileName)
                # 判断是否有表格信息，若有，提取时间和发文机构，添加到fileName中，若无，fileName就是title
                tableList = wd.find_elements(By.CSS_SELECTOR, ".middle-con-left-top .search-result")[i].find_elements(By.CLASS_NAME, "search-con")
                # table若存在，只能为1
                if (len(tableList) == 1):
                    # 将表格信息的text全部提取出来再处理
                    tableText = tableList[0].text
                    tableContentList = tableText.split('\n') # 分割
                    institution = 'null' # 如果某些政策文件没有发文机构，用null占位
                    for j in range(0, len(tableContentList)):
                        if ('机构' in tableContentList[j]): # 判断是否有机构和日期信息
                            # print(tableContentList[j+1])
                            institution = tableContentList[j+1]
                        if ('日期' in tableContentList[j]):
                            # print(tableContentList[j+1])
                            date = tableContentList[j+1]
                    if '京' not in institution:
                        print("第{}个结果发文机构中不含‘京’，跳过该文件".format(i+1))
                        continue
                    fileName = date + '_' + institution + '_' + fileName
                    
                    print(fileName)
                # 打开文件网址
                js = "window.open('"+content_url+"')"#创建js脚本
                wd.execute_script(js)#执行，打开新的标签页
                # 切换页面
                windows = wd.window_handles
                print(windows)
                wd.switch_to.window(windows[1])
                print(wd.current_url)
                # 开始处理该政策
                # 定位标题
                title = find_title()
                title = title.split('\n')[0] # 截取，去掉第二行的多余“pdf下载”等字样
                # print(title)
                try:
                    #定位正文
                    content = wd.find_element(By.ID, 'mainText').text
                    # print(content)
                    # 用fileName命名txt文件
                    output_path = '当前路径/file/{}.txt'.format(fileName)
                    # 这里用w，打开时重写文件，防止exception后多次写入相同内容
                    with open(output_path, 'w', encoding='utf-8') as f:
                        print(title, file=f)
                        print(content, file=f)
                    wd.close()
                    wd.switch_to.window(windows[0]) # 切换至主页面
                except:
                    # 记录错误文件名称
                    log_path = '当前路径/file/error_log.txt'
                    with open(log_path, 'a+', encoding='utf-8') as f:
                        print("文件处理错误：", file=f)
                        print(title, file=f)
                        print("", file=f)
                    print("文件{}处理时发生错误，已记录到error_list文档！".format(title))
                    wd.switch_to.window(windows[0]) # 切换至主页面
    except selenium.common.exceptions.StaleElementReferenceException as e:
        solve_this_page()


# 日期循环器，每次处理一年，一年按照每个月处理
# 参数格式：'2021'
def solve_one_year(year):
    search_keyword('创新')
    for month in range(1, 13):
        print("当前正在处理第 {} 月的数据.".format(month))
        if month < 9:
            startTime = year+'-0'+str(month)+'-01'
            endTime = year+'-0'+str(month+1)+'-01'
            print(startTime)
            print(endTime)
            select_time(startTime, endTime) # 已经sleep3保证重新加载
        elif month == 9:
            startTime = year+'-09-01'
            endTime = year+'-10-01'
            print(startTime)
            print(endTime)
            select_time(startTime, endTime) # 已经sleep3保证重新加载
        elif month == 12:
            startTime = year+'-12-01'
            endTime = str(int(year)+1)+'-01-01'
            print(startTime)
            print(endTime)
            select_time(startTime, endTime) # 已经sleep3保证重新加载
        else:
            startTime = year+'-'+str(month)+'-01'
            endTime = year+'-'+str(month+1)+'-01'
            print(startTime)
            print(endTime)
            select_time(startTime, endTime) # 已经sleep3保证重新加载
        page_no = 1
        while(True):
            sleep(1)
            print("当前正在处理第 {} 页数据".format(page_no))
            page_no += 1
            solve_this_page()
            nextPage = wd.find_elements(By.CSS_SELECTOR, ".middle-con-left-bottom .m-style .next") # 若下一页不存在，class有一个别名disabled
            endPage = wd.find_elements(By.CSS_SELECTOR, ".middle-con-left-bottom .m-style .disabled")
            if len(endPage) == 0: # endPage空的时候nextPage必不为空
                nextPage[0].click()
            else:
                print("已经是最后一页")
                break

# 具体开始工作时，要先检索关键词，再select时间，再处理每一页内容

# 按照给定时间处理，但是给定时间段不能超过500个检索结果
# 例如：'2021-01-01','2021-02-01'
def solve_by_time(startTime, endTime):
    search_keyword('创新')
    select_time(startTime, endTime) # 已经sleep3保证重新加载
    page_no = 1
    while(True):
        sleep(1)
        print("当前正在处理第 {} 页数据".format(page_no))
        page_no += 1
        solve_this_page()
        nextPage = wd.find_elements(By.CSS_SELECTOR, ".middle-con-left-bottom .m-style .next") # 若下一页不存在，class有一个别名disabled
        endPage = wd.find_elements(By.CSS_SELECTOR, ".middle-con-left-bottom .m-style .disabled")
        if len(endPage) == 0: # endPage空的时候nextPage必不为空
            nextPage[0].click()
        else:
            print("已经是最后一页")
            break

# 输入年份，自动按照每月处理
# solve_one_year('2017')

# 按照输入时间段查询，若结果数量>=500无法处理
# solve_by_time('2021-12-01','2022-01-01')

# 全自动处理
yearList = ['2014', '2013']
for year in yearList:
    solve_one_year(year)
    file_control.solve(year)
    # wd.close() # 这里一定不能关，直接重新wd.get就行，相当于刷新

wd.quit()







