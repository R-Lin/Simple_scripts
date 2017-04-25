## USAGE:
## comm_logging.py
#### add code to the script:
```python
import os
import sys
from common import comm_logging

if __name__ == '__main__':
    # script_path and logger config
    sript_dir, script_name = os.path.split(sys.argv[0])
    if sript_dir:
        os.chdir(sript_dir)
    log_name = script_name.replace('.', '_') + '.log'
    log = comm_logging.log_init(log_name, script_dir=sript_dir)

```