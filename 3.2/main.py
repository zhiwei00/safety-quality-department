# -*- coding: utf-8 -*-
import multiprocessing
multiprocessing.freeze_support()


if __name__ == "__main__":
    from src.application import Application

    Application()

