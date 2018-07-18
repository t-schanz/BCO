import os

print("========================================")
if os.environ["test_key"] == "test":
    print("Key = Test")

else:
    print("Key is:")
    foo = os.environ["test_key"]

    if os.environ.has_key("test_key"):
        print("But the key should be there.")
print("========================================")
