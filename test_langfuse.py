"""
One-off script to test the Langfuse connection directly, independent of
the FastAPI app — isolates whether the problem is credentials/network,
or something about how traces are triggered in the app itself.

Run from project root: python test_langfuse.py
"""

from dotenv import load_dotenv
load_dotenv()

from langfuse import Langfuse

langfuse = Langfuse()

# Built-in connectivity + credential check
ok = langfuse.auth_check()
print(f"Auth check passed: {ok}")

# Manually create and immediately flush one trace/span
with langfuse.start_as_current_observation(as_type="span", name="manual-test-trace") as span:
    span.update(input="test input", output="test output")

langfuse.flush()  # force-send immediately, don't wait for background batching
print("Flushed — check the Langfuse dashboard now.")