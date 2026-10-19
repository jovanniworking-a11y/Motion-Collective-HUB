"""Run the checks: python learn/check.py py01 | ml02 | all"""
import importlib.util, os, sys, glob, traceback
ROOT = os.path.dirname(os.path.abspath(__file__))
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def run_one(d):
    tag = os.path.basename(d).split("_")[0]
    if not os.path.exists(os.path.join(d, "check.py")):
        print(f"{tag}  (no automatic check, see its README)"); return None
    try:
        ex = load(os.path.join(d, "exercise.py"), tag + "_exercise"); load(os.path.join(d, "check.py"), tag + "_check").run(ex)
        print(f"{tag}  PASS"); return True
    except AssertionError as e: print(f"{tag}  not yet: {e}")
    except TypeError as e:
        if "NoneType" in str(e) or "ellipsis" in str(e): print(f"{tag}  not started yet: a function still has `...` instead of code")
        else: print(f"{tag}  error: {type(e).__name__}: {e}"); traceback.print_exc(limit=1)
    except Exception as e: print(f"{tag}  error: {type(e).__name__}: {e}"); traceback.print_exc(limit=1)
    return False
if __name__ == "__main__":
    want = sys.argv[1] if len(sys.argv) > 1 else "all"
    dirs = sorted(glob.glob(os.path.join(ROOT, "*", "*_*")))
    dirs = [d for d in dirs if os.path.isdir(d) and (want == "all" or os.path.basename(d).startswith(want))]
    if not dirs: print("no exercise called", want); sys.exit(1)
    res = [run_one(d) for d in dirs]
    if want == "all": print(f"\n{sum(r is True for r in res)} of {sum(r is not None for r in res)} checked exercises passing")
