import random
import string


def generate_random_string(length):
    random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
    return random_string


random_string = generate_random_string(10)
print("Random String:", random_string)
print(random.random())
