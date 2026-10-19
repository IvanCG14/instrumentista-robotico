import sys
if sys.prefix == '/home/iandre/Documents/asist_rbt_instrument/venv':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/iandre/Documents/asist_rbt_instrument/surgical_ws/install/surgical_assistant'
