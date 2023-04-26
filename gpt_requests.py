# -*- coding: utf-8 -*-
# Copyright (c) 2023 by WenHuan Yang-Zhang.
# Date: 2023-04
# Ich und google :)

import os
import openai


class gpt_rob:
    openai.api_key = "sk-"
    openai.organization = "org-"


    @staticmethod
    def openai_requests(chat_setting, message_history):
        # Load your API key from an environment variable or secret management service
        # ========================================= chat setting
        model = chat_setting.get("model")
        creative = chat_setting.get("creative")
        scenario = chat_setting.get("scenario")
        # ========================================== message
        message = [{"role": "system", "content": scenario}]
        message.extend(message_history)
        #{"role": "user", "content": "Who won the world series in 2020?"}]
        response = openai.ChatCompletion.create(model=model, messages=message)
        anser = response.choices[0].message.content
        return anser


    def go_to_chat(self, message):
        pass


# a function to convert a json to a csv file
# rob = gpt_rob()
# setting = {"model": "gpt-3.5-turbo",
#     "creative":5,
#     "scenario":"You are a helpful assistant, you call yourself Chatty."}
# anser = rob.openai_requests(setting, {"role": "user", "content": "你好"})
# print(anser)