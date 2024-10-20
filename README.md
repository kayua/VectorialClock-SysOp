![SysOP](Resources/ScreenSysOp.png)
# Reliable Communication
This code implements a communication system between two processes using sockets, allowing for the selection of the delivery semantics that best suits the application's context. Three delivery semantics are implemented: at most once, at least once, and exactly once.


## 1. Steps to Install:



### 1. Upgrade and update
   ```bash   
   sudo apt-get update
   sudo apt-get upgrade 
   ```
### 2. Installation of application and internal dependencies
    ```bash
    git clone [https://github.com/kayua/ModelsAudioClassification]
    pip install -r requirements.txt
    ```
   
## 2. Run experiments:


### 1. Run (main.py) Server Mode
`python3 main.py --mode server (arguments)`

### 2. Run (main.py) Sender Mode
`python3 main.py --mode sender (arguments)`

### Input parameters:

    Arguments:
        --mode                  Choose "sender" or "server" Mode (DEFAULT 'server')
        --host                  Host address for the server (DEFAULT 'localhost')
        --port                  Port number for the server (DEFAULT '8100')
        --semantic              Message handling semantic (DEFAULT 'at_most_once')
        --log-level             Logging level for server operations (DEFAULT 'INFO')
        --timeout               Socket timeout for receiving messages in seconds (DEFAULT 'None')
        --max_messages          Maximum number of messages to process before stopping (DEFAULT 'None')

    --------------------------------------------------------------


## 3. Implemented semantics
| **Semantic**   |                                           Description                                            |         Command         |
|:-------------:|:------------------------------------------------------------------------------------------------:|:-----------------------:|
| At Most Once  |                       Ensures that each message will be sent at most once.                       |   --mode at_most_once   |
| At Least Once |     Ensures that the message will be delivered at least once, which may result in duplicates     | --mode at_least_once    |
| Exactly Once  |Ensures the unique and reliable delivery of each message, eliminating both duplicates and losses. |   --mode exactly_once   |
---------------------------------------------------------------------------------------------------------------------------------------

## 4. Requirements:

`pyfiglet 1.0.2`
`logging`