import streamlit as st

st.set_page_config(page_title='HADAOJI PRINT')

st.title('HADAOJI PRINT 見積アプリ')

qty = st.number_input('枚数', min_value=1, value=10)
body = st.number_input('ボディ単価', min_value=0, value=660)
print_price = st.number_input('プリント単価', min_value=0, value=300)
plates = st.number_input('版数', min_value=0, value=2)

subtotal = qty * body + qty * print_price + plates * 8000
st.metric('小計', f'{subtotal:,}円')
st.metric('税込', f'{int(subtotal*1.1):,}円')

st.success('Ver1 初期版')