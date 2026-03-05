import re

import jieba

# ==== 1. 初始化配置 ====
basic_config_data = """
护肤品    套装类      套装    三件套    礼盒    礼盒装    旅行装    中样    装    盒
护肤品    乳液类      乳液    美白乳    润肤乳    凝乳    柔肤液    亮肤乳    菁华乳    修护乳    护手霜    轻乳
护肤品    眼部护理    眼霜    眼部精华    眼膜    眼部啫喱    眼精华    眼部水
护肤品    面膜类      面膜    贴片面膜    睡眠面膜    泥膜    免洗面膜    膜    面贴膜
护肤品    清洁类    洗面    清洁    洁面    洗面奶    洗面膏    洁面膏    洁面乳    洁颜    洸颜    卸妆    卸妆水    卸妆油    卸妆乳    去角质    磨砂    洗颜    洗颜霜    深层清洁    凝露    卸妆液
护肤品    水类        化妆水    爽肤水    柔肤水    补水露    精粹水    亮肤水    亮肤    润肤水    保湿水    胶原水    喷雾    舒缓喷雾    美容液     护肤水    男士护肤水    菁华水    红水
护肤品    面霜类      面霜    日霜    晚霜    清爽霜    滋润霜    保湿霜    凝霜    早安霜    底霜    乳霜    修护霜    亮肤霜    控霜    日间霜    日用霜    柔肤霜    晚间霜    菁华霜    早安霜
护肤品    精华类      精华    精华液    精华水    精华露    精华素    原液    安瓶    精华油    夜乳    夜霜    健肤水    润唇膏
护肤品    防晒类      防晒霜    防晒乳    防晒喷雾    防晒露    防晒液    防晒啫喱    隔离霜    晒后修护    修护露
化妆品    口红类    唇釉    口红    唇彩    唇膏    唇泥
化妆品    底妆类      粉底液    粉底霜    粉底膏    粉饼    气垫    BB霜    CC霜    散粉    蜜粉    定妆粉    遮瑕    肌底液    粉霜    修颜霜    隔离    妆前乳    粉扑
# 化妆品    眼部彩妆    眉粉    眉笔    染眉膏    眉膏    眼线    眼线笔    眼线液    眼影    睫毛膏    睫毛底膏    睫毛夹    假睫毛    涂眼影笔
化妆品    修容类      腮红    鼻影    修容粉    高光    高光棒    修容棒    阴影粉
其他    其他    其他
"""
test_cases = [
"资生堂新透白美肌光感焕采亮肤乳SPF30+/PA+++"

]
# ==== 3. 自定义词典 ====
jieba.add_word("补水露")
jieba.add_word("男士控油")
jieba.add_word("洗面奶")
jieba.add_word("活泉深层")
jieba.add_word("洁面膏")
jieba.add_word("洗颜霜")  # 新增
jieba.add_word("眼线笔")  # 新增
jieba.add_word("亮肤乳")  # 新增
jieba.add_word("亮肤霜")  # 新增
jieba.add_word("亮肤水")  # 新增
jieba.add_word("妆前乳")  # 新增
jieba.add_word("底霜")  # 新增
jieba.add_word("假睫毛")  # 新增
jieba.add_word("眼影笔")  # 新增
jieba.add_word("元气霜")  # 新增



def req_tb():
    # ==== 2. 生成分类映射 ====
    category_config_map = {}
    for config_line in basic_config_data.split('\n'):
        parts = re.split(r'\s{2,}', config_line.strip())
        if len(parts) < 3:
            continue
        main, sub = parts[0], parts[1]
        for keyword in parts[2:]:
            category_config_map[keyword] = (main, sub)

    def preprocess_title(title):
        # 去除括号及其内容（如 "(干性肌肤适用)"）
        title = re.sub(r'\([^)]*\)', '', str(title))
        # 去除非中文、字母、数字外的符号
        # title = re.sub(r'[^\u4e00-\u9fa5,a-z,A-Z,0-9]', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip()
        return title

    # ==== 5. 分类函数 ====
    def classify_product(cut_words):
        # 匹配 2-gram
        for i in range(len(cut_words) - 1):
            bigram = cut_words[i] + cut_words[i + 1]
            if bigram in category_config_map:
                return category_config_map[bigram]
        # 按词长降序匹配
        sorted_words = sorted(cut_words, key=lambda x: len(x), reverse=True)
        for word in sorted_words:
            if word in category_config_map:
                return category_config_map[word]
        return ("其他", "其他")


    for title in test_cases:
        clean_title = preprocess_title(title)
        cut_words = jieba.lcut(clean_title)
        main, sub = classify_product(cut_words)
        print(f"标题: {title}")
        print(f"分词: {cut_words}")
        print(f"分类: {main} - {sub}\n")
    # tb = requests.get("https://taobao.com")
    # print(tb)


req_tb()

