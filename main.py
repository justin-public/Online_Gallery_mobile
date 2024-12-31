import streamlit as st
import sqlite3
import re
from socket import *
from urllib.parse import parse_qs, urlparse
from datetime import datetime

css = """
<style>
    /* Base styles */
    .container {
        display: flex;
        align-items: center; /* Align items vertically in the center */
        width: 100%;
        padding: 10px;
    }
    .name-label {
        margin-right: 10px; /* Space between label and input */
    }
    .name-input {
        flex: 1; /* Make the input take the remaining space */
        max-width: 400px; /* Set a max-width for the input field */
    }
    /* Responsive styles */
    @media (max-width: 600px) {
        .container {
            flex-direction: column; /* Stack vertically on small screens */
            align-items: flex-start;
        }
        .name-label {
            margin-right: 0;
            margin-bottom: 5px; /* Space below the label */
        }
        .name-input {
            width: 100%; /* Make the input field full width */
        }
    }
</style>
"""


"""
def _comment_info_init_write(commentindexcnt):
    with open("CommentIndex.txt", "w") as file:
        file.write(commentindexcnt)
    
def _comment_info_init_Read():
    f = open("CommentIndex.txt", "r")
    Comment_line = f.readline()
    f.close()
    return Comment_line
"""

def generate_comment_id(contents_id: str):
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()
    # 현재 최대 comment_id를 조회
    cursor.execute('''
        SELECT comment_id FROM comments
        WHERE contents_id = ?
        ORDER BY comment_id DESC
        LIMIT 1
    ''', (contents_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        last_id = result[0]
        match = re.match(r'(.+_M)(\d{3})$', last_id)
        if match:
            prefix, num_str = match.groups()
            num = int(num_str)
            num = (num + 1) % 1000  # 999에서 000으로 초기화
            return f"{prefix}{num:03d}"
    # 초기 상태일 때
    return f"{contents_id}_M000"



def initialize_db():
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contents_id TEXT NOT NULL,
            comment_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            author TEXT NOT NULL,
            comment TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_comment(contents_id: str, author: str, comment: str):
    comment_id = generate_comment_id(contents_id)
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()

    # 현재 UTC 시간을 "년-월-일 시:분:초" 형식으로 포맷팅
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO comments (contents_id, comment_id, timestamp, author, comment)
        VALUES (?, ?, ?, ?, ?)
    ''', (contents_id, comment_id, timestamp, author, comment))
    conn.commit()
    conn.close()

def get_latest_comment(contents_id: str):
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM comments
        WHERE contents_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
    ''', (contents_id,))
    result = cursor.fetchone()
    conn.close()
    return result


HOST = '121.140.54.39'
PORT = 6060
BUFSIZE = 1024
ADDR = (HOST, PORT)
def main():
    #global counter
    #st.title("QR 코드 정보 표시")
    st.markdown(css, unsafe_allow_html=True)
    # URL 파라미터 가져오기
    query_params = st.experimental_get_query_params()
   
    initialize_db()
    
    if 'id' in query_params:
        id_number = query_params['id'][0]
        #st.write(f"현재 컨텐츠 의 ID 번호는 {id_number}입니다.")
        st.write(f"ID 번호: {id_number}")
        st.markdown('<div class="container">', unsafe_allow_html=True)
        st.markdown('<div class="name-label">작성자</div>', unsafe_allow_html=True)
       
        name_input = st.text_input('', placeholder='Enter name', key='name_input', help=None)
        user_input = st.text_area("", key="text_area")
        char_count = len(user_input)
        st.write(f"50/{char_count}")
        #now = datetime.now()
        #current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        #combine_packet = f"{id_number},{current_datetime},{name_input},{user_input}"
        Send_Packet_logic = st.button("Send")
        
        if Send_Packet_logic:
            add_comment(id_number,name_input,user_input)
            latest_comment = get_latest_comment(id_number)
            combine_packet = f"{latest_comment[1]},{latest_comment[2]},{latest_comment[3]},{latest_comment[4]},{latest_comment[5]}"
            print(combine_packet)
            if char_count > 50:
                st.warning("입력한 글자가 50자를 초과했습니다. 50자 이하로 입력해주세요.")
            else:
                clientSocket = socket(AF_INET, SOCK_STREAM)
                try:
                    clientSocket.connect(ADDR)
                    request = str(combine_packet)
                    clientSocket.send(request.encode('utf-8'))
                    st.write(combine_packet)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                finally:
                    clientSocket.close()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.write("ID 번호가 URL에 없습니다.")

if __name__ == "__main__":
    main()