FROM python:3.10-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 変更点: コピー先を './' に変更
COPY ./app ./

# 変更点: CMDは不要になるので削除します（docker-composeでcommandを指定するため）