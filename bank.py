import threading
import time
import random
import queue

NUM_TELLERS = 3
NUM_CUSTOMERS = 50

door_sem = threading.Semaphore(2)
manager_sem = threading.Semaphore(1)
safe_sem = threading.Semaphore(2)

bank_open_event = threading.Event()

available_tellers_sem = threading.Semaphore(0)
available_tellers_queue = queue.Queue()
available_tellers_lock = threading.Lock()

customer_arrived = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
teller_asks_tx = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
customer_sends_tx = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
transaction_done = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
customer_left = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]

current_customer_id = [None] * NUM_TELLERS
current_transaction_type = [None] * NUM_TELLERS
shared_lock = threading.Lock()

tellers_ready_count = 0
tellers_ready_lock = threading.Lock()

shutting_down = False
shutting_down_lock = threading.Lock()


def ms_sleep(min_ms, max_ms):
    time.sleep(random.uniform(min_ms, max_ms) / 1000.0)


def teller_thread(tid):
    global tellers_ready_count

    with tellers_ready_lock:
        tellers_ready_count += 1
        if tellers_ready_count == NUM_TELLERS:
            bank_open_event.set()

    while True:
        with shutting_down_lock:
            if shutting_down and current_customer_id[tid] is None:
                print(f"Teller {tid} []: leaving for the day")
                return

        print(f"Teller {tid} []: ready to serve")
        print(f"Teller {tid} []: waiting for a customer")

        with available_tellers_lock:
            available_tellers_queue.put(tid)
        available_tellers_sem.release()

        customer_arrived[tid].acquire()

        with shutting_down_lock:
            if shutting_down and current_customer_id[tid] is None:
                print(f"Teller {tid} []: leaving for the day")
                return

        with shared_lock:
            cid = current_customer_id[tid]
            tx = current_transaction_type[tid]

        print(f"Teller {tid} [Customer {cid}]: serving a customer")
        print(f"Teller {tid} [Customer {cid}]: asks for transaction")
        teller_asks_tx[tid].release()

        customer_sends_tx[tid].acquire()

        print(f"Teller {tid} [Customer {cid}]: handling {tx} transaction")

        if tx == "withdrawal":
            print(f"Teller {tid} [Customer {cid}]: going to the manager")
            manager_sem.acquire()
            print(f"Teller {tid} [Customer {cid}]: getting manager's permission")
            ms_sleep(5, 30)
            print(f"Teller {tid} [Customer {cid}]: got manager's permission")
            manager_sem.release()

        print(f"Teller {tid} [Customer {cid}]: going to safe")
        safe_sem.acquire()
        print(f"Teller {tid} [Customer {cid}]: enter safe")
        ms_sleep(10, 50)
        print(f"Teller {tid} [Customer {cid}]: leaving safe")
        safe_sem.release()

        print(f"Teller {tid} [Customer {cid}]: finishes {tx} transaction.")
        print(f"Teller {tid} [Customer {cid}]: wait for customer to leave.")
        transaction_done[tid].release()

        customer_left[tid].acquire()

        with shared_lock:
            current_customer_id[tid] = None
            current_transaction_type[tid] = None


def customer_thread(cid):
    tx = random.choice(["deposit", "withdrawal"])
    print(f"Customer {cid} []: wants to perform a {tx} transaction")

    ms_sleep(0, 100)

    bank_open_event.wait()

    print(f"Customer {cid} []: going to bank.")
    door_sem.acquire()
    print(f"Customer {cid} []: entering bank.")
    print(f"Customer {cid} []: getting in line.")

    print(f"Customer {cid} []: selecting a teller.")
    available_tellers_sem.acquire()
    with available_tellers_lock:
        tid = available_tellers_queue.get()

    print(f"Customer {cid} [Teller {tid}]: selects teller")
    print(f"Customer {cid} [Teller {tid}] introduces itself")

    with shared_lock:
        current_customer_id[tid] = cid
        current_transaction_type[tid] = tx

    customer_arrived[tid].release()

    teller_asks_tx[tid].acquire()
    print(f"Customer {cid} [Teller {tid}]: asks for {tx} transaction")

    customer_sends_tx[tid].release()

    transaction_done[tid].acquire()
    print(f"Customer {cid} [Teller {tid}]: leaves teller")

    print(f"Customer {cid} []: goes to door")
    print(f"Customer {cid} []: leaves the bank")
    door_sem.release()
    customer_left[tid].release()


def main():
    global shutting_down

    random.seed()

    tellers = []
    for tid in range(NUM_TELLERS):
        t = threading.Thread(target=teller_thread, args=(tid,))
        t.start()
        tellers.append(t)

    customers = []
    for cid in range(NUM_CUSTOMERS):
        c = threading.Thread(target=customer_thread, args=(cid,))
        c.start()
        customers.append(c)

    for c in customers:
        c.join()

    with shutting_down_lock:
        shutting_down = True

    for tid in range(NUM_TELLERS):
        if current_customer_id[tid] is None:
            customer_arrived[tid].release()

    for t in tellers:
        t.join()

    print("The bank closes for the day.")


if __name__ == "__main__":
    main()