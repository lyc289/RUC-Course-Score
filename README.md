# RUC成绩出分推送
实时监控成绩系统，配合pushplus将更新实时推送至微信/邮箱等渠道

### 部署
```
git clone https://github.com/lyc289/RUC-Course-Score.git
cd RUC-Course-Score
pip install -r requirements.txt
```
将`config-example.ini`复制为`config.ini`，并填写其中的配置项
- username: 微人大账号
- password: 微人大密码
- browser: 推荐Chrome
- driver: 浏览器地址



### 运行



完成配置后，在终端运行
`python main.py`
推荐的做法是挂到后台:
```
# 使用tmux
tmux new -s score
tmux a -t score
python main.py
```

### 致谢
感谢pjd学长开发的 ruclogin