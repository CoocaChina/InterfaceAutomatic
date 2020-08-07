from dingtalkchatbot.chatbot import DingtalkChatbot, ActionCard

# WebHook地址
webhook = 'https://oapi.dingtalk.com/robot/send?access_token=63f7487985764ea0639866741ac34979e5947afacc4b507079c7f108a3782ea7'
# 初始化机器人小丁
xiaoding = DingtalkChatbot(webhook)
# Text消息@所有人

if __name__ == '__main__':
    # ActionCard独立跳转消息类型（双选项）
    btns2 = [{"title": "支持", "actionURL": "https://www.dingtalk.com/"},
             {"title": "反对", "actionURL": "http://www.back china.com/news/2018/01/11/537468.html"}]
    actioncard2 = ActionCard(title='万万没想到，竟然...',
                             text='![选择](http://www.songshan.es/wp-content/uploads/2016/01/Yin-Yang.png) \n### 故事是这样子的...',
                             btns=btns2,
                             btn_orientation=1,
                             hide_avatar=1)
    xiaoding.send_action_card(actioncard2)