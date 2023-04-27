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
        # ========================================= chat setting
        model = chat_setting.get("model")
        creative = chat_setting.get("creative") / 10
        scenario = chat_setting.get("scenario")
        max_tokens = 4000
        # ========================================== message
        message = [{"role": "system", "content": scenario}]
        message.extend(message_history)
        print(model, message)
        if model in ["gpt-4"]:
            response = openai.ChatCompletion.create(model=model, messages=message, temperature=creative)
        else:
            response = openai.ChatCompletion.create(model=model, messages=message, temperature=creative)
        anser = response.choices[0].message.content
        return anser


    def go_to_chat(self, message):
        pass

if __name__ == '__main__':
    rob = gpt_rob()
    setting = {"model": "gpt-4",
        "creative":10,
        "scenario":"You are a helpful assistant, you call yourself Chatty."}
    anser = rob.openai_requests(setting, [{"role": "user", "content": "hello"}])
    print(anser)