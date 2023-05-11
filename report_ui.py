# import streamlit和其它的处理word的库
import streamlit as st


# 定义一个包含了@cache的testforcache类, 在这个类中的第二个方法使用st的数字属于框获取数字并相加，测试cache的效果
class testforcache:
    def __init__(self):
        pass

    @st.cache
    def test1(self):
        return 1

    def test2(self):
        a = st.number_input('input a number')
        return a + self.test1()

