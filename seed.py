from models.user import User, db

# Create all tables
db.drop_all()
db.create_all()

# Add users
u1 = User.register('Tyler', 'tyler758', 'Tyler', 'Robison', 'tyler@gmail.com', True)
# Tyler is only admin user
u2 = User.register('Bobo758', 'bob758', 'Bob', 'Smith', 'bob@gmail.com', False)
u3 = User.register('Freddy', 'fred758', 'Fred', 'Durst', 'fred@gmail.com', False)
u4 = User.register('ChickenGal', 'chicken758', 'Jane', 'Green', 'chicken@yahoo.com', False)

db.session.add_all([u1, u2, u3, u4])
db.session.commit()