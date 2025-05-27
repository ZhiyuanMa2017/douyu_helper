# encoding:utf-8
from common.dy_glows import *
from common.login_check import *
from common.config import conf
from common.dy_badge import *
from common.logger import logger
from common.dy_glows import glow_donate
import math
from common.get_secrets import get_secrets
from common.send_message import send_message, bank_send, mail_send


def run():
    logger.info("------登录检查开始------")
    login_res = is_login()
    logger.info("------登录检查结束------")
    mode = int(conf.get_conf("Modechoose")['givemode'])
    if login_res:
        get_glow()
        try:
            glow_nums = get_own()
            assert glow_nums != 0
            if mode == 1:
                logger.info("当前选择模式为:自选模式")
                nums = conf.get_conf_list('selfMode', 'giftCount')
                room_list = conf.get_conf_list('selfMode', 'roomId')
                logger.info("------开始捐赠荧光棒------")
                print_sentence = {}
                for i in range(len(nums)):
                    print_sentence[room_list[i]] = glow_donate(nums[i], room_list[i])
                logger.info("------荧光棒捐赠结束------")
                get_need_exp(print_sentence)
            elif mode == 0:
                logger.info("当前选择模式为:平均分配模式")
                room_list = get_room_list()
                every_give = math.ceil(glow_nums / len(room_list))
                left = int(glow_nums) - int(every_give) * (len(room_list) - 1)
                logger.info("------开始捐赠荧光棒------")
                print_sentence = {}
                for room in room_list:
                    if room == room_list[-1]:
                        print_sentence[room] = glow_donate(left, room)
                    else:
                        print_sentence[room] = glow_donate(every_give, room)
                logger.info("------荧光棒捐赠结束------")
                get_need_exp(print_sentence)
            elif mode == 2:
                logger.info("当前选择模式为:选择+平均模式")
                # 获取配置的选择房间
                selected_room_list = conf.get_conf_list('selectAverageMode', 'roomId')
                
                logger.info("------开始捐赠荧光棒------")
                print_sentence = {}
                remaining_glows = glow_nums
                
                # 首先给选择的房间每个分配1个荧光棒
                logger.info("给选择的房间各分配1个荧光棒:")
                for room in selected_room_list:
                    if remaining_glows >= 1:
                        print_sentence[room] = glow_donate(1, room)
                        remaining_glows -= 1
                    else:
                        logger.warning("荧光棒不足，无法给房间%s分配" % room)
                        break
                
                # 获取所有房间列表并排除已分配的房间
                all_room_list = get_room_list()
                remaining_room_list = [room for room in all_room_list if room not in selected_room_list]
                
                # 如果还有剩余荧光棒且还有未分配的房间，则平均分配
                if remaining_glows > 0 and len(remaining_room_list) > 0:
                    logger.info("剩余荧光棒平均分配给其他房间:")
                    every_give = math.ceil(remaining_glows / len(remaining_room_list))
                    left = int(remaining_glows) - int(every_give) * (len(remaining_room_list) - 1)
                    
                    for room in remaining_room_list:
                        if room == remaining_room_list[-1]:
                            print_sentence[room] = glow_donate(left, room)
                        else:
                            print_sentence[room] = glow_donate(every_give, room)
                elif remaining_glows > 0:
                    logger.info("所有房间都已在选择列表中，剩余%d个荧光棒无法分配" % remaining_glows)
                elif len(remaining_room_list) == 0:
                    logger.info("所有房间都已在选择列表中，无其他房间可分配")
                
                logger.info("------荧光棒捐赠结束------")
                get_need_exp(print_sentence)
            else:
                logger.warning("配置错误,没有这种选项,请修改配置并重新执行")
                bank_send(False, "配置错误,没有这种选项,请修改配置并重新执行")
        except Exception as e:
            logger.warning("背包中没有荧光棒,无法执行赠送,任务即将结束")
            bank_send(False, "背包中没有荧光棒,无法执行赠送,任务即将结束")
            logger.debug(e)
    else:
        logger.warning("未登录状态无法进行后续操作,任务已结束")
        bank_send(False, "未登录状态无法进行后续操作,任务已结束")
    try:
        server_key = get_secrets("SERVERPUSHKEY")
        send_message(server_key)
    except Exception as e:
        logger.info("当前未配置Server酱推送，任务结束")
        logger.debug(e)


if __name__ == '__main__':
    run()
