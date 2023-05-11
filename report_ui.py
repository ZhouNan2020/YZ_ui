# import streamlit和其它的处理word的库
import streamlit as st


# 定义一个包含了@cache的testforcache类, 在这个类中的第二个方法使用st的数字输入框获取2个数字并与init的数字相加，测试cache的效果
# 将 st.number _ input ()或 st.write ()调用移到 test2()之外
# 重新运行脚本并调整数字输入框的值，以查看缓存的效果

class testforcache:
    def __init__(self):
        self.number1 = st.number_input('Input a number', value=1)
        self.number2 = st.number_input('Input a number', value=1)

    @st.cache
    def test1(self):
        return self.number1 + self.number2

    def test2(self):
        return self.number1 + self.number2

# 实例化testforcache类
test = testforcache()
# 调用test1方法
st.write(test.test1())
# 调用test2方法
st.write(test.test2())
