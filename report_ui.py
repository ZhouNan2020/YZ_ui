# import streamlit和其它的处理word的库
import streamlit as st


# 定义一个包含了@cache的testforcache类, 在这个类中的第二个方法使用st的数字输入框获取2个数字并与init的数字相加，
# 将 st.number _ input ()或 st.write ()调用移到 test2()之外
# 测试cache的效果
class testforcache:
    def __init__(self):
        self.number = 0

    @st.cache
    def test1(self):
        st.write("test1")
        self.number = st.number_input("test1", value=0)

    def test2(self):
        st.write("test2")
        self.number = self.number + st.number_input("test2", value=0)


# 实例化testforcache类
test = testforcache()
# 调用test1()方法
test.test1()


