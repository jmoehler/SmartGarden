import random
import string
import sys

#set sys path so that i can import from the hub
sys.path.append('../')

from hub.database.database_setup import db_handler 


picture_path = "a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/q/r/s/t/u/v/w/x/y/z"
result = ''.join(random.choices(string.ascii_lowercase, k=50))
recommended_action = ''.join(random.choices(string.ascii_lowercase, k=50))



with db_handler() as db:
    #db.add_picture_analysis(picture_path, result, recommended_action)
    analysis = db.get_all_picture_analysis()


print(analysis)