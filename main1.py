import streamlit as st
import qrcode
from PIL import Image
import io

def generate_qr_code(url, id_number):
    # URL과 ID를 결합하여 QR 코드 데이터 생성
    data = f"{url}?id={id_number}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
   
    # QR 코드를 이미지로 변환
    img = qr.make_image(fill='black', back_color='white')
   
    # 이미지 메모리 버퍼에 저장
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

def main():
    st.title("QR 코드 생성기")
    url = st.text_input("URL 입력:")
    id_number = st.text_input("ID 번호 입력:")
    if st.button("QR 코드 생성"):
        if url and id_number:
            qr_code_image = generate_qr_code(url, id_number)
            st.image(qr_code_image, caption='QR 코드', use_column_width=True)
            st.success("QR 코드가 생성되었습니다!")
        else:
            st.error("URL과 ID 번호를 모두 입력해주세요.")
if __name__ == "__main__":
    main()