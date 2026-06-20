import io
from datetime import date
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

st.set_page_config(page_title="HADAOJI PRINT 見積", page_icon="🧾", layout="wide")

BODY_MASTER = {
    "00085-CVT": {"name":"5.6oz Tシャツ", "variants":{"WM〜XL":{"sell":660,"cost":440},"XXL〜XXXL":{"sell":840,"cost":560},"4XL〜5XL":{"sell":960,"cost":640}}},
    "00300-ACT": {"name":"ドライTシャツ", "variants":{"WM〜LL":{"sell":516,"cost":344},"3L〜5L":{"sell":594,"cost":396},"6L〜7L":{"sell":810,"cost":540}}},
    "5001-01": {"name":"United Athle Tシャツ", "variants":{"S〜XL ホワイト":{"sell":756,"cost":504},"S〜XL カラー":{"sell":816,"cost":544},"XXL カラー":{"sell":1020,"cost":680}}},
    "5011-01": {"name":"ロンT", "variants":{"S〜XL ホワイト":{"sell":1188,"cost":792},"S〜XL カラー":{"sell":1320,"cost":880},"XXL カラー":{"sell":1560,"cost":1040}}},
    "持ち込み": {"name":"持ち込みウェア", "variants":{"持ち込み":{"sell":0,"cost":0}}},
}

def yen(v): return f"{int(round(v)):,}円"

def print_unit(qty, special):
    sell,cost = (800,500) if qty <= 9 else ((200,100) if qty >= 100 else (300,150))
    return (sell + (150 if special else 0), cost + (100 if special else 0))

def make_pdf(doc_type, no, customer, subject, rows, subtotal, tax, total, note):
    buf=io.BytesIO(); pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=14*mm,leftMargin=14*mm,topMargin=14*mm,bottomMargin=14*mm)
    p=ParagraphStyle("p",fontName="HeiseiKakuGo-W5",fontSize=9,leading=13)
    t=ParagraphStyle("t",fontName="HeiseiKakuGo-W5",fontSize=22,leading=28,alignment=1)
    label="御見積金額（税込）" if doc_type=="見積書" else "御請求金額（税込）"
    story=[Paragraph(doc_type,t),Spacer(1,8),Paragraph(f"<b>{customer}</b><br/>件名：{subject}<br/>番号：{no}<br/>発行日：{date.today().strftime('%Y/%m/%d')}",p),Spacer(1,8)]
    amount=Table([[label, yen(total)]], colWidths=[70*mm,100*mm])
    amount.setStyle(TableStyle([("BOX",(0,0),(-1,-1),2,colors.black),("BACKGROUND",(0,0),(-1,-1),colors.whitesmoke),("ALIGN",(1,0),(1,0),"RIGHT"),("FONTSIZE",(1,0),(1,0),20),("FONTNAME",(0,0),(-1,-1),"HeiseiKakuGo-W5"),("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10)]))
    story += [amount,Spacer(1,10)]
    data=[["品目","内容","数量","単価","金額"]]+[[r['item'],r['desc'],r['qty'],yen(r['unit']),yen(r['amount'])] for r in rows]+[["","","","小計",yen(subtotal)],["","","","消費税",yen(tax)],["","","","合計",yen(total)]]
    table=Table(data,colWidths=[35*mm,70*mm,22*mm,28*mm,28*mm])
    table.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),"HeiseiKakuGo-W5"),("GRID",(0,0),(-1,-1),0.5,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("ALIGN",(2,1),(-1,-1),"RIGHT")]))
    story += [table,Spacer(1,10),Paragraph("<b>備考</b><br/>"+note.replace("\n","<br/>"),p),Spacer(1,8),Paragraph("株式会社ハダオジ / HADAOJI PRINT",p)]
    doc.build(story); buf.seek(0); return buf

st.title("HADAOJI PRINT 見積・請求アプリ v3")
st.caption("入力中にプレビュー確認できます")
left,right=st.columns([1,1.1])
with left:
    doc_type=st.selectbox("書類種類",["見積書","請求書"])
    no=st.text_input("番号",f"HP-{date.today().strftime('%Y%m%d')}-001")
    customer=st.text_input("宛名","〇〇 様")
    subject=st.text_input("件名","オリジナルウェア制作")
    code=st.selectbox("品番",list(BODY_MASTER.keys()))
    var=st.selectbox("区分",list(BODY_MASTER[code]["variants"].keys()))
    qty=st.number_input("枚数",1,999,10)
    base=BODY_MASTER[code]["variants"][var]
    manual=st.checkbox("単価を手入力")
    body_sell=st.number_input("ボディ販売単価",0,99999,base["sell"],disabled=not manual)
    body_cost=st.number_input("ボディ原価",0,99999,base["cost"],disabled=not manual)
    spots=st.number_input("プリント箇所数",0,10,1)
    plates=st.number_input("製版数",0,10,1)
    special=st.checkbox("特色プリント（販売+150 / 原価+100）")
    note=st.text_area("備考","納期：約2週間\n内容確定後の制作開始となります。")

ps,pc=print_unit(qty,special)
body_total=body_sell*qty; print_total=ps*qty*spots; plate_total=8000*plates
subtotal=body_total+print_total+plate_total; tax=subtotal*0.1; total=subtotal+tax
cost=body_cost*qty+pc*qty*spots+5500*plates; profit=subtotal-cost
rows=[{"item":"ボディ","desc":f"{code} {BODY_MASTER[code]['name']} / {var}","qty":f"{qty}枚","unit":body_sell,"amount":body_total}]
if spots: rows.append({"item":"プリント代","desc":f"{spots}箇所"+(" / 特色" if special else ""),"qty":f"{qty}枚","unit":ps*spots,"amount":print_total})
if plates: rows.append({"item":"製版代","desc":"シルクスクリーン製版","qty":f"{plates}版","unit":8000,"amount":plate_total})

with right:
    st.subheader("プレビュー")
    st.markdown(f"""
    ### {doc_type}
    **{customer}**  
    件名：{subject}  
    番号：{no}  
    発行日：{date.today().strftime('%Y/%m/%d')}

    ## {'御見積金額（税込）' if doc_type=='見積書' else '御請求金額（税込）'}  
    # {yen(total)}
    """)
    st.table([{ "品目":r["item"], "内容":r["desc"], "数量":r["qty"], "単価":yen(r["unit"]), "金額":yen(r["amount"]) } for r in rows])
    st.write(f"小計：{yen(subtotal)} / 消費税：{yen(tax)} / 合計：{yen(total)}")
    st.info(note)
    st.success(f"管理用：原価 {yen(cost)} / 利益 {yen(profit)}")
    pdf=make_pdf(doc_type,no,customer,subject,rows,subtotal,tax,total,note)
    st.download_button("正式PDFをダウンロード",data=pdf,file_name=f"{no}_{doc_type}.pdf",mime="application/pdf",type="primary")
