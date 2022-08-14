import vk_api
import psycopg2

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


from vk_tools import Keyboard
from vk_events import send_message
from vk_config import token_vk
from create_db import engine, get_session, guests, orgs, groups, info, tech_support, sendings
from sqlalchemy.orm import Session, sessionmaker

session = sessionmaker(bind=engine)

vk_session = vk_api.VkApi(token=token_vk)

def id_group(event_p):
    group_id = vk_session.method("groups.getById", {"peer_id": event_p.peer_id})

    return group_id


def is_admin(id_p, event_p):

    group_id = id_group(event_p)
    group_inf = vk_session.method("groups.getMembers", {"group_id": group_id[0]["id"], "filter": "managers"})

    for member in group_inf["items"]:

        if member["id"] == id_p:

            if member["role"] == "administrator" or "creator":
                return True
            else:
                return False


def start():

    for event in VkLongPoll(vk_session).listen():

        group_id = id_group(event)

        if event.type == VkEventType.MESSAGE_NEW and event.to_me:

            user_id = event.user_id
            text = event.text.lower()

            user = vk_session.method("users.get", {"user_ids": user_id})
            first_name = user[0]['first_name']
            last_name = user[0]['last_name']


            if text == "start":


                if is_admin(user_id, event):
                    send_message(vk_session, user_id, "Hi, admin!")
                else:
                    send_message(vk_session, user_id, "Hi, user!")
                    #тут должно выделяться новое поле в бд для гостей

                result = vk_session.method("groups.isMember", {"group_id": group_id[0]["id"], 'user_id': user_id})

                if result:
                    send_message(vk_session, user_id, "Спасибо, что вступили в наше сообщество!")
                    #в колонке с вступили надо отметить тру
                    i = vk_session.query(guests).get(8)
                    i.first_group = True
                    session.add(i)
                    session.commit()
                else:
                    send_message(vk_session, user_id, "Вы не вступили в сообщество.")
                    #в колонке с вступили надо отметить фолс
                    i = vk_session.query(guests).get(8)
                    i.second_group = False
                    session.add(i)
                    session.commit()



