import sys
sys.path.insert(0, r'c:\Users\tejas\OneDrive\Desktop\ML project\Backend')

try:
    import utils.security as sec
    print("Module imported successfully")
    print(dir(sec))
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
