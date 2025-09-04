# 1. 公式のPythonイメージをベースとして使用します (軽量なslim版がおすすめです)
FROM python:3.10-slim

# 2. コンテナの中での作業場所（ディレクトリ）を指定します
WORKDIR /usr/src/app

# 3. 必要なライブラリが書かれたファイルを先にコピーします
COPY requirements.txt ./

# 4. requirements.txtを基に、コンテナ内にライブラリをインストールします
#    (コードをコピーする前に実行することで、ビルド時間を短縮できます)
RUN pip install --no-cache-dir -r requirements.txt

# 5. アプリケーションのコード（appフォルダの中身）をコンテナにコピーします
COPY ./app ./app

# 6. コンテナが起動したときに実行するコマンドを指定します
CMD ["python", "app/main.py"]