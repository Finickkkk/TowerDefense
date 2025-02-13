import s_taper
from s_taper.consts import *

scheme = {
    "user_id": INT + KEY,
    "nick": TEXT,
    "hp": INT,
    "damage": INT
}
db = s_taper.Taper("users", "tower.db").create_table(scheme)