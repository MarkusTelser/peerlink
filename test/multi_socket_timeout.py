import socket
import threading
import sched
import time
import random

def worker(sleep_time, semaphore):
    with semaphore:
        print("started", semaphore._value)
        time.sleep(sleep_time)
        print("finished", semaphore._value)

def max_connections():
    semaphore = threading.BoundedSemaphore(value=5)
    
    for i in range(7):
        sleep_time = random.randint(0, 9)
        threading.Thread(target=worker, args=[sleep_time, semaphore]).start()

def func():
    print("start func")
    time.sleep(3)
    print("finished doing job")
    return "cid..."

  
def wait_for_cid():
    expiry_date = time.time() + 5
    print("expiry date", expiry_date)  
    
    time.sleep(7)
     
    if time.time() > expiry_date:
        func()
        print("cid expired")

def timeouts_retry():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    MAX_TIMEOUT_CYCLES = 8

    n = 0
    while n <= MAX_TIMEOUT_CYCLES:
        try:
            timeout = 15 * (2 ** n)
            sock.settimeout(timeout)
            sock.recv(1024)
        except socket.timeout:
            print(f"received timeout after {timeout}s")
            n += 1

    if n + 1 == MAX_TIMEOUT_CYCLES:
        raise Exception("timed out after 8 retry cycles")
    
wait_for_cid()