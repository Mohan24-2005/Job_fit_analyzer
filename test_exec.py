import sys
import traceback

try:
    with open(r'c:\Users\tejas\OneDrive\Desktop\ML project\Backend\utils\security.py', 'r') as f:
        code = f.read()
    exec(code)
    print("Code executed successfully")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    traceback.print_exc()
