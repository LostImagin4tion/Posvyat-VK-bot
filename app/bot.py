import vk_api
import psycopg2
from sqlalchemy.testing import db

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


from vk_tools import Keyboard
from vk_events import send_message
from vk_config import token_vk
from create_db import engine, get_session, guests, orgs, groups, info, tech_support, sendings
from sqlalchemy.orm import Session, sessionmaker

session = Session(bind=engine)

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


            if text == "start":


                if is_admin(user_id, event):
                    send_message(vk_session, user_id, "Hi, admin!")
                else:
                    send_message(vk_session, user_id, "Hi, user!")

                    result = vk_session.method("groups.isMember", {"group_id": group_id[0]["id"], 'user_id': user_id})

                    new_guest = guests(
                        vk_link=str(user_id),
                    )
                    session.add(new_guest)

                    session.commit()

                    if result:
                        send_message(vk_session, user_id, "Спасибо, что вступили в наше сообщество!")

                        user_setting = session.query(guests).filter_by(vk_link=str(user_id)).first()

                        if user_setting:
                            user_setting.first_group = True
                            user_setting.second_group = True
                        else:
                            user_setting = guests(vk_link=user_id, first_group=True, percent=True)
                            session.add(user_setting)
                        session.commit()

                    else:
                        send_message(vk_session, user_id, "Вы не вступили в сообщество.")
                        user_setting = session.query(guests).filter_by(vk_link=str(user_id)).first()

                        if user_setting:
                            user_setting.first_group = True
                            user_setting.second_group = False
                        else:
                            user_setting = guests(vk_link=str(user_id), first_group=True, second_group=False)
                            session.add(user_setting)
                        session.commit()




