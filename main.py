import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import ScalarFormatter

# 全局配置：中文显示与 pandas 输出格式、禁用科学计数
plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体
plt.rcParams['axes.unicode_minus'] = False  # 负号显示
pd.set_option('display.float_format', '{:.2f}'.format)

# 中英文列名映射
COLUMN_MAPPING = {
    'update_time': '更新时间', 'id': '商品ID', 'title': '商品名称',
    'price': '价格', 'sale_count': '销量', 'comment_count': '评论数',
    '店名': '品牌名称', 'sub_type': '子类别', 'main_type': '主类别',
    '是否为男士专用': '是否男士专用', '销售额': '销售额', 'day': '天数'
}

def load_data(filepath: str) -> pd.DataFrame:
    """加载并预处理数据：重命名列（英文->中文）"""
    df = pd.read_excel(filepath)
    df.rename(columns=COLUMN_MAPPING, inplace=True)
    return df


def truncate_float(num: float, decimals: int = 2) -> float:
    """截断浮点数而非四舍五入，保留指定小数位"""
    s = f"{num:.{decimals+5}f}"  # 预留余量
    integer, dot, fraction = s.partition('.')
    return float(f"{integer}.{fraction[:decimals]}")


def plot_brand_sku(df: pd.DataFrame):
    """各品牌 SKU 数柱状图，添加数据标签"""
    counts = df['品牌名称'].value_counts().sort_values(ascending=False)
    plt.figure(figsize=(12, 9))
    bars = counts.plot.bar(width=0.8, alpha=0.6)
    # 禁用科学计数
    bars.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
    plt.title('各品牌 SKU 数', fontsize=18)
    plt.ylabel('商品数量', fontsize=14)
    plt.xticks(rotation=45)
    # 添加标签
    for p in bars.patches:
        bars.text(
            p.get_x()+p.get_width()/2, p.get_height(),
            int(p.get_height()), ha='center', va='bottom', fontsize=9
        )
    plt.tight_layout()
    plt.show()


def analyze_shop(df: pd.DataFrame) -> pd.DataFrame:
    """品牌销售额与销量分析，并添加数据标签"""
    agg = df.groupby('品牌名称')[['销售额', '销量']].sum()
    fig, axes = plt.subplots(2, 1, figsize=(14, 12))
    for ax, metric in zip(axes, ['销售额', '销量']):
        data = agg[metric].sort_values(ascending=False)
        # 单位换算
        if metric == '销售额':
            disp = data / 1e8; unit = '亿元'
        else:
            disp = data / 1e4; unit = '万'
        bars = disp.plot.bar(ax=ax, alpha=0.8, edgecolor='k')
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
        ax.set_title(f'各品牌 {metric} 对比（单位：{unit}）', fontsize=15)
        ax.set_xlabel('品牌名称'); ax.set_ylabel(f'{metric}（{unit}）')
        ax.tick_params(rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        for p in bars.patches:
            ax.text(
                p.get_x()+p.get_width()/2, p.get_height(),
                truncate_float(p.get_height(), 2), ha='center', va='bottom', fontsize=9
            )
    plt.tight_layout(); plt.show()
    return agg.sort_values('销售额', ascending=False)


def plot_category_distribution(df: pd.DataFrame):
    """主/子类别销量占比饼图"""
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    for ax, col, title, start in zip(
        axes, ['主类别', '子类别'], ['主类别销售量占比', '子类别销售量占比'], [60, 230]
    ):
        data = df.groupby(col)['销量'].sum()
        wedges, texts, autotexts = ax.pie(
            data, labels=data.index,
            autopct='%.1f%%', pctdistance=0.8,
            startangle=start, radius=1.2, counterclock=False,
            wedgeprops={'linewidth':1.2}, textprops={'fontsize':14}
        )
        ax.set_title(title, fontsize=18)
    plt.subplots_adjust(wspace=0.4); plt.show()


def plot_brand_category(df: pd.DataFrame):
    """品牌-主/子类别对比图，添加数据标签"""
    for metric in ['销量', '销售额']:
        plt.figure(figsize=(18, 6))
        bars = sns.barplot(
            x='品牌名称', y=metric, hue='主类别', data=df,
            saturation=0.75, errorbar=None
        )
        bars.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
        plt.title(f'各品牌各主类别{metric}对比'); plt.xticks(rotation=45)
        plt.tight_layout(); plt.show()
    for metric in ['销量', '销售额']:
        plt.figure(figsize=(18, 6))
        bars = sns.barplot(
            x='品牌名称', y=metric, hue='子类别', data=df,
            saturation=0.75, errorbar=None
        )
        bars.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
        plt.title(f'各品牌各子类别{metric}对比'); plt.xticks(rotation=45)
        plt.tight_layout(); plt.show()


def plot_brand_popularity(df: pd.DataFrame):
    """品牌热度分析，数据标签添加"""
    avg_comments = df.groupby('品牌名称')['评论数'].mean().sort_values(ascending=False)
    plt.figure(figsize=(12, 6))
    bars = avg_comments.plot.bar(width=0.8)
    bars.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
    plt.title('各品牌平均评论数'); plt.xticks(rotation=45)
    for p in bars.patches:
        bars.text(p.get_x()+p.get_width()/2, p.get_height(), truncate_float(p.get_height(),2), ha='center', va='bottom', fontsize=9)
    plt.tight_layout(); plt.show()

    agg = df.groupby('品牌名称').agg({'销量':'mean','评论数':'mean','价格':'mean'})
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(
        agg['销量'], agg['评论数'], s=agg['价格']*10, alpha=0.7
    )
    for idx, row in agg.iterrows():
        plt.text(row['销量'], row['评论数'], idx)
    plt.xlabel('平均销量'); plt.ylabel('平均评论数')
    plt.title('品牌销量 vs 评论热度（气泡=均价）'); plt.grid(True); plt.tight_layout(); plt.show()


def plot_price_distribution(df: pd.DataFrame):
    """价格分析及平均价格线与标签"""
    plt.figure(figsize=(14, 8))
    sns.boxplot(x='品牌名称', y='价格', data=df)
    plt.ylim(0, 3000); plt.xticks(rotation=45); plt.title('各品牌价格分布'); plt.tight_layout(); plt.show()

    avg_price = df.groupby('品牌名称')['价格'].mean().sort_values(ascending=False)
    overall_avg = df['价格'].mean()
    plt.figure(figsize=(12, 6))
    bars = avg_price.plot.bar(alpha=0.6)
    bars.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
    plt.axhline(overall_avg, linestyle='--', label=f"全品牌平均: {truncate_float(overall_avg,2)}")
    plt.title('各品牌平均价格'); plt.ylabel('平均价格'); plt.xticks(rotation=45)
    for p in bars.patches:
        bars.text(p.get_x()+p.get_width()/2, p.get_height(), truncate_float(p.get_height(),2), ha='center', va='bottom', fontsize=9)
    plt.legend(); plt.tight_layout(); plt.show()


def plot_gender_products(df: pd.DataFrame):
    """男士专用产品销量与销售额对比，添加标签"""
    df['是否男士专用'] = df['是否男士专用'].str.strip()
    male_df = df[(df['是否男士专用']=='是')&(df['主类别'].isin(['护肤品','化妆品']))]
    plt.figure(figsize=(12, 6))
    bars = sns.barplot(x='品牌名称', y='销量', hue='主类别', data=male_df, errorbar=None)
    bars.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
    plt.title('男士专用产品销量对比'); plt.xticks(rotation=45)
    for p in bars.patches:
        bars.text(p.get_x()+p.get_width()/2, p.get_height(), truncate_float(p.get_height(),2), ha='center', va='bottom', fontsize=8)
    plt.tight_layout(); plt.show()

    totals = male_df.groupby('品牌名称')[['销量','销售额']].sum()
    fig, axes = plt.subplots(1,2,figsize=(14,6))
    for ax, metric in zip(axes, ['销量','销售额']):
        bars = totals[metric].sort_values().plot.barh(ax=ax)
        ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=False))
        ax.set_title(f"男士护肤品{metric}排名")
        for p in bars.patches:
            ax.text(p.get_width(), p.get_y()+p.get_height()/2, truncate_float(p.get_width(),2), va='center', fontsize=8)
    plt.tight_layout(); plt.show()


def plot_time_series(df: pd.DataFrame):
    """日销量时间序列趋势图，显示具体值"""
    df['天数'] = df['天数'].astype(int)
    daily = df.groupby('天数')['销量'].sum()
    plt.figure(figsize=(12, 6))
    plt.plot(daily.index, daily.values, marker='o')
    for x, y in zip(daily.index, daily.values):
        plt.text(x, y, int(y), ha='center', va='bottom', fontsize=8)
    plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
    plt.title('11月日销量趋势'); plt.xlabel('天数'); plt.ylabel('销量')
    plt.gca().xaxis.set_major_locator(plt.MultipleLocator(1))
    plt.grid(True, linestyle='-.', alpha=0.5); plt.tight_layout(); plt.show()


if __name__ == '__main__':
    df = load_data('data/clean_beautymakeup.xlsx')
    print(df.head(10))
    plot_brand_sku(df)
    stats = analyze_shop(df); print(stats)
    plot_category_distribution(df)
    plot_brand_category(df)
    plot_brand_popularity(df)
    plot_price_distribution(df)
    plot_gender_products(df)
    plot_time_series(df)