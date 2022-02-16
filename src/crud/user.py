from src.database.database import User, Session


async def create_user(user, db: Session):

    if db.query(User).filter(User.user_id == user['user_id']).first() == None:
        new_user = User(user_id = user['user_id'], group = user['group'], platform = user['platform'])
        db.add(new_user)
        db.commit()
        return True
    else:
        return False

async def update_user(user, db: Session):
    dbuser = db.query(User).filter(User.user_id == user['user_id']).first()
    if dbuser is not None:
        dbuser.group = user['group']
        db.commit()
        return True
    else:
       return False

async def get_user(user_id: str, db: Session):
    return db.query(User).filter(User.user_id == user_id).first()


async def delete_user(user_id: str, db: Session):
    pass

async def get_users(db: Session):
    return db.query(User).all()
