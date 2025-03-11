# from sqlalchemy import create_engine, select
# from sqlalchemy.orm import sessionmaker


# # Функция для получения информации о базе данных от пользователя
# def get_database_config():
#     db_user = input("Введите имя пользователя базы данных: ")
#     db_password = input("Введите пароль базы данных: ")
#     db_host = input("Введите хост базы данных (например, localhost): ")
#     db_port = input("Введите порт базы данных (например, 5432): ")
#     db_name = input("Введите имя базы данных: ")
#     return db_user, db_password, db_host, db_port, db_name


# # Получаем параметры подключения к базе данных
# db_user, db_password, db_host, db_port, db_name = get_database_config()

# # Создание подключения к базе данных
# DATABASE_URL = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
# engine = create_engine(DATABASE_URL)

# # Создание сессии
# Session = sessionmaker(bind=engine)
# session = Session()

# # Получение имени или идентификатора издателя от пользователя
# publisher_input = input("Введите имя или идентификатор издателя: ")

# # Проверка, является ли входное значение числом (идентификатором)
# if publisher_input.isdigit():
#     publisher_id = int(publisher_input)
#     publisher = session.query(Publisher).filter(Publisher.id == publisher_id).first()
# else:
#     publisher_name = publisher_input
#     publisher = session.query(Publisher).filter(Publisher.name.ilike(f"%{publisher_name}%")).first()

# # Если издатель найден
# if publisher:
#     print(f"Издатель: {publisher.name} (ID: {publisher.id})")

#     # Получение магазинов, продающих книги этого издателя
#     results = session.query(Shop).join(Stock).join(Book).filter(Book.id_publisher == publisher.id).all()

#     if results:
#         print("Магазины, продающие книги этого издателя:")
#         for shop in results:
#             print(f"- {shop.name} (ID: {shop.id})")
#     else:
#         print("Нет магазинов, продающих книги этого издателя.")
# else:
#     print("Издатель не найден.")

# # Закрытие сессии
# session.close()

import sqlalchemy
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

# Определение модели Publisher
class Publisher(Base):
    __tablename__ = 'publishers'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=100), unique=True)

    # Связь с книгами
    books = relationship("Book", back_populates="publisher")

# Определение модели Shop
class Shop(Base):
    __tablename__ = 'shops'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=100), unique=True)

    # Связь со складами
    stocks = relationship("Stock", back_populates="shop")

# Определение модели Book
class Book(Base):
    __tablename__ = 'books'

    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String(length=200), nullable=False)
    id_publisher = sq.Column(sq.Integer, sq.ForeignKey('publishers.id'), nullable=False)

    # Связь с издателем
    publisher = relationship("Publisher", back_populates="books")
    # Связь со складами
    stocks = relationship("Stock", back_populates="book")

# Определение модели Stock
class Stock(Base):
    __tablename__ = 'stocks'

    id = sq.Column(sq.Integer, primary_key=True)
    id_shop = sq.Column(sq.Integer, sq.ForeignKey('shops.id'), nullable=False)
    id_book = sq.Column(sq.Integer, sq.ForeignKey('books.id'), nullable=False)

    # Связь с магазином и книгой
    shop = relationship("Shop", back_populates="stocks")
    book = relationship("Book", back_populates="stocks")

def create_tables(engine):
    Base.metadata.create_all(engine)

# Параметры подключения
DSN = "postgresql://postgres:aeg19802402@localhost:5432/bookshop"
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()

# Пример создания объектов
publisher1 = Publisher(name="Издательство A")
book1 = Book(title="Книга 1", publisher=publisher1)
shop1 = Shop(name="Магазин 1")
stock1 = Stock(shop=shop1, book=book1)

# Добавление объектов в сессию
session.add(publisher1)
session.add(book1)
session.add(shop1)
session.add(stock1)
session.commit()  # Фиксируем изменения

# Запросы
q = session.query(Publisher).join(Book).filter(Book.title == "Книга 1")
print("Издатели, которые выпустили 'Книга 1':")
for publisher in q.all():
    print(publisher.id, publisher.name)

# Обновление объектов
session.query(Publisher).filter(Publisher.name == "Издательство A").update({"name": "Новое Издательство A"})
session.commit()  # Фиксируем изменения

# Удаление объектов
session.query(Stock).filter(Stock.id_book == book1.id).delete()
session.commit()  # Фиксируем изменения

# Закрытие сессии
session.close()

