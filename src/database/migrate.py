from .database import User

def migrate_test(db):
    test_new_user = User(user_id = "TEST_NEW", group = "", platform = "YANDEX")
    db.add(test_new_user)
    db.commit()
    
    test_default_user = User(user_id = "TEST_DEFAULT", group = "ИКБО-01-20", platform = "YANDEX")
    db.add(test_default_user)
    db.commit()