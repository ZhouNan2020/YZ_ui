# import streamlit和其它的处理word的库
import streamlit as st


# 定义一个包含了@cache的testforcache类, 在这个类中的第二个方法使用st的数字输入框获取2个数字并与init的数字相加，测试cache的效果
class testforcache:
    def __init__(self):
        self.a = 1
        self.b = 2

    @st.cache
    def test2(self):
        c = st.number_input('a', value=self.a)
        d = st.number_input('b', value=self.b)
        return self.a + self.b

# 实例化
test = testforcache()
# 调用test2方法
test.test2()
