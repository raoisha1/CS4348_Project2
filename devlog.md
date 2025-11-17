# Devlog

## 2025-11-16 

setting up the project folder and initializing the git repository.

### What I know so far
- using Python threads and semaphores.
- simulates tellers, customers, shared resources (manager, safe, door).
- thread_demo.py and example.py

### Plan for the entire project
- Create structure
- Implement teller - customer 
- Add semaphores for: teller availability, customer queue, manager, safe, door  
- Test 
- Expand to 50
- Create README and final

### Goal of this session
- Initialize Git repository
- Create required files
- Commit first entry

## 2025-11-16  [Session 2 Start]
Thoughts so far:
- The basic teller–customer synchronization model is clear.
- need for multiple semaphores: manager, safe, door, teller availability, and handshake semaphores.
- implementing the full `bank.py`.

Plan for this session:
- Implement core teller/customer
- Add semaphores 
- Create shared variables
- follow the provided sample format.
- Run tests