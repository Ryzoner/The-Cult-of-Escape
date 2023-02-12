# -*- coding: utf-8 -*-

class SpriteError(Exception):
    '''Can't find sprite file error'''
    __slots__ = ['text']

    def __init__(self):
        super().__init__()
        self.text = 'Не удаётся найти файл спрайта'
