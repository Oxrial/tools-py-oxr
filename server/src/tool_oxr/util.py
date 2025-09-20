from concurrent.futures import ThreadPoolExecutor


PORTS = {"SERVER": 39000, "APP": 39001, "DESKTOP": 39002, "API": 39003, "RELOAD": 39004}

executor = ThreadPoolExecutor(max_workers=1)


# 包装接口返回
def wrap_response(data=None, message="success", status=1):
    return {"status": status, "message": message, "data": data}


def build_logger(name):
    import logging

    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    consoleHeader = logging.StreamHandler()
    consoleHeader.setFormatter(formatter)
    logger.addHandler(consoleHeader)
    # file
    fileHandler = logging.FileHandler(f"info.log")
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger
