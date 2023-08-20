import streamlit as st
import pandas as pd
import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Pie, Bar, Grid
from streamlit_echarts import st_pyecharts
import re
from collections import Counter
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import folium
from streamlit_folium import st_folium
import seaborn as sns
import random

st.set_page_config(
    page_title="My Streamlit App",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    .stApp {
        max-width: 1300px;  /* Adjust the max-width to control the width of the page */
        margin: 0 auto;  /* Center the content horizontally */
        padding: 0 20px;  /* Adjust the padding to control the side white space */
        max-height:10000px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def change_date_1(x):
    try:
        return datetime.strptime(x, '%m/%d/%Y')
    except:
        try:
            return datetime.strptime(x, '%d.%m.%Y')
        except:
            return datetime.today().date()

def change_date_2(x):
    try:
        return datetime.strptime(x, '%m/%d/%Y')
    except:
        try:
            return datetime.strptime(x, '%d.%m.%Y')
        except:
            return None

def generate_date_range(start_date, end_date):
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date)
        current_date += relativedelta(months=1)
    return date_range

def remove_duplicates(input_list):
    output_list = []
    seen = set()
    for item in input_list:
        if item not in seen:
            output_list.append(item)
            seen.add(item)
    return output_list

def generate_distinct_colors(num_colors):
    """Generate a list of distinct colors using ColorBrewer palette."""
    color_palette = sns.color_palette("Set1", n_colors=num_colors)
    distinct_colors = [sns.color_palette([color])[0] for color in color_palette]
    return distinct_colors

def generate_distinct_colors_dict(things):
    num_colors = len(things)
    returned_dict = {}
    for i in range(num_colors):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        hex_color = "#{:02X}{:02X}{:02X}".format(r, g, b)
        returned_dict[things[i]] = hex_color
    return returned_dict

st.title("Hydrogen Data Visualization 氢气数据可视化")

selected_topic = st.selectbox("Select a topic to visualize: \n选择一个话题进行展示:",
                                ["Hydrogen Fueling Stations\n加氢站", "Hydrogen Safety Incidents\n氢气安全事故"])
if selected_topic == "Hydrogen Fueling Stations\n加氢站":
    st.header("Hydrogen Fueling Stations 加氢站")
    df = pd.read_csv("hydrogen stations chinese english data.csv",index_col=[0])
    df_companies = pd.read_csv("companies data chinese english.csv",index_col=[0])
    df_companies["CompanyName\n公司名称"] = df_companies["CompanyName\n公司名称"].apply(lambda x: " ".join(x.split("\n")))
    df.iloc[:,-8:] = df.iloc[:,-8:].fillna(0)
    
    df[["EndDate\n结束日期","UpdateDate\n更新日期"]] = df[["EndDate\n结束日期","UpdateDate\n更新日期"]].applymap(change_date_1)
    df[["StartDate\n开始日期"]] = df[["StartDate\n开始日期"]].applymap(change_date_2)
    
    selected_option_4 = st.radio("Select an option\n选择一个选项",["Show in Charts\n以图表展示","Show in Maps\n以地图展示","Show Raw Data\n展示原始数据"])
    if selected_option_4 == "Show in Charts\n以图表展示":
        selected_option = st.selectbox("Select a category to visualize: \n选择一个类别进行展示:",
                                    ["Status\n状态", "PublicAccess\n公共访问", "Country\n国家", "Continent\n洲", "Fuel\n燃料", "Operator\n运营商","TechnologyProvider\n技术提供商","Partner\n合作伙伴"])
        if selected_option in ["Status\n状态", "PublicAccess\n公共访问", "Continent\n洲"]:
            selected_option_2 = st.radio("Select an option\n选择一个选项", ["Show Stations in All Years\n展示所有年份的加氢站", "Show Stations by Year\n按年份展示加氢站","Show Stations by Years in Histograms\n按年份通过分布图展示加氢站"], index=0)
            if selected_option_2 == "Show Stations in All Years\n展示所有年份的加氢站":
                pie_data = list(Counter(df[selected_option]).items())
                title_dict = {
                    "Status\n状态": "Status of Hydrogen Stations\n加氢站状态",
                    "PublicAccess\n公共访问": "Public Accesses of Hydrogen Stations\n加氢站公共获取情况",
                    "Continent\n洲": "Continents of Hydrogen Stations\n加氢站分布大洲"
                }
                pie_chart = (
                    Pie()
                    .add("", pie_data, radius=["30%", "70%"])
                    .set_global_opts(title_opts=opts.TitleOpts(title=f"{title_dict[selected_option]}\nOut of all stations in the record",
                                                            pos_bottom="85%", pos_left="8%",
                                                            ),
                                                            graphic_opts=[
                    opts.GraphicGroup(
                        graphic_item=opts.GraphicItem(
                            bounding="raw",
                            right="5%",
                            top="10%",  # Adjust this value to add more space to the top
                            z=100,
                        )
                    )
            ],toolbox_opts=opts.ToolboxOpts(
            feature={
                "saveAsImage": {},
                "dataZoom": {},
                "restore": {},          # Restore to original state
                "brush": {},
                "dataView": {}
            }
        ),
                                legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center",padding=[10, 0, 50, 0],border_width=0),
                                )
                .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}:\n{c} ({d}%)"))
    )
                st_pyecharts(pie_chart, height=600)
            if selected_option_2 == "Show Stations by Year\n按年份展示加氢站":
                col4, col5 = st.columns([5,1])
                with col4:
                    start_date_2 = date(df["StartDate\n开始日期"].min().year,df["StartDate\n开始日期"].min().month,1)
                    end_date = date(datetime.today().date().year,datetime.today().date().month,1) - relativedelta(months=1)
                    for day in generate_date_range(start_date_2, end_date):
                        df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<day)&(df["EndDate\n结束日期"]>day+relativedelta(months=1))]
                        if sum([i[1] for i in list(Counter(df_partial[selected_option]).items())]) > 1:
                            break
                    start_date = day
                    step = timedelta(days=30)
                    date_range = [start_date + i * step for i in range(int((end_date - start_date) / step) + 1)]
                    col4.selected_month = st.select_slider("Select a month:",
                                                options=date_range,
                                                format_func=lambda date: date.strftime("%b %Y"))
                df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<col4.selected_month)&(df["EndDate\n结束日期"]>col4.selected_month+relativedelta(months=1))]
                pie_data = list(Counter(df[selected_option]).items())
                pie_data_partial = list(Counter(df_partial[selected_option]).items())
                for pair in pie_data:
                    if pair[0] not in [i[0] for i in pie_data_partial]:
                        pie_data_partial.append((pair[0],0))
                pie_data_partial = sorted(pie_data_partial,key=lambda x:x[0])
                title_dict = {
                    "Status\n状态": "Status of Hydrogen Stations\n加氢站状态",
                    "PublicAccess\n公共访问": "Public Accesses of Hydrogen Stations\n加氢站公共获取情况",
                    "Continent\n洲": "Continents of Hydrogen Stations\n加氢站分布大洲"
                }
                pie_chart = (
                    Pie()
                    .add("", pie_data_partial, radius=["30%", "70%"])
                    .set_global_opts(title_opts=opts.TitleOpts(title=f"{title_dict[selected_option]}\nOut of all stations operating\nIn {col4.selected_month.strftime('%b %Y')}",
                                                               pos_bottom="85%", pos_left="8%"),
                                    graphic_opts=[
                    opts.GraphicGroup(
                        graphic_item=opts.GraphicItem(
                            bounding="raw",
                            right="5%",
                            top="10%",  # Adjust this value to add more space to the top
                            z=100,
                        )
                    )
                ],toolbox_opts=opts.ToolboxOpts(
                feature={
                    "saveAsImage": {},
                    "dataZoom": {},
                    "restore": {},          # Restore to original state
                    "brush": {},
                    "dataView": {}
                }
            ),
            legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center",padding=[10, 0, 50, 0],border_width=0),
            )
                    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}:\n{c} ({d}%)"))
                )
                st_pyecharts(pie_chart, height=600)
            if selected_option_2 == "Show Stations by Years in Histograms\n按年份通过分布图展示加氢站":
                    start_date_2 = datetime(df["StartDate\n开始日期"].min().year,df["StartDate\n开始日期"].min().month,1)
                    end_date = datetime(datetime.today().date().year,datetime.today().date().month,1) - relativedelta(months=1)
                    for day in generate_date_range(start_date_2, end_date):
                        df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<day)&(df["EndDate\n结束日期"]>day+relativedelta(months=1))]
                        if sum([i[1] for i in list(Counter(df_partial[selected_option]).items())]) > 0:
                            break
                    start_date = day
                    step = timedelta(days=30)
                    date_range = [start_date + i * step for i in range(int((end_date - start_date) / step) + 1)]
                    index_list = sorted(remove_duplicates(list(df[selected_option])))
                    data = []
                    for date in date_range:
                        df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<date)&(df["EndDate\n结束日期"]>date+relativedelta(months=1))]
                        bar_data_2 = sorted(list(Counter(df_partial[selected_option]).items()),key=lambda x:x[0])
                        for i in index_list:
                            if i not in [i[0] for i in bar_data_2]:
                                bar_data_2.append((i,0))
                        bar_data_2 = dict(bar_data_2)
                        data.append(bar_data_2)
                    new_df = pd.DataFrame(data,index = date_range)
                    bar_chart = Bar().add_xaxis([datetime.strftime(i,"%b %Y") for i in new_df.index])#.add_yaxis("in Operation\n运行中", new_df["in Operation\n运行中"])
                    for option_2 in new_df.columns:
                        bar_chart.add_yaxis(option_2, list(new_df[option_2]),stack="stack_1", category_gap="-10%")
                    pattern = re.compile('\n[\u4e00-\u9fff]+')
                    bar_chart =(
                        bar_chart.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                        .set_global_opts(title_opts=opts.TitleOpts(title=f"Number of Stations\n加氢站数量\nStacked Bar Plot by {re.sub(pattern,'',selected_option)}"),
                                    yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=1050,interval=100),
                                    # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                    legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                    toolbox_opts=opts.ToolboxOpts(
                feature={
                    "saveAsImage": {},
                    "dataZoom": {},
                    "restore": {},          # Restore to original state
                    "brush": {},
                    "dataView": {}
                }
                )))
                    grid = Grid()
                    grid.add(
                        bar_chart,
                        grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%", pos_bottom="20%", pos_top="15%")  # Adjust the left and right padding as needed
                    )
                    st_pyecharts(grid, height=600, width=1000)
        
                    bar_chart_2 = Bar().add_xaxis([datetime.strftime(i,"%b %Y") for i in new_df.index])#.add_yaxis("in Operation\n运行中", new_df["in Operation\n运行中"])
                    for option_2 in new_df.columns:
                        bar_chart_2.add_yaxis(option_2, list((new_df[option_2]/new_df.sum(axis=1))*100),stack="stack_1", category_gap="-10%")
                    pattern = re.compile('\n[\u4e00-\u9fff]+')
                    bar_chart_2 =(
                    bar_chart_2.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                    .set_global_opts(title_opts=opts.TitleOpts(title=f"Percentage of Stations\n加氢站比例\nStacked Bar Plot by {re.sub(pattern,'',selected_option)}"),
                                    yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=105,interval=10),
                                    # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                    legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                    toolbox_opts=opts.ToolboxOpts(
                feature={
                    "saveAsImage": {},
                    "dataZoom": {},
                    "restore": {},          # Restore to original state
                    "brush": {},
                    "dataView": {}
                }
                )))
                    grid_2 = Grid()
                    grid_2.add(
                        bar_chart_2,
                        grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%",pos_bottom="20%")  # Adjust the left and right padding as needed
                    )
                    st_pyecharts(grid_2, height=600, width=1000)
        elif selected_option == "Country\n国家":
            selected_option_2 = st.radio("Select an option\n选择一个选项", ["Show Stations in All Years\n展示所有年份的加氢站", "Show Stations by Year\n按年份展示加氢站","Show Stations of a Country by Years\n按年份展示某国家的加氢站"], index=0)
            button_1 = st.checkbox("Show stacked bar plot")
            if button_1:
                selected_option_3 = st.selectbox("Select an option\n选择一个选项", ["Status\n状态", "PublicAccess\n公共访问", "Fuel\n燃料"], index=0)
            if selected_option_2 == "Show Stations in All Years\n展示所有年份的加氢站":
                if not button_1:
                    bar_data = sorted([(" ".join(i[0].split("\n")),i[1]) for i in list(Counter(df[selected_option]).items())],key=lambda x: x[1], reverse=True)[:20][::-1]
                    bar_chart = (
                        Bar()
                        .add_xaxis([i[0] for i in bar_data])
                        .add_yaxis("Number of Stations\n加氢站数量", [i[1] for i in bar_data])
                        .reversal_axis()
                        .set_global_opts(title_opts=opts.TitleOpts(title="Number of Stations in Top 20 Countries\n加氢站数量前二十国家"),
                                        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=350,interval=50),
                                        # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                        legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center",padding=[0, 0, 0, 0],border_width=0),
                                        toolbox_opts=opts.ToolboxOpts(
                    feature={
                        "saveAsImage": {},
                        "dataZoom": {},
                        "restore": {},          # Restore to original state
                        "brush": {},
                        "dataView": {}
                    }
                ))
                )
                    grid = Grid()
        
                    # Add padding to the left side of the chart
                    grid.add(
                        bar_chart,
                        grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%", pos_bottom="20%", pos_top="15%")  # Adjust the left and right padding as needed
                    )
                    st_pyecharts(grid, height=600, width=1000)
                else:
                    if selected_option_3 != "Fuel\n燃料":
                        bar_data_1 = sorted([("\n".join(i[0].split("\n")),i[1]) for i in list(Counter(df["Country\n国家"]).items())],key=lambda x: x[1], reverse=True)[:20][::-1]
                        index_list = list(set(list(df[selected_option_3])))
                        bar_data_2 = [i for i in list(Counter([(x, y) for x, y in zip(df['Country\n国家'], df[selected_option_3])]).items()) if i[0][0] in [i[0] for i in bar_data_1]]
                        pattern = re.compile('\n[\u4e00-\u9fff]+')
                        for country in list(set([i[0][0] for i in bar_data_2])):
                            for j in index_list:
                                if j not in [i[0][1] for i in bar_data_2 if i[0][0]==country]:
                                    bar_data_2.append(((country,j),0))
                        bar_data_2 = sorted(bar_data_2, key=lambda x:([i[0] for i in bar_data_1].index(x[0][0]),index_list.index(x[0][1])))
                        bar_data_3 = sorted([(" ".join(i[0].split("\n")),i[1]) for i in list(Counter(df["Country\n国家"]).items())],key=lambda x: x[1], reverse=True)[:20][::-1]
                        bar_chart = Bar().add_xaxis(remove_duplicates([i[0] for i in bar_data_3]))
                        for option_2 in index_list:
                            bar_chart.add_yaxis(option_2, [i[1] for i in bar_data_2 if i[0][1]==option_2],stack="stack_1")
                        bar_chart =(
                            bar_chart.reversal_axis()
                            .set_global_opts(title_opts=opts.TitleOpts(title=f"Number of Stations in Top 20 Countries\n加氢站数量前二十国家\nStacked Bar Plot by {re.sub(pattern,'',selected_option_3)}"),
                                            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=350,interval=50),
                                            # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                            legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center",padding=[0, 0, 0, 0],border_width=0),
                                            toolbox_opts=opts.ToolboxOpts(
                        feature={
                            "saveAsImage": {},
                            "dataZoom": {},
                            "restore": {},          # Restore to original state
                            "brush": {},
                            "dataView": {}
                        }
                    )))
                        grid = Grid()
                        grid.add(
                            bar_chart,
                            grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%", pos_bottom="20%", pos_top="15%")  # Adjust the left and right padding as needed
                        )
                        st_pyecharts(grid, height=600, width=1000)
                    else:
                        df.columns = list(df.columns[:-8])+[re.sub("Fuel(\d) |燃料(\d) ","",i,re.I) for i in list(df.columns[-8:])]
                        bar_data_1 = sorted([("\n".join(i[0].split("\n")),i[1]) for i in list(Counter(df["Country\n国家"]).items())],key=lambda x: x[1], reverse=True)[:20][::-1]
                        index_list = list(df.columns[-8:])
                        bar_data_2 = []
                        for column in index_list:
                            bar_data_2 += [((i[0],re.sub("Fuel(\d) |燃料(\d) ","",column,re.I)),i[1]) for i in list(Counter(df.loc[df[column] == 1,"Country\n国家"]).items()) if i[0] in [i[0] for i in bar_data_1]]
                        for column in index_list:
                            for country in remove_duplicates([i[0] for i in bar_data_1]):
                                for j in index_list:
                                    if j not in [i[0][1] for i in bar_data_2 if i[0][0]==country]:
                                        bar_data_2.append(((country,j),0))
                        pattern = re.compile('\n[\u4e00-\u9fff]+')
                        bar_data_2 = sorted(bar_data_2, key=lambda x:([i[0] for i in bar_data_1].index(x[0][0]),index_list.index(x[0][1])))
                        bar_data_3 = sorted([(" ".join(i[0].split("\n")),i[1]) for i in list(Counter(df["Country\n国家"]).items())],key=lambda x: x[1], reverse=True)[:20][::-1]
                        bar_chart = Bar().add_xaxis(remove_duplicates([i[0] for i in bar_data_3]))
                        for option_2 in index_list:
                            bar_chart.add_yaxis(option_2, [i[1] for i in bar_data_2 if i[0][1]==option_2],stack="stack_1")
                        bar_chart =(
                            bar_chart.reversal_axis()
                            .set_global_opts(title_opts=opts.TitleOpts(title=f"Number of Stations in Top 20 Countries\n加氢站数量前二十国家\nStacked Bar Plot by {re.sub(pattern,'',selected_option_3)}"),
                                            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=350,interval=50),
                                            # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                            legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                            toolbox_opts=opts.ToolboxOpts(
                        feature={
                            "saveAsImage": {},
                            "dataZoom": {},
                            "restore": {},          # Restore to original state
                            "brush": {},
                            "dataView": {}
                        }
                    )))
                        grid = Grid()
                        grid.add(
                            bar_chart,
                            grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%", pos_bottom="20%", pos_top="15%")  # Adjust the left and right padding as needed
                        )
                        st_pyecharts(grid, height=600, width=1000)
            if selected_option_2 == "Show Stations by Year\n按年份展示加氢站":
                col4, col5 = st.columns([5,1])
                with col4:
                    start_date_2 = datetime(df["StartDate\n开始日期"].min().year,df["StartDate\n开始日期"].min().month,1)
                    end_date = datetime(datetime.today().date().year,datetime.today().date().month,1) - relativedelta(months=1)
                    for day in generate_date_range(start_date_2, end_date):
                        df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<day)&(df["EndDate\n结束日期"]>day+relativedelta(months=1))]
                        if sum([i[1] for i in list(Counter(df_partial[selected_option]).items())]) > 50:
                            break
                    start_date = day
                    step = timedelta(days=30)
                    date_range = [start_date + i * step for i in range(int((end_date - start_date) / step) + 1)]
                    col4.selected_month = st.select_slider("Select a month:",
                                                options=date_range,
                                                format_func=lambda date: date.strftime("%b %Y"))
                df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<col4.selected_month)&(df["EndDate\n结束日期"]>col4.selected_month+relativedelta(months=1))]
                if not button_1:
                    bar_data_partial = sorted([(" ".join(i[0].split("\n")),i[1]) for i in list(Counter(df_partial[selected_option]).items())],key=lambda x: x[1], reverse=True)[:20][::-1]
                    bar_chart = (
                        Bar()
                        .add_xaxis([i[0] for i in bar_data_partial])
                        .add_yaxis("Number of Stations\n加氢站数量", [i[1] for i in bar_data_partial])
                        .reversal_axis()
                        .set_global_opts(title_opts=opts.TitleOpts(title=f"Number of Stations in Top 20 Countries in {datetime.strftime(col4.selected_month,'%b %Y')}\n加氢站数量前二十国家"),
                                        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=200,interval=10),
                                        # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                        legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center",padding=[0, 0, 0, 0],border_width=0),
                                        toolbox_opts=opts.ToolboxOpts(
                    feature={
                        "saveAsImage": {},
                        "dataZoom": {},
                        "restore": {},          # Restore to original state
                        "brush": {},
                        "dataView": {}
                    }
                ))
                )
                    grid = Grid()
        
                    # Add padding to the left side of the chart
                    grid.add(
                        bar_chart,
                        grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%", pos_bottom="20%", pos_top="15%")  # Adjust the left and right padding as needed
                    )
                    st_pyecharts(grid, height=600, width=1000)
                else:
                    if selected_option_3 != "Fuel\n燃料":
                        bar_data_1 = sorted([("\n".join(i[0].split("\n")),i[1]) for i in list(Counter(df_partial["Country\n国家"]).items())],key=lambda x: x[1], reverse=True)[:20][::-1]
                        index_list = list(set(list(df[selected_option_3])))
                        bar_data_2 = [i for i in list(Counter([(x, y) for x, y in zip(df_partial['Country\n国家'], df_partial[selected_option_3])]).items()) if i[0][0] in [i[0] for i in bar_data_1]]
                        for country in list(set([i[0][0] for i in bar_data_2])):
                            for j in index_list:
                                if j not in [i[0][1] for i in bar_data_2 if i[0][0]==country]:
                                    bar_data_2.append(((country,j),0))
                        pattern = re.compile('\n[\u4e00-\u9fff]+')
                        bar_data_2 = sorted(bar_data_2, key=lambda x:([i[0] for i in bar_data_1].index(x[0][0]),index_list.index(x[0][1])))
                        bar_data_3 = sorted([(" ".join(i[0].split("\n")),i[1]) for i in list(Counter(df_partial["Country\n国家"]).items())],key=lambda x: x[1], reverse=True)[:20][::-1]
                        bar_chart = Bar().add_xaxis(remove_duplicates([i[0] for i in bar_data_3]))
                        for option_2 in index_list:
                            bar_chart.add_yaxis(option_2, [i[1] for i in bar_data_2 if i[0][1]==option_2],stack="stack_1")
                        bar_chart =(
                            bar_chart.reversal_axis()
                            .set_global_opts(title_opts=opts.TitleOpts(title=f"Number of Stations in Top 20 Countries\n加氢站数量前二十国家\nStacked Bar Plot by {re.sub(pattern,'',selected_option_3)} in {datetime.strftime(col4.selected_month,'%b %Y')}"),
                                            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=200,interval=10),
                                            # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                            legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                            toolbox_opts=opts.ToolboxOpts(
                        feature={
                            "saveAsImage": {},
                            "dataZoom": {},
                            "restore": {},          # Restore to original state
                            "brush": {},
                            "dataView": {}
                        }
                    )))
                        grid = Grid()
                        grid.add(
                            bar_chart,
                            grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%", pos_bottom="20%", pos_top="15%")  # Adjust the left and right padding as needed
                        )
                        st_pyecharts(grid, height=600, width=1000)
                    else:
                        df_partial.columns = list(df_partial.columns[:-8])+[re.sub("Fuel(\d) |燃料(\d) ","",i,re.I) for i in list(df_partial.columns[-8:])]
                        bar_data_1 = sorted([("\n".join(i[0].split("\n")),i[1]) for i in list(Counter(df_partial["Country\n国家"]).items())],key=lambda x: x[1], reverse=True)[:20][::-1]
                        index_list = list(df_partial.columns[-8:])
                        bar_data_2 = []
                        for column in index_list:
                            bar_data_2 += [((i[0],re.sub("Fuel(\d) |燃料(\d) ","",column,re.I)),i[1]) for i in list(Counter(df_partial.loc[df_partial[column] == 1,"Country\n国家"]).items()) if i[0] in [i[0] for i in bar_data_1]]
                        for column in index_list:
                            for country in remove_duplicates([i[0] for i in bar_data_1]):
                                for j in index_list:
                                    if j not in [i[0][1] for i in bar_data_2 if i[0][0]==country]:
                                        bar_data_2.append(((country,j),0))
                        pattern = re.compile('\n[\u4e00-\u9fff]+')
                        bar_data_2 = sorted(bar_data_2, key=lambda x:([i[0] for i in bar_data_1].index(x[0][0]),index_list.index(x[0][1])))
                        bar_data_3 = sorted([(" ".join(i[0].split("\n")),i[1]) for i in list(Counter(df_partial["Country\n国家"]).items())],key=lambda x: x[1], reverse=True)[:20][::-1]
                        bar_chart = Bar().add_xaxis(remove_duplicates([i[0] for i in bar_data_3]))
                        for option_2 in index_list:
                            bar_chart.add_yaxis(option_2, [i[1] for i in bar_data_2 if i[0][1]==option_2],stack="stack_1")
                        bar_chart =(
                            bar_chart.reversal_axis()
                            .set_global_opts(title_opts=opts.TitleOpts(title=f"Number of Stations in Top 20 Countries\n加氢站数量前二十国家\nStacked Bar Plot by {re.sub(pattern,'',selected_option_3)} in {datetime.strftime(col4.selected_month,'%b %Y')}"),
                                            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=200,interval=10),
                                            # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                            legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                            toolbox_opts=opts.ToolboxOpts(
                        feature={
                            "saveAsImage": {},
                            "dataZoom": {},
                            "restore": {},          # Restore to original state
                            "brush": {},
                            "dataView": {}
                        }
                        )))
                        grid = Grid()
                        grid.add(
                            bar_chart,
                            grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%", pos_bottom="20%", pos_top="15%")  # Adjust the left and right padding as needed
                        )
                        st_pyecharts(grid, height=600, width=1000)
        
            if selected_option_2 == "Show Stations of a Country by Years\n按年份展示某国家的加氢站":
                selected_option_3 = st.selectbox("Select an option\n选择一个选项", ["Status\n状态", "PublicAccess\n公共访问", "Fuel\n燃料"], index=0, key="selected_option_3")
                if selected_option_3 != "Fuel\n燃料":
                    selected_country = st.selectbox("Select a country\n选择一个国家",remove_duplicates(sorted(list(df["Country\n国家"]))),index=remove_duplicates(sorted(list(df["Country\n国家"]))).index("Japan\n日本"))
                    df = df[df["Country\n国家"]==selected_country]
                    start_date_2 = datetime(df["StartDate\n开始日期"].min().year,df["StartDate\n开始日期"].min().month,1)
                    end_date = datetime(datetime.today().date().year,datetime.today().date().month,1) - relativedelta(months=1)
                    for day in generate_date_range(start_date_2, end_date):
                        df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<day)&(df["EndDate\n结束日期"]>day+relativedelta(months=1))]
                        if sum([i[1] for i in list(Counter(df_partial[selected_option_3]).items())]) > 0:
                            break
                    start_date = day
                    step = timedelta(days=30)
                    date_range = [start_date + i * step for i in range(int((end_date - start_date) / step) + 1)]
                    index_list = sorted(remove_duplicates(list(df[selected_option_3])))
                    data = []
                    for date in date_range:
                        df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<date)&(df["EndDate\n结束日期"]>date+relativedelta(months=1))]
                        bar_data_2 = sorted(list(Counter(df_partial[selected_option_3]).items()),key=lambda x:x[0])
                        for i in index_list:
                            if i not in [i[0] for i in bar_data_2]:
                                bar_data_2.append((i,0))
                        bar_data_2 = dict(bar_data_2)
                        data.append(bar_data_2)
                    new_df = pd.DataFrame(data,index = date_range)
                    bar_chart = Bar().add_xaxis([datetime.strftime(i,"%b %Y") for i in new_df.index])#.add_yaxis("in Operation\n运行中", new_df["in Operation\n运行中"])
                    for option_2 in new_df.columns:
                        bar_chart.add_yaxis(option_2, list(new_df[option_2]),stack="stack_1", category_gap="-10%")
                    english_name,chinese_name = selected_country.split('\n')
                    pattern = re.compile('\n[\u4e00-\u9fff]+')
                    bar_chart =(
                        bar_chart.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                        .set_global_opts(title_opts=opts.TitleOpts(title=f"Number of Stations in {english_name}\n{chinese_name}加氢站数量\nStacked Bar Plot by {re.sub(pattern,'',selected_option_3)}"),
                                        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=200,interval=10),
                                        # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                        legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                        toolbox_opts=opts.ToolboxOpts(
                    feature={
                        "saveAsImage": {},
                        "dataZoom": {},
                        "restore": {},          # Restore to original state
                        "brush": {},
                        "dataView": {}
                    }
                    )))
                    grid = Grid()
                    grid.add(
                        bar_chart,
                        grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%", pos_bottom="20%", pos_top="15%")  # Adjust the left and right padding as needed
                    )
                    st_pyecharts(grid, height=600, width=1000)
        
                    bar_chart_2 = Bar().add_xaxis([datetime.strftime(i,"%b %Y") for i in new_df.index])#.add_yaxis("in Operation\n运行中", new_df["in Operation\n运行中"])
                    for option_2 in new_df.columns:
                        bar_chart_2.add_yaxis(option_2, list((new_df[option_2]/new_df.sum(axis=1))*100),stack="stack_1", category_gap="-10%")
                    english_name,chinese_name = selected_country.split('\n')
                    pattern = re.compile('\n[\u4e00-\u9fff]+')
                    bar_chart_2 =(
                        bar_chart_2.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                        .set_global_opts(title_opts=opts.TitleOpts(title=f"Percentage of Stations in {english_name}\n{chinese_name}加氢站比例\nStacked Bar Plot by {re.sub(pattern,'',selected_option_3)}"),
                                        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=105,interval=10),
                                        # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                        legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                        toolbox_opts=opts.ToolboxOpts(
                    feature={
                        "saveAsImage": {},
                        "dataZoom": {},
                        "restore": {},          # Restore to original state
                        "brush": {},
                        "dataView": {}
                    }
                    )))
                    grid_2 = Grid()
                    grid_2.add(
                        bar_chart_2,
                        grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%",pos_bottom="20%")  # Adjust the left and right padding as needed
                    )
                    st_pyecharts(grid_2, height=600, width=1000)
                else:
                    selected_country = st.selectbox("Select a country\n选择一个国家",remove_duplicates(sorted(list(df["Country\n国家"]))),index=remove_duplicates(sorted(list(df["Country\n国家"]))).index("Japan\n日本"))
                    df = df[df["Country\n国家"]==selected_country]
                    start_date_2 = datetime(df["StartDate\n开始日期"].min().year,df["StartDate\n开始日期"].min().month,1)
                    end_date = datetime(datetime.today().date().year,datetime.today().date().month,1) - relativedelta(months=1)
                    for day in generate_date_range(start_date_2, end_date):
                        df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<day)&(df["EndDate\n结束日期"]>day+relativedelta(months=1))]
                        if sum(df_partial.iloc[:,-8:].sum(axis=1)) > 0:
                            break
                    start_date = day
                    step = timedelta(days=30)
                    date_range = [start_date + i * step for i in range(int((end_date - start_date) / step) + 1)]
                    index_list = list(df_partial.columns)[-8:]
                    data = []
                    for date in date_range:
                        df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<date)&(df["EndDate\n结束日期"]>date+relativedelta(months=1))]
                        bar_data_2 = dict(df_partial.iloc[:,-8:].sum(axis=0))
                        for i in index_list:
                            if i not in bar_data_2.keys():
                                bar_data_2[i] = 0
                        data.append(bar_data_2)
                    new_df = pd.DataFrame(data,index = date_range)
                    new_df.columns = [re.sub(r"(fuel|燃料)(\d) ","",i,flags=re.M|re.I) for i in new_df.columns]
                    bar_chart = Bar().add_xaxis([datetime.strftime(i,"%b %Y") for i in new_df.index])#.add_yaxis("in Operation\n运行中", new_df["in Operation\n运行中"])
                    for option_2 in new_df.columns:
                        bar_chart.add_yaxis(option_2,list(new_df[option_2]),stack="stack_1", category_gap="-10%")
                    english_name,chinese_name = selected_country.split('\n')
                    pattern = re.compile('\n[\u4e00-\u9fff]+')
                    bar_chart =(
                        bar_chart.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                        .set_global_opts(title_opts=opts.TitleOpts(title=f"Number of Stations in {english_name}\n{chinese_name}加氢站数量\nStacked Bar Plot by {re.sub(pattern,'',selected_option_3)}"),
                                        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=200,interval=10),
                                        # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                        legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                        toolbox_opts=opts.ToolboxOpts(
                    feature={
                        "saveAsImage": {},
                        "dataZoom": {},
                        "restore": {},          # Restore to original state
                        "brush": {},
                        "dataView": {}
                    }
                    )))
                    grid = Grid()
                    grid.add(
                        bar_chart,
                        grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%",pos_bottom="20%", pos_top="15%")  # Adjust the left and right padding as needed
                    )
                    st_pyecharts(grid, height=600, width=1000)
        
                    bar_chart_2 = Bar().add_xaxis([datetime.strftime(i,"%b %Y") for i in new_df.index])#.add_yaxis("in Operation\n运行中", new_df["in Operation\n运行中"])
                    for option_2 in new_df.columns:
                        bar_chart_2.add_yaxis(option_2,list((new_df[option_2]/new_df.sum(axis=1))*100),stack="stack_1", category_gap="-10%")
                    english_name,chinese_name = selected_country.split('\n')
                    pattern = re.compile('\n[\u4e00-\u9fff]+')
                    bar_chart_2 =(
                        bar_chart_2.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                        .set_global_opts(title_opts=opts.TitleOpts(title=f"Percentage of Stations in {english_name}\n{chinese_name}加氢站比例\nStacked Bar Plot by {re.sub(pattern,'',selected_option_3)}"),
                                        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=105,interval=10),
                                        # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                        legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                        toolbox_opts=opts.ToolboxOpts(
                    feature={
                        "saveAsImage": {},
                        "dataZoom": {},
                        "restore": {},          # Restore to original state
                        "brush": {},
                        "dataView": {}
                    }
                    )))
                    grid_2 = Grid()
                    grid_2.add(
                        bar_chart_2,
                        grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%", pos_bottom="20%", pos_top="15%")  # Adjust the left and right padding as needed
                    )
                    st_pyecharts(grid_2, height=600, width=1000)
        
        elif selected_option == "Fuel\n燃料":
            selected_option_2 = st.radio("Select an option\n选择一个选项", ["Show Stations in All Years\n展示所有年份的加氢站", "Show Stations by Year\n按年份展示加氢站","Show Stations by Years in Histograms\n按年份通过分布图展示加氢站"], index=0)
            if selected_option_2 == "Show Stations in All Years\n展示所有年份的加氢站":
                pie_data = [(re.sub(r"(fuel|燃料)(\d) ","",i[0],flags=re.M|re.I),i[1]) for i in list(dict(np.sum(df.iloc[:,-8:],axis=0)).items())]
                pie_chart = (
                    Pie()
                    .add("Fuel Types of Hydrogen Stations\n加氢站燃料类型", pie_data, radius=["30%", "70%"])
                    .set_global_opts(title_opts=opts.TitleOpts(title="Fuel Types of Hydrogen Stations\n加氢站燃料类型",pos_bottom="90%", pos_left="15%"),
                                    legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center",padding=[10, 0, 50, 0],border_width=0),
                                    toolbox_opts=opts.ToolboxOpts(
                feature={
                    "saveAsImage": {},
                    "dataZoom": {},
                    "restore": {},          # Restore to original state
                    "brush": {},
                    "dataView": {}
                }
            ))
                    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}:\n{c} ({d}%)"))
                )
                st_pyecharts(pie_chart, height=600)
            if selected_option_2 == "Show Stations by Year\n按年份展示加氢站":
                start_date_2 = datetime(df["StartDate\n开始日期"].min().year,df["StartDate\n开始日期"].min().month,1)
                end_date = datetime(datetime.today().date().year,datetime.today().date().month,1) - relativedelta(months=1)
                for day in generate_date_range(start_date_2, end_date):
                    df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<day)&(df["EndDate\n结束日期"]>day+relativedelta(months=1))]
                    if sum(df_partial.iloc[:,-8:].sum(axis=1)) > 1:
                        break
                start_date = day
                step = timedelta(days=30)
                date_range = [start_date + i * step for i in range(int((end_date - start_date) / step) + 1)]
                selected_month = st.select_slider("Select a month:",
                                            options=date_range,
                                            format_func=lambda date: date.strftime("%b %Y"))
                df_partial =  df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<selected_month)&(df["EndDate\n结束日期"]>selected_month+relativedelta(months=1))]
                pie_data = [(re.sub(r"(fuel|燃料)(\d) ","",i[0],flags=re.M|re.I),i[1]) for i in list(dict(np.sum(df_partial.iloc[:,-8:],axis=0)).items())]
                pie_chart = (
                    Pie()
                    .add("Fuel Types of Hydrogen Stations\n加氢站燃料类型", pie_data, radius=["30%", "70%"])
                    .set_global_opts(title_opts=opts.TitleOpts(title="Fuel Types of Hydrogen Stations\n加氢站燃料类型",pos_bottom="90%", pos_left="15%"),
                                    legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center",padding=[10, 0, 50, 0],border_width=0),
                                    toolbox_opts=opts.ToolboxOpts(
                feature={
                    "saveAsImage": {},
                    "dataZoom": {},
                    "restore": {},          # Restore to original state
                    "brush": {},
                    "dataView": {}
                }
            ))
                    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}:\n{c} ({d}%)"))
                )
                st_pyecharts(pie_chart, height=600)
            if selected_option_2 == "Show Stations by Years in Histograms\n按年份通过分布图展示加氢站":
                    start_date_2 = datetime(df["StartDate\n开始日期"].min().year,df["StartDate\n开始日期"].min().month,1)
                    end_date = datetime(datetime.today().date().year,datetime.today().date().month,1) - relativedelta(months=1)
                    for day in generate_date_range(start_date_2, end_date):
                        df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<day)&(df["EndDate\n结束日期"]>day+relativedelta(months=1))]
                        if sum(df_partial.iloc[:,-8:].sum(axis=1)) > 0:
                            break
                    start_date = day
                    step = timedelta(days=30)
                    date_range = [start_date + i * step for i in range(int((end_date - start_date) / step) + 1)]
                    index_list = list(df_partial.columns)[-8:]
                    data = []
                    for date in date_range:
                        df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<date)&(df["EndDate\n结束日期"]>date+relativedelta(months=1))]
                        bar_data_2 = dict(df_partial.iloc[:,-8:].sum(axis=0))
                        for i in index_list:
                            if i not in bar_data_2.keys():
                                bar_data_2[i] = 0
                        data.append(bar_data_2)
                    new_df = pd.DataFrame(data,index = date_range)
                    new_df.columns = [re.sub(r"(fuel|燃料)(\d) ","",i,flags=re.M|re.I) for i in new_df.columns]
                    bar_chart = Bar().add_xaxis([datetime.strftime(i,"%b %Y") for i in new_df.index])
                    for option_2 in new_df.columns:
                        bar_chart.add_yaxis(option_2,list(new_df[option_2]),stack="stack_1", category_gap="-10%")
                    pattern = re.compile('\n[\u4e00-\u9fff]+')
                    bar_chart =(
                        bar_chart.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                        .set_global_opts(title_opts=opts.TitleOpts(title=f"Number of Stations\n加氢站数量\nStacked Bar Plot by {re.sub(pattern,'',selected_option)}"),
                                        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=1300,interval=100),
                                        # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                        legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                        toolbox_opts=opts.ToolboxOpts(
                    feature={
                        "saveAsImage": {},
                        "dataZoom": {},
                        "restore": {},          # Restore to original state
                        "brush": {},
                        "dataView": {}
                    }
                    )))
                    grid = Grid()
                    grid.add(
                        bar_chart,
                        grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%",pos_bottom="20%", pos_top="15%")  # Adjust the left and right padding as needed
                    )
                    st_pyecharts(grid, height=600, width=1000)
    
                    bar_chart_2 = Bar().add_xaxis([datetime.strftime(i,"%b %Y") for i in new_df.index])#.add_yaxis("in Operation\n运行中", new_df["in Operation\n运行中"])
                    for option_2 in new_df.columns:
                        bar_chart_2.add_yaxis(option_2,list((new_df[option_2]/new_df.sum(axis=1))*100),stack="stack_1", category_gap="-10%")
                    pattern = re.compile('\n[\u4e00-\u9fff]+')
                    bar_chart_2 =(
                        bar_chart_2.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                        .set_global_opts(title_opts=opts.TitleOpts(title=f"Percentage of Stations\n加氢站比例\nStacked Bar Plot by {re.sub(pattern,'',selected_option)}"),
                                        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=105,interval=10),
                                        # datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                        legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                        toolbox_opts=opts.ToolboxOpts(
                    feature={
                        "saveAsImage": {},
                        "dataZoom": {},
                        "restore": {},          # Restore to original state
                        "brush": {},
                        "dataView": {}
                    }
                    )))
                    grid_2 = Grid()
                    grid_2.add(
                        bar_chart_2,
                        grid_opts=opts.GridOpts(pos_left="17%", pos_right="10%", pos_bottom="20%", pos_top="15%")  # Adjust the left and right padding as needed
                    )
                    st_pyecharts(grid_2, height=600, width=1000)
    
        elif selected_option == "Operator\n运营商":
            selected_option_4 = st.radio("Select a Scope:\n选择一个范围:",["Worldwide\n全世界","Regional\n某地区"],index=0)
            if selected_option_4 == "Regional\n某地区":
                selected_continent = st.selectbox("Select Continent:\n选择大洲:",sorted(remove_duplicates(df["Continent\n洲"])),index=3)
                selected_country = st.selectbox("Select Country:\n选择国家:",sorted(remove_duplicates(df[df["Continent\n洲"]==selected_continent]["Country\n国家"])))
                selected_state = st.selectbox("Select State:\n选择州/省:",remove_duplicates(df[df["Country\n国家"]==selected_country]["State\n州/省"]))
                selections = [selected_continent,selected_country,selected_state]
                selected_option_3 = st.radio("Select a Scope:\n选择一个范围:",selections,index=0)
                column_list = ["Continent\n洲","Country\n国家","State\n州/省"]
                column = column_list[selections.index(selected_option_3)]
                df = df[df[column]==selected_option_3]
            selected_option_2 = st.radio("Select an option\n选择一个选项", ["Show Stations' Operators in All Years\n展示所有年份的加氢站的运营商", 
                                                                      "Show Stations' Operators by Year\n按年份展示加氢站的运营商"], index=0)
            if selected_option_2 == "Show Stations' Operators by Year\n按年份展示加氢站的运营商":
                start_date_2 = datetime(df["StartDate\n开始日期"].min().year,df["StartDate\n开始日期"].min().month,1)
                end_date = datetime(datetime.today().date().year,datetime.today().date().month,1) - relativedelta(months=1)
                for day in generate_date_range(start_date_2, end_date):
                    df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<day)&(df["EndDate\n结束日期"]>day+relativedelta(months=1))]
                    if sum(df_partial.iloc[:,-8:].sum(axis=1)) > 0:
                        break
                start_date = day
                step = timedelta(days=30)
                date_range = [start_date + i * step for i in range(int((end_date - start_date) / step) + 1)]
                selected_month = st.select_slider("Select a month:",
                                            options=date_range,
                                            format_func=lambda date: date.strftime("%b %Y"))
                df =  df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<selected_month)&(df["EndDate\n结束日期"]>selected_month+relativedelta(months=1))]
            companies_data = sorted([(" ".join(str(i[0]).split("\n")),i[1]) for i in list(Counter(df["Operator\n运营商"]).items()) if str(i[0])!="nan" and "regional or local" not in str(i[0])],key=lambda x: x[1], reverse=True)[:40][::-1]
            df_companies_data = pd.DataFrame(companies_data)
            color_country_dict = generate_distinct_colors_dict(remove_duplicates(df_companies["Country\n国家"]))
            df_companies_data = df_companies_data.merge(df_companies[["CompanyName\n公司名称","Country\n国家"]], left_on = 0, right_on="CompanyName\n公司名称")
            df_companies_data["Color\n颜色"] = df_companies_data["Country\n国家"].apply(lambda x: color_country_dict[x])
            df_companies_data = df_companies_data.drop_duplicates()
            df_pivot = df_companies_data.pivot(index="CompanyName\n公司名称", columns="Country\n国家", values=1)
            df_pivot = df_pivot.iloc[[index for index, _ in sorted(enumerate([row.dropna().values[0] for _, row in df_pivot.iterrows()]), key=lambda x: x[1])],:]
            # color_mapping = dict(zip(df_companies_data["CompanyName\n公司名称"], df_companies_data["Color\n颜色"]))
            bar_chart = Bar().add_xaxis(list(df_pivot.index))
            for column in df_pivot.columns:
                bar_chart.add_yaxis(column,list(df_pivot[column]), stack="stack_1", category_gap="20%")
            try:
                english_name, chinese_name = selected_option_3.split("\n")
            except:
                english_name, chinese_name = ["the World","全世界"]
            bar_chart =(bar_chart.reversal_axis()
                .set_global_opts(title_opts=opts.TitleOpts(title=f"Number of Stations' Operators in Top 40 Companies in {english_name}\n{chinese_name}地区加氢站运营商数量前四十公司"),
                                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=110,interval=10),
                                yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=10)),
                                legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                toolbox_opts=opts.ToolboxOpts(
            feature={
                "saveAsImage": {},
                "dataZoom": {},
                "restore": {},          # Restore to original state
                "brush": {},
                "dataView": {}
            }
            ))
            .set_series_opts(
            label_opts=opts.LabelOpts(
            position="inside",    # Label position inside the bar
            formatter="{c}",        # Display the value as the label
        ))
            )
            grid = Grid()
            grid.add(
                bar_chart,
                grid_opts=opts.GridOpts(pos_left="40%", pos_right="10%", pos_bottom="12%", pos_top="15%")  # Adjust the left and right padding as needed
            )
            st_pyecharts(grid, height=700, width=1000)
    
        elif selected_option == "TechnologyProvider\n技术提供商":
            selected_option_4 = st.radio("Select a Scope:\n选择一个范围:",["Worldwide\n全世界","Regional\n某地区"],index=0)
            if selected_option_4 == "Regional\n某地区":
                selected_continent = st.selectbox("Select Continent:\n选择大洲:",sorted(remove_duplicates(df["Continent\n洲"])),index=3)
                selected_country = st.selectbox("Select Country:\n选择国家:",sorted(remove_duplicates(df[df["Continent\n洲"]==selected_continent]["Country\n国家"])))
                selected_state = st.selectbox("Select State:\n选择州/省:",remove_duplicates(df[df["Country\n国家"]==selected_country]["State\n州/省"]))
                selections = [selected_continent,selected_country,selected_state]
                selected_option_3 = st.radio("Select a Scope:\n选择一个范围:",selections,index=0)
                column_list = ["Continent\n洲","Country\n国家","State\n州/省"]
                column = column_list[selections.index(selected_option_3)]
                df = df[df[column]==selected_option_3]
            selected_option_2 = st.radio("Select an option\n选择一个选项", ["Show Stations' Technology Providers in All Years\n展示所有年份的加氢站的技术提供商", 
                                                                      "Show Stations' Technology Providers by Year\n按年份展示加氢站的技术提供商"], index=0)
            if selected_option_2 == "Show Stations' Technology Providers by Year\n按年份展示加氢站的技术提供商":
                start_date_2 = datetime(df["StartDate\n开始日期"].min().year,df["StartDate\n开始日期"].min().month,1)
                end_date = datetime(datetime.today().date().year,datetime.today().date().month,1) - relativedelta(months=1)
                for day in generate_date_range(start_date_2, end_date):
                    df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<day)&(df["EndDate\n结束日期"]>day+relativedelta(months=1))]
                    if sum(df_partial.iloc[:,-8:].sum(axis=1)) > 0:
                        break
                start_date = day
                step = timedelta(days=30)
                date_range = [start_date + i * step for i in range(int((end_date - start_date) / step) + 1)]
                selected_month = st.select_slider("Select a month:",
                                            options=date_range,
                                            format_func=lambda date: date.strftime("%b %Y"))
                df =  df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<selected_month)&(df["EndDate\n结束日期"]>selected_month+relativedelta(months=1))]
            companies_data = sorted([(" ".join(str(i[0]).split("\n")),i[1]) for i in list(Counter(df[[column for column in df.columns if "TechnologyProvider" in column]].values.flatten()).items()) if str(i[0])!="nan" and "regional or local" not in str(i[0])],key=lambda x: x[1], reverse=True)[:40][::-1]
            df_companies_data = pd.DataFrame(companies_data)
            color_country_dict = generate_distinct_colors_dict(remove_duplicates(df_companies["Country\n国家"]))
            df_companies_data = df_companies_data.merge(df_companies[["CompanyName\n公司名称","Country\n国家"]], left_on = 0, right_on="CompanyName\n公司名称")
            df_companies_data["Color\n颜色"] = df_companies_data["Country\n国家"].apply(lambda x: color_country_dict[x])
            df_companies_data = df_companies_data.drop_duplicates()
            df_pivot = df_companies_data.pivot(index="CompanyName\n公司名称", columns="Country\n国家", values=1)
            df_pivot = df_pivot.iloc[[index for index, _ in sorted(enumerate([row.dropna().values[0] for _, row in df_pivot.iterrows()]), key=lambda x: x[1])],:]
            # color_mapping = dict(zip(df_companies_data["CompanyName\n公司名称"], df_companies_data["Color\n颜色"]))
            bar_chart = Bar().add_xaxis(list(df_pivot.index))
            for column in df_pivot.columns:
                bar_chart.add_yaxis(column,list(df_pivot[column]), stack="stack_1", category_gap="20%")
            try:
                english_name, chinese_name = selected_option_3.split("\n")
            except:
                english_name, chinese_name = ["the World","全世界"]
            bar_chart =(bar_chart.reversal_axis()
                .set_global_opts(title_opts=opts.TitleOpts(title=f"Number of Stations' Technology Providers in Top 40 Companies in {english_name}\n{chinese_name}地区加氢站技术提供商数量前四十公司"),
                                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=200,interval=10),
                                yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=9)),
                                legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                toolbox_opts=opts.ToolboxOpts(
            feature={
                "saveAsImage": {},
                "dataZoom": {},
                "restore": {},          # Restore to original state
                "brush": {},
                "dataView": {}
            }
            ))
            .set_series_opts(
            label_opts=opts.LabelOpts(
            position="inside",    # Label position inside the bar
            formatter="{c}",        # Display the value as the label
        ))
            )
            grid = Grid()
            grid.add(
                bar_chart,
                grid_opts=opts.GridOpts(pos_left="40%", pos_right="10%", pos_bottom="12%", pos_top="15%")  # Adjust the left and right padding as needed
            )
            st_pyecharts(grid, height=700, width=1000)
    
        elif selected_option == "Partner\n合作伙伴":
            selected_option_4 = st.radio("Select a Scope:\n选择一个范围:",["Worldwide\n全世界","Regional\n某地区"],index=0)
            if selected_option_4 == "Regional\n某地区":
                selected_continent = st.selectbox("Select Continent:\n选择大洲:",sorted(remove_duplicates(df["Continent\n洲"])),index=3)
                selected_country = st.selectbox("Select Country:\n选择国家:",sorted(remove_duplicates(df[df["Continent\n洲"]==selected_continent]["Country\n国家"])))
                selected_state = st.selectbox("Select State:\n选择州/省:",remove_duplicates(df[df["Country\n国家"]==selected_country]["State\n州/省"]))
                selections = [selected_continent,selected_country,selected_state]
                selected_option_3 = st.radio("Select a Scope:\n选择一个范围:",selections,index=0)
                column_list = ["Continent\n洲","Country\n国家","State\n州/省"]
                column = column_list[selections.index(selected_option_3)]
                df = df[df[column]==selected_option_3]
            selected_option_2 = st.radio("Select an option\n选择一个选项", ["Show Stations' Partners in All Years\n展示所有年份的加氢站的合作伙伴", 
                                                                      "Show Stations' Partners by Year\n按年份展示加氢站的合作伙伴"], index=0)
            if selected_option_2 == "Show Stations' Partners by Year\n按年份展示加氢站的合作伙伴":
                start_date_2 = datetime(df["StartDate\n开始日期"].min().year,df["StartDate\n开始日期"].min().month,1)
                end_date = datetime(datetime.today().date().year,datetime.today().date().month,1) - relativedelta(months=1)
                for day in generate_date_range(start_date_2, end_date):
                    df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<day)&(df["EndDate\n结束日期"]>day+relativedelta(months=1))]
                    if sum(df_partial.iloc[:,-8:].sum(axis=1)) > 0:
                        break
                start_date = day
                step = timedelta(days=30)
                date_range = [start_date + i * step for i in range(int((end_date - start_date) / step) + 1)]
                selected_month = st.select_slider("Select a month:",
                                            options=date_range,
                                            format_func=lambda date: date.strftime("%b %Y"))
                df =  df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<selected_month)&(df["EndDate\n结束日期"]>selected_month+relativedelta(months=1))]
            companies_data = sorted([(" ".join(str(i[0]).split("\n")),i[1]) for i in list(Counter(df[[column for column in df.columns if "Partner" in column]].values.flatten()).items()) if str(i[0])!="nan" and "regional or local" not in str(i[0])],key=lambda x: x[1], reverse=True)[:40][::-1]
            df_companies_data = pd.DataFrame(companies_data)
            color_country_dict = generate_distinct_colors_dict(remove_duplicates(df_companies["Country\n国家"]))
            df_companies_data = df_companies_data.merge(df_companies[["CompanyName\n公司名称","Country\n国家"]], left_on = 0, right_on="CompanyName\n公司名称")
            df_companies_data["Color\n颜色"] = df_companies_data["Country\n国家"].apply(lambda x: color_country_dict[x])
            df_companies_data = df_companies_data.drop_duplicates()
            df_pivot = df_companies_data.pivot(index="CompanyName\n公司名称", columns="Country\n国家", values=1)
            df_pivot = df_pivot.iloc[[index for index, _ in sorted(enumerate([row.dropna().values[0] for _, row in df_pivot.iterrows()]), key=lambda x: x[1])],:]
            # color_mapping = dict(zip(df_companies_data["CompanyName\n公司名称"], df_companies_data["Color\n颜色"]))
            bar_chart = Bar().add_xaxis(list(df_pivot.index))
            for column in df_pivot.columns:
                bar_chart.add_yaxis(column,list(df_pivot[column]), stack="stack_1", category_gap="20%")
            try:
                english_name, chinese_name = selected_option_3.split("\n")
            except:
                english_name, chinese_name = ["the World","全世界"]
            bar_chart =(bar_chart.reversal_axis()
                .set_global_opts(title_opts=opts.TitleOpts(title=f"Number of Stations' Partners in Top 40 Companies in {english_name}\n{chinese_name}地区加氢站合作伙伴数量前四十公司"),
                                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=200,interval=10),
                                yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=9)),
                                legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center", padding=[0, 0, 0, 0], border_width=0),
                                toolbox_opts=opts.ToolboxOpts(
            feature={
                "saveAsImage": {},
                "dataZoom": {},
                "restore": {},          # Restore to original state
                "brush": {},
                "dataView": {}
            }
            ))
            .set_series_opts(
            label_opts=opts.LabelOpts(
            position="inside",    # Label position inside the bar
            formatter="{c}",        # Display the value as the label
        ))
            )
            grid = Grid()
            grid.add(
                bar_chart,
                grid_opts=opts.GridOpts(pos_left="40%", pos_right="10%", pos_bottom="12%", pos_top="15%")  # Adjust the left and right padding as needed
            )
            st_pyecharts(grid, height=700, width=1000)
    
    if selected_option_4 == "Show in Maps\n以地图展示":
        selected_option = st.radio("Select an option:\n选择一个选项:",["Show All Stations\n展示所有加氢站","Show Stations by Years and Filtering\n按年份和筛选展示加氢站"],index=1)
        selected_option_2 = st.selectbox("Color by:\n上色:",["Status\n状态", "PublicAccess\n公共访问", "Fuel\n燃料"])
        if selected_option == "Show All Stations\n展示所有加氢站":
            marker_data = []
            color_list = ['#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255)) for r, g, b in generate_distinct_colors(len(remove_duplicates(df[selected_option_2])))]
            st.markdown(
                "".join([f'<div style="background-color: {color_list[i]}; width: 15px; height: 10px;"></div><div>{sorted(remove_duplicates(df[selected_option_2]))[i]}</div>' for i in range(len(color_list))]),
                unsafe_allow_html=True
            )
            if selected_option_2 != "Fuel\n燃料":
                m = folium.Map(location = [0, 0], zoom_start = 2, tiles = "CartoDB Positron")
                for j in range(len(df)):
                    j_row = df.iloc[j]
                    popup_str = ""
                    for column in ["StationName\n站名","Street1\n街道1","Street2\n街道 2","City\n城市","State\n州/省","Country\n国家","Operator\n运营商",
                                   "TechnologyProvider1\n技术提供者1","TechnologyProvider2\n技术提供者2","TechnologyProvider3\n技术提供者3","TechnologyProvider4\n技术提供者4",
                                   "Partner1\n合作伙伴1","Partner2\n合作伙伴2","Partner3\n合作伙伴3","Partner4\n合作伙伴4"]:
                        try:
                            if j_row[column] != "" and str(j_row[column]) != "nan":
                                popup_str += "<p>"+column+": "+str(j_row[column])+"</p>"
                        except:
                            pass
                    popup_str += "<p>"+selected_option_2+": "+str(j_row[selected_option_2])+"</p>"
                    popup = folium.Popup(popup_str, max_width=300)
                    folium.CircleMarker(location = [j_row["Latitude\n纬度"],j_row["Longitude\n经度"]],
                                        radius=5,
                                        color='none',
                                        fill=True,
                                        fill_color=color_list[sorted(remove_duplicates(df[selected_option_2])).index(df.iloc[j][selected_option_2])],
                                        fill_opacity=0.7,
                                        popup=popup).add_to(m)
                st_map = st_folium(m, width=900, height=600)
            else:
                pass
        if selected_option == "Show Stations by Years and Filtering\n按年份和筛选展示加氢站":
            selected_continent = st.selectbox("Select Continent:\n选择大洲:",sorted(remove_duplicates(df["Continent\n洲"])),index=3)
            selected_country = st.selectbox("Select Country:\n选择国家:",sorted(remove_duplicates(df[df["Continent\n洲"]==selected_continent]["Country\n国家"])))
            selected_state = st.selectbox("Select State:\n选择州/省:",remove_duplicates(df[df["Country\n国家"]==selected_country]["State\n州/省"]))
            selected_city = st.selectbox("Select City:\n选择城市:",remove_duplicates(df[df["State\n州/省"]==selected_state]["City\n城市"]))
            selections = [selected_continent,selected_country,selected_state,selected_city]
            selected_option_3 = st.radio("Select a Scope:\n选择一个范围:",selections,index=1)
            column_list = ["Continent\n洲","Country\n国家","State\n州/省","City\n城市"]
            column = column_list[selections.index(selected_option_3)]
            df = df[df[column]==selected_option_3]
            selected_option_5 = st.radio("Select a Year",["Show All Stations","Show Stations by Years"],index=0)
            if selected_option_5 == "Show Stations by Years":
                start_date_2 = datetime(df["StartDate\n开始日期"].min().year,df["StartDate\n开始日期"].min().month,1)
                end_date = datetime(datetime.today().date().year,datetime.today().date().month,1) - relativedelta(months=1)
                for day in generate_date_range(start_date_2, end_date):
                    df_partial = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<day)&(df["EndDate\n结束日期"]>day+relativedelta(months=1))]
                    if len(df_partial) > 0:
                        break
                start_date = day
                step = timedelta(days=30)
                date_range = [start_date + i * step for i in range(int((end_date - start_date) / step) + 1)]
                selected_month = st.select_slider("Select a month:",
                                            options=date_range,
                                            format_func=lambda date: date.strftime("%b %Y"))
                df = df[df["StartDate\n开始日期"]!=None][(df["StartDate\n开始日期"]<selected_month)&(df["EndDate\n结束日期"]>selected_month+relativedelta(months=1))]
    
            if selected_option_2 != "Fuel\n燃料":
                marker_data = []
                color_list = ['#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255)) for r, g, b in generate_distinct_colors(len(remove_duplicates(df[selected_option_2])))]
                st.markdown(
                    "".join([f'<div style="background-color: {color_list[i]}; width: 15px; height: 10px;"></div><div>{sorted(remove_duplicates(df[selected_option_2]))[i]}</div>' for i in range(len(color_list))]),
                    unsafe_allow_html=True
                )
                m = folium.Map(location = df[["Latitude\n纬度","Longitude\n经度"]].median(), zoom_start = 5, tiles = "CartoDB Positron")
                for j in range(len(df)):
                    j_row = df.iloc[j]
                    popup_str = ""
                    for column in ["StationName\n站名","Street1\n街道1","Street2\n街道 2","City\n城市","State\n州/省","Country\n国家","Operator\n运营商",
                                   "TechnologyProvider1\n技术提供者1","TechnologyProvider2\n技术提供者2","TechnologyProvider3\n技术提供者3","TechnologyProvider4\n技术提供者4",
                                   "Partner1\n合作伙伴1","Partner2\n合作伙伴2","Partner3\n合作伙伴3","Partner4\n合作伙伴4"]:
                        try:
                            if j_row[column] != "" and str(j_row[column]) != "nan":
                                popup_str += "<p>"+column+": "+str(j_row[column])+"</p>"
                        except:
                            pass
                    popup_str += "<p>"+selected_option_2+": "+str(j_row[selected_option_2])+"</p>"
                    popup = folium.Popup(popup_str, max_width=300)
                    folium.CircleMarker(location = [j_row["Latitude\n纬度"],j_row["Longitude\n经度"]],
                                        radius=5,
                                        color='none',
                                        fill=True,
                                        fill_color=color_list[sorted(remove_duplicates(df[selected_option_2])).index(df.iloc[j][selected_option_2])],
                                        fill_opacity=0.7,
                                        popup=popup).add_to(m)
                st_map = st_folium(m, width=900, height=600)
            else:
                selected_option_6 = st.radio("Select an Option:",["Show All Stations","Show Stations of One Fuel","Show Stations of More Than One Fuels"],index=0)
                if selected_option_6 == "Show Stations of One Fuel":
                    df = df[df.iloc[:,-8:].sum(axis=1)==1]
                if selected_option_6 == "Show Stations of More Than One Fuels":
                    df = df[df.iloc[:,-8:].sum(axis=1)>1]
                color_list = ['#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255)) for r, g, b in generate_distinct_colors(len(df.columns[-8:]))]
                st.markdown(
                    "".join([f'<div style="background-color: {color_list[i]}; width: 15px; height: 10px;"></div><div>{df.columns[-8:][i]}</div>' for i in range(len(color_list))]),
                    unsafe_allow_html=True
                )
                m = folium.Map(location = df[["Latitude\n纬度","Longitude\n经度"]].median(), zoom_start = 5, tiles = "CartoDB Positron")
                m_2 = folium.Map(location = df[["Latitude\n纬度","Longitude\n经度"]].median(), zoom_start = 5, tiles = "CartoDB Positron")
                for j in range(len(df)):
                    j_row = df.iloc[j]
                    popup_str = ""
                    for column in ["StationName\n站名","Street1\n街道1","Street2\n街道 2","City\n城市","State\n州/省","Country\n国家","Operator\n运营商",
                                   "TechnologyProvider1\n技术提供者1","TechnologyProvider2\n技术提供者2","TechnologyProvider3\n技术提供者3","TechnologyProvider4\n技术提供者4",
                                   "Partner1\n合作伙伴1","Partner2\n合作伙伴2","Partner3\n合作伙伴3","Partner4\n合作伙伴4"]:
                        try:
                            if j_row[column] != "" and str(j_row[column]) != "nan":
                                popup_str += "<p>"+column+": "+str(j_row[column])+"</p>"
                        except:
                            pass
                    popup_str += "<p>"+"Fuel\n燃料: "
                    for column in list(df.columns)[-8:]:
                        if str(j_row[column]) != "nan":
                            if str(j_row[column]) != "nan":
                                if j_row[column] == 1:
                                    popup_str += re.sub("Fuel(\d) |燃料(\d) ","",column)+", "
                    popup_str += "</p>"
                    popup = folium.Popup(popup_str, max_width=300)
                    step = 1e-3
                    n = 0
                    for k, column in enumerate(list(df.columns)[-8:]):
                        if j_row[column] == 1:
                            location = [j_row["Latitude\n纬度"],j_row["Longitude\n经度"]+n*step]
                            folium.CircleMarker(location = location,
                                                radius=5,
                                                color='none',
                                                fill=True,
                                                fill_color=color_list[k],
                                                fill_opacity=0.7,
                                                popup=folium.Popup(popup_str+"\n"+str(n+1), max_width=300)).add_to(m)
                            n += 1
                st_map = st_folium(m, width=900, height=600)
    if selected_option_4 == "Show Raw Data\n展示原始数据":
        st.subheader("Hydrogen Stations 加氢站")
        st.write(df)
        st.subheader("Hydrogen Operators/Technology Providers/Partners Companies 氢气运营商/技术提供商/合作伙伴公司")
        st.write(df_companies)
if selected_topic == "Hydrogen Safety Incidents\n氢气安全事故":
    st.header("Hydrogen Safety Incidents 氢气安全事故")
    df = pd.read_csv("hydrogen data chinese english.csv",index_col=[0])
    df["Incident Date\n事件日期"] = df["Incident Date\n事件日期"].apply(lambda x: datetime.strptime(x.split("\n")[0], '%d-%b-%Y'))
    selected_option_6 = st.radio("",["See Visualization\n展示可视化","Show Raw Data\n展示原始数据"])
    if selected_option_6 == "See Visualization\n展示可视化":
        selected_option_5 = st.radio("Select a Year",["Show All Stations","Show Stations by Years"],index=0)
        if selected_option_5 == "Show Stations by Years":
            min_year, max_year = st.slider("Select a Range", df["Incident Date\n事件日期"].min().year, datetime.now().year, (df["Incident Date\n事件日期"].min().year, datetime.now().year))
            df = df[df["Incident Date\n事件日期"]!=None][(df["Incident Date\n事件日期"]>datetime(min_year,1,1))&(df["Incident Date\n事件日期"]<datetime(max_year,12,31))]
        columns_to_select = list(df.columns)[2:13]+[list(df.columns)[-1]]
        selected_column = st.selectbox("Choose a feature to visualize:\n选择一个特征进行可视化:",columns_to_select)
        if selected_column in ["Severity\n严重性","Leak\n泄漏","Ignition\n点火","Characteristics\n特点","When Incident Discovered\n事故发现时间"]:
            pie_data = sorted(list(Counter(df[selected_column].str.split(", ").explode()).items()),key=lambda x: x[1], reverse=True)[::-1]
            pie_chart = (
                Pie()
                .add("", pie_data, radius=["30%", "70%"])
                .set_global_opts(title_opts=opts.TitleOpts(title=f"{selected_column}\nOut of all stations in the record",
                                                        pos_bottom="85%", pos_left="8%",
                                                        ),
                                                        graphic_opts=[
                opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(
                        bounding="raw",
                        right="5%",
                        top="10%",  # Adjust this value to add more space to the top
                        z=100,
                    )
                )
        ],toolbox_opts=opts.ToolboxOpts(
        feature={
            "saveAsImage": {},
            "dataZoom": {},
            "restore": {},          # Restore to original state
            "brush": {},
            "dataView": {}
        }
        ),
                            legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center",padding=[10, 0, 50, 0],border_width=0),
                            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}:\n{c} ({d}%)"))
        )
            st_pyecharts(pie_chart, height=600)
          
        elif selected_column != "Incident Date\n事件日期":
            bar_data = sorted([(" ".join(i[0].split("\n")),i[1]) for i in list(Counter(df[selected_column].str.split(", ").explode()).items())],key=lambda x: x[1], reverse=True)[:40][::-1]
            english_name, chinese_name = selected_column.split("\n")
            bar_chart = (
                Bar()
                .add_xaxis([i[0] for i in bar_data])
                .add_yaxis("Number of Stations\n加氢站数量", [i[1] for i in bar_data])
                .reversal_axis()
                .set_global_opts(title_opts=opts.TitleOpts(title=f"Top 40 {english_name}\n前四十{chinese_name}"),
                                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12),min_=0, max_=200,interval=50),
                                legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%", pos_left="center",padding=[0, 0, 0, 0],border_width=0),
                                toolbox_opts=opts.ToolboxOpts(
            feature={
                "saveAsImage": {},
                "dataZoom": {},
                "restore": {},          # Restore to original state
                "brush": {},
                "dataView": {}
            }
        ))
        )
            grid = Grid()
    
            # Add padding to the left side of the chart
            grid.add(
                bar_chart,
                grid_opts=opts.GridOpts(pos_left="30%", pos_right="10%", pos_bottom="5%", pos_top="15%")  # Adjust the left and right padding as needed
            )
            st_pyecharts(grid, height=800, width=1000)
    
        elif selected_column == "Incident Date\n事件日期":
            pass  
    if selected_option_6 == "Show Raw Data\n展示原始数据":
      st.write(df)
          
          
