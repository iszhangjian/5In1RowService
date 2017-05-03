#-*- encoding: UTF-8 -*-

from base_service import BaseService
import logging, json, copy
from room_object import RoomObject

class RoomService(BaseService):
    def __init__(self, main, sid):
        BaseService.__init__(self, main, sid)
        self.registCommand('1000', self.createRoomHandler)
        self.registCommand('1001', self.postListHandler)
        self.registCommand('1002', self.enterRoomHandler)
        self.registCommand('1003', self.leaveRoomHandler)

    # 新建房间 cid=0
    def createRoomHandler(self, hid, data):
        respData = {'sid': 1001,
                    'cid': 1000}
        if not data.has_key('uid'):
            logging.warning('create room data has not uid key')
            return

        uid = data['uid']
        user = self.main.findUserByUid(uid)
        if user:
            # room = RoomObject(len(self.main.rooms) + 1, user)
            room = {
                'rid': len(self.main.rooms) + 1,
                'users': [user]
            }
            user['rid'] = room['rid']
            self.main.rooms.append(room)
            respData['result'] = 1
            respData['room'] = room
            respData['code'] = 0
        else:
            respData['result'] = 0
            respData['room'] = None
            respData['code'] = 1100
        respJson = json.dumps(respData)
        self.main.host.send(hid, respJson)
        logging.debug('send s=1001 c=1000 ' + respJson)
        if respData['result'] == 1:
            self.postAllListHandler()

    # 房间列表 cid=1
    def postListHandler(self, hid, data=''):
        try:
            respData = {'sid': 1001,
                        'cid': 1001,
                        'result': 1,
                        'code': 0,
                        'rooms': self.main.rooms}
            respJson = json.dumps(respData)
        except:
            respData = {'sid': 1001,
                        'cid': 1001,
                        'result': 0,
                        'code': 1101,
                        'rooms': []}
            respJson = json.dumps(respData)
        self.main.host.send(hid, respJson)
        logging.debug('send s=1001 c=1001 ' + respJson)

    def postAllListHandler(self):
        for client in self.main.host.clients:
            self.postListHandler(client.hid)


    # 进入房间 cid=2
    def enterRoomHandler(self, hid, data):
        respData = {'sid': 1001,
                    'cid': 1002}
        if not data.has_key('uid') or not data.has_key('rid'):
            logging.warning('enter room data key err')
            return

        uid = data['uid']
        rid = data['rid']
        user = self.main.findUserByUid(uid)
        user['rid'] = rid
        room = self.main.findRoomByRid(rid)
        users = room['users']
        users.append(user)

        if user and room:
            respData['result'] = 1
            respData['code'] = 0
            respData['room'] = room
            respJson = json.dumps(respData)
            for user in room['users']:
                h = self.main.userHid[user['uid']]
                self.main.host.send(h, respJson)
            self.postAllListHandler()

        else:
            respData['result'] = 0
            respData['code'] = 1001
            respData['room'] = None
            respJson = json.dumps(respData)
            self.main.host.send(hid, respJson)

        logging.debug('send s=1001 c=1002 ' + respJson)

    # 退出房间 cid=3
    def leaveRoomHandler(self, hid, data):
        respData = {'sid': 1001,
                    'cid': 1003}
        if not data.has_key('uid') or not data.has_key('rid'):
            logging.warning('leave room data key err')
            return

        uid = data['uid']
        rid = data['rid']
        respData['uid'] = uid
        user = self.main.findUserByUid(uid)
        room = self.main.findRoomByRid(rid)
        user['rid'] = None
        hids = []
        result = 1
        try:
            for user in room['users']:
                hids.append(self.main.userHid[uid])
                if user['uid'] == uid:
                    room['users'].remove(user)
            if not len(room['users']):
                self.main.rooms.remove(room)
                room = None
        except:
            result = 0

        if uid and result:
            respData['result'] = 1
            respData['code'] = 0

        else:
            respData['result'] = 0
            respData['code'] = 1001

        respData['room'] = room

        respJson = json.dumps(respData)
        for h in hids:
            self.main.host.send(h, respJson)
        logging.debug('send s=1001 c=1003 ' + respJson)
        self.postAllListHandler()

